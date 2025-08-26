from collections import deque
import threading
import pygame
import time
import atexit

ONLINE = pygame.event.custom_type()
OFFLINE = pygame.event.custom_type()

import serial
import serial.tools.list_ports

state = 'no'
serial_conn = None
output_queue = deque()
output_queue_lock = threading.Lock()
running = True
aware_timer = None 

ACK = b'ACK\xff\xff\xff'

def init():
    """初始化模块"""
    send_thread = threading.Thread(target=link_thread_func, daemon=True)
    send_thread.start()
    
    atexit.register(cleanup)

def link_thread_func():
    """通信线程"""
    global state, serial_conn
    
    while running:
        try:
            if state != 'success' or serial_conn is None or not serial_conn.is_open:
                time.sleep(0.1)
                continue
            if output_queue:
                with output_queue_lock:
                    item_type, data, callback = output_queue[0]
                try:
                    debug = data == "DebugMeasure"
                    data = data.encode('utf-8')
                    # print(f'Sent: {item_type}, {data}, {callback}')
                    serial_conn.write(data + b'\xff\xff\xff')
                    if item_type == 'w':  # 写操作
                        response = serial_conn.read(1)
                        if response == b'\x88':
                            with output_queue_lock:
                                output_queue.popleft()
                        else:
                            raise Exception(f'写确认失败. 应当收到 "0x88"，实际收到 "{response}"')
                    elif item_type == 'r':  # 读操作
                        response = read_datapack(debug)
                        # print(f'Received: {response}')
                        with output_queue_lock:
                            output_queue.popleft()
                        if callback:
                            try:
                                callback(response)
                            except Exception as e:
                                import traceback
                                traceback.print_exc()
                                print(f"({item_type}, {data}, {callback})回调函数错误: {e}")
                except Exception as e:
                    print(f"通信错误: {e}")
                    handle_disconnection()
            time.sleep(0.01)
        except Exception as e:
            print(f"通信线程错误: {e}")
            if running:
                handle_disconnection()

def read_datapack(debug=False):
    """
    读取数据包

    Returns:
        data (str): 数据包内容
    """
    if serial_conn is None:
        raise Exception("通信端口不存在")

    if debug:
        byte = serial_conn.read(768+3)
        if len(byte) < 768+3:
            raise Exception("读取数据包超时")
        return byte[:-3]
    else:
        data = []
        ff_count = 0

        while running:
            byte = serial_conn.read(1)
            if not byte:
                raise Exception("读取数据包超时")

            if byte == b'\xff':
                ff_count += 1
                if ff_count == 3:
                    while data and data[-1] == b'\xff':
                        data.pop()
                    return b''.join(data)
            elif ff_count > 0:
                ff_count = 0
                data.clear()
            else:
                data.append(byte)
    raise Exception("读取被中断")

def send_write_data(data):
    """
    发送写数据

    Args:
        data (str): 要发送的数据
    """
    with output_queue_lock:
        output_queue.append(('w', data, None))

def send_read_data(data, callback=None):
    """
    发送读数据

    Args:
        data (str): 要发送的数据
        callback (function): 读取响应的回调函数
    """
    with output_queue_lock:
        output_queue.append(('r', data, callback))

def handle_disconnection():
    """处理断开连接"""
    global state, serial_conn
    if state == 'success':
        print("连接断开")
        state = 'no'
        if serial_conn and serial_conn.is_open:
            try:
                serial_conn.close()
            except:
                pass
        serial_conn = None
        pygame.event.post(pygame.event.Event(OFFLINE))
        with output_queue_lock:
            output_queue.clear()

def link_aware():
    """连接感知"""
    global aware_timer
    if not running:
        return
    if state != 'success' or serial_conn is None:
        aware_timer = threading.Timer(3, link_aware)
        aware_timer.daemon = True
        aware_timer.start()
        return

    def aware_callback(response):
        if response != b'ACK':
            print("握手应答内容不正确")
            handle_disconnection()

    send_read_data('ACK', aware_callback)
    aware_timer = threading.Timer(3, link_aware)
    aware_timer.daemon = True
    aware_timer.start()

def auto_connect():
    """自动连接"""
    global state, serial_conn, aware_timer
    state = 'search'
    ports = serial.tools.list_ports.comports()
    for p, d, _ in sorted(ports):
        if '蓝牙' in d:
            continue
        print(f"尝试连接端口：{p} - {d}")
        try:
            ser = serial.Serial(
                port=p,
                baudrate=115200,
                bytesize=8,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=2,
                write_timeout=2,
            )
            if ser.is_open:
                ser.write(ACK)
                response = ser.read(len(ACK))
                if response == ACK:
                    print(f"成功连接到：{p}")
                    state = 'success'
                    serial_conn = ser
                    pygame.event.post(pygame.event.Event(ONLINE))
                    if aware_timer:
                        aware_timer.cancel()
                    link_aware()
                    return
        except Exception as e:
            print(f"连接失败：{p}, 错误: {e}")
    state = 'no'
    return None

def cleanup():
    """清理函数，用于程序退出时释放资源"""
    global running, aware_timer

    with output_queue_lock:
        running = False
        if aware_timer:
            aware_timer.cancel()
        if serial_conn and serial_conn.is_open:
            try:
                serial_conn.close()
            except:
                import traceback
                traceback.print_exc()
