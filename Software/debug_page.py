import time
import pygame
import pygame.freetype

import fantas
from fantas import uimanager as u

import link

import colors
import iconmap
import textstyle
import buttonstyle

import page_button

PADDING = 40

class DebugPageButton(page_button.PageButton):
    def __init__(self, title_bar, **anchor):
        super().__init__(title_bar, '调试', iconmap.DEBUG, **anchor)
        self.usable_rect = title_bar.get_usable_rect()
        self.wave_boxes = [
            WaveBox((self.usable_rect.w - 3 * PADDING, (self.usable_rect.h - 4 * PADDING) // 3), 0, self, topleft=(self.usable_rect.left + PADDING * 2, self.usable_rect.top + PADDING)),
            WaveBox((self.usable_rect.w - 3 * PADDING, (self.usable_rect.h - 4 * PADDING) // 3), 1, self, midleft=(self.usable_rect.left + PADDING * 2, self.usable_rect.centery)),
            WaveBox((self.usable_rect.w - 3 * PADDING, (self.usable_rect.h - 4 * PADDING) // 3), 2, self, bottomleft=(self.usable_rect.left + PADDING * 2, self.usable_rect.bottom - PADDING)),
        ]
        self.running = True
    
    def start_link(self):
        if link.state == 'success':
            self.running = True
            link.send_read_data('DebugMeasure', self.draw_curve)

    def show_page(self):
        super().show_page()
        self.auto_adjust_size()
        for i in range(len(self.wave_boxes)):
            self.wave_boxes[i].join(u.root)
            self.wave_boxes[i].appear(i * 3)
        self.start_link()

    def hide_page(self):
        super().hide_page()
        for i in range(len(self.wave_boxes)):
            self.wave_boxes[i].disappear(i * 3)

    def auto_adjust_size(self):
        if not self.is_banned:
            return
        usable_rect = self.title_bar.get_usable_rect()
        if self.usable_rect == usable_rect:
            return
        self.usable_rect = usable_rect
        r, c = calc_rc_num((usable_rect.w - 3 * PADDING, (usable_rect.h - 4 * PADDING) // 3 - 24), WaveBox.MAX_BLOCK_SIZE)
        for i in self.wave_boxes:
            i.set_size((usable_rect.w - 3 * PADDING, (usable_rect.h - 4 * PADDING) // 3))
            i.rect.left = usable_rect.left + PADDING * 2
            i.draw_lines(r, c)
        self.wave_boxes[0].rect.top = usable_rect.top + PADDING
        self.wave_boxes[1].rect.centery = usable_rect.centery
        self.wave_boxes[2].rect.bottom = usable_rect.bottom - PADDING
        for i in self.wave_boxes:
            i.auto_adjust_size()
            if link.state != 'success':
                i.wave.draw()

    def draw_curve(self, byte_data):
        adc_values = []
        # print(len(byte_data))
        if (len(byte_data) == 768):
            for i in range(0, len(byte_data), 2):
                value = byte_data[i] | (byte_data[i+1] << 8)
                adc_values.append(value)
            self.wave_boxes[0].wave.points = adc_values[0::3]
            self.wave_boxes[1].wave.points = adc_values[1::3]
            self.wave_boxes[2].wave.points = adc_values[2::3]
            for i in self.wave_boxes:
                i.wave.draw()
        if self.running and link.state == 'success':
            time.sleep(0.2)
            link.send_read_data('DebugMeasure', self.draw_curve)
        else:
            self.running = False

class WaveBox(fantas.Label):
    MAX_BLOCK_SIZE = 100
    LINE_COLOR = colors.LIGHTBLUE2
    REBOUND_CURVE = fantas.get_rebound_curve(1.2, 0.5)

    def __init__(self, size, ID, page_button, **anchor):
        super().__init__(size, bd=2, bg=colors.WHITE, sc=colors.DARKBLUE, radius={'border_radius': 12}, **anchor)
        self.id = ID
        self.id_text = fantas.Text(f'通道 {ID + 1}', u.fonts['maplemono'], {'size': self.rect.h / 2, 'fgcolor': colors.LIGHTBLUE1, 'style': pygame.freetype.STYLE_STRONG | pygame.freetype.STYLE_OBLIQUE}, center=(self.rect.w / 2, self.rect.h / 2))
        self.id_text.join(self)
        # self.page_button = page_button
        self.scale_texts = (
            WaveScaleText("3.3V", self, left=self.rect.left + 12),
            WaveScaleText("1.65", self, left=self.rect.left + 12),
            WaveScaleText("0", self, left=self.rect.left + 12),
        )
        self.row_lines = []
        self.col_lines = []
        r, c = calc_rc_num((self.rect.w, self.rect.h - 24), WaveBox.MAX_BLOCK_SIZE)
        self.draw_lines(r, c)
        self.trigger = fantas.Trigger()
        self.alpha = 0
        self.rect.top -= PADDING

        self.alpha_kf = fantas.UiKeyFrame(self, 'alpha', 255, 8, fantas.harmonic_curve)
        self.top_kf = fantas.RectKeyFrame(self, 'top', self.rect.top, 12, WaveBox.REBOUND_CURVE)

        self.wave = Wave(self)

    def auto_adjust_size(self):
        self.top_kf.value = self.rect.top
        self.id_text.style['size'] = self.rect.h / 2
        self.id_text.rect.center = (self.rect.w / 2, self.rect.h / 2)
        self.id_text.update_img()

    def draw_lines(self, rows, cols):
        if rows > len(self.row_lines):
            for _ in range(rows - len(self.row_lines)):
                l = fantas.Label((self.rect.w - self.bd * 2, 1), bg=WaveBox.LINE_COLOR, left=self.bd)
                l.join_to(self, 1)
                l.anchor = 'left'
                self.row_lines.append(l)
        elif rows < len(self.row_lines):
            for _ in range(len(self.row_lines) - rows):
                self.row_lines[-1].leave()
                self.row_lines.pop()
        if cols > len(self.col_lines):
            for _ in range(cols - len(self.col_lines)):
                l = fantas.Label((1, self.rect.h - 24), bg=WaveBox.LINE_COLOR, top=12)
                l.join_to(self, 1)
                l.anchor = 'top'
                self.col_lines.append(l)
        elif cols < len(self.col_lines):
            for _ in range(len(self.col_lines) - cols):
                self.col_lines[-1].leave()
                self.col_lines.pop()
        for i in range(rows):
            self.row_lines[i].set_size((self.rect.w - self.bd * 2, 1))
            self.row_lines[i].rect.top = 12 + (self.rect.h - 24) * i // (rows - 1)
        self.scale_texts[0].rect.centery = self.rect.top + 12
        self.scale_texts[1].rect.centery = self.rect.centery
        self.scale_texts[2].rect.centery = self.rect.bottom - 12
        for i in range(cols):
            self.col_lines[i].set_size((1, self.rect.h - 24))
            self.col_lines[i].rect.left = self.rect.w * (i + 1) // (cols + 1)
    
    def appear(self, delay):
        if self.trigger.is_launched():
            self.trigger.stop()
        if delay > 0:
            self.trigger.bind_endupwith(self.appear_ani)
            self.trigger.launch(delay)
        else:
            self.appear_ani()
    
    def appear_ani(self):
        self.alpha_kf.value = 255
        self.alpha_kf.launch()
        self.alpha_kf.bind_endupwith(None)
        self.top_kf.value += PADDING
        self.top_kf.curve = WaveBox.REBOUND_CURVE
        self.top_kf.launch()
        for i in self.scale_texts:
            i.appear()

    def disappear(self, delay):
        if self.trigger.is_launched():
            self.trigger.stop()
        if delay > 0:
            self.trigger.bind_endupwith(self.disappear_ani)
            self.trigger.launch(delay)
        else:
            self.disappear_ani()

    def disappear_ani(self):
        self.alpha_kf.value = 0
        self.alpha_kf.launch()
        self.alpha_kf.bind_endupwith(self.leave)
        self.top_kf.value -= PADDING
        self.top_kf.curve = fantas.faster_curve
        self.top_kf.launch()
        for i in self.scale_texts:
            i.disappear()

class WaveScaleText(fantas.Text):
    def __init__(self, text, wave_box, **kwargs):
        super().__init__(text, u.fonts['maplemono'], textstyle.DEBUG_WAVE_SCALE_TEXT, **kwargs)
        self.wave_box = wave_box
        self.anchor = "centery"

        self.alpha = 0
        self.alpha_kf = fantas.UiKeyFrame(self, 'alpha', 255, 8, fantas.harmonic_curve)
        self.pos_kf = fantas.RectKeyFrame(self, 'right', self.wave_box.rect.left - 12, 8, fantas.harmonic_curve)

    def appear(self):
        self.join_to(u.root, 0)
        self.alpha_kf.value = 255
        self.alpha_kf.launch()
        self.alpha_kf.bind_endupwith(None)
        self.rect.left = self.wave_box.rect.left + 12
        self.pos_kf.launch()

    def disappear(self):
        self.alpha_kf.value = 0
        self.alpha_kf.launch()
        self.alpha_kf.bind_endupwith(self.leave)

class Wave(fantas.Ui):
    COLOR = colors.CURVERED

    def __init__(self, wave_box):
        super().__init__(pygame.Surface((1, 1), flags=pygame.SRCALPHA).convert_alpha(), topleft=(0, 0))
        self.anchor = 'topleft'
        self.wave_box = wave_box
        self.join(wave_box)
        self.points = [None] * 128
        self.line = fantas.Label(self.size, bg=colors.BLACK, left=0)
        self.line.anchor = 'left'
        self.line.alpha = 100
        self.line.join(self)
        self.text = fantas.Text("0.00mV", u.fonts['maplemono'], {'fgcolor': colors.WHITE, 'bgcolor': colors.BLACK, 'size': 24})
        self.text.alpha = 144
        self.text.join(self)

    def draw(self):
        self.img = pygame.Surface(self.wave_box.rect.size, flags=pygame.SRCALPHA).convert_alpha()
        self.size = self.origin_size = self.img.get_size()
        if self.points is not None:
            pygame.draw.lines(self.img, Wave.COLOR, False, self.get_points(), 3)
        a = self.get_average()
        text = f'{round(a * 3300 / 4095, 2)}mV'
        if text != self.text.text:
            self.text.text = text
            self.text.update_img()
        if self.size[0] != self.line.size[0]:
            self.line.set_size((self.size[0], 3))
        self.line.rect.centery = self.size[1] - 12 - (self.size[1] - 24) * a / 4095
        self.text.rect.center = self.line.rect.center
        self.mark_update()

    def get_points(self):
        w, h = self.size
        x_start = 12
        x_end = w - 12
        x_step = (x_end - x_start) / (len(self.points) - 1)         
        y_min = 12
        y_max = h - 12
        return [(round(x_start + i * x_step), round(y_max - (value / 4095) * (y_max - y_min))) for i, value in enumerate(self.points)]
    
    def get_average(self):
        window_size = 3
        filtered_points = []
        
        for i in range(len(self.points)):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(self.points), i + window_size // 2 + 1)
            window = self.points[start_idx:end_idx]
            
            filtered_value = sum(window) / len(window)
            filtered_points.append(filtered_value)
        
        return sum(filtered_points) / len(filtered_points)

def calc_rc_num(area_size, max_block_size):
    """
    计算区域内行列数

    Args:
        area_size (tuple(int, int)): 区域大小 (宽, 高)
        max_block_size (int): 最大块大小
    """
    width, height = area_size
    cols = (width + max_block_size - 1) // max_block_size - 1
    rows = (height + max_block_size - 1) // max_block_size + 1
    if (rows % 2) == 0:
        rows += 1
    return (rows, cols)
