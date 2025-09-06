import re
import time
import math

import pygame
import fantas
from fantas import uimanager as u

import link

import colors
import iconmap
import textstyle
import buttonstyle

import page_button
import debug_page

PADDING = 40

class MeasurePageButton(page_button.PageButton):
    def __init__(self, title_bar, **anchor):
        super().__init__(title_bar, '检测', iconmap.MEASURE, **anchor)
        self.usable_rect = title_bar.get_usable_rect()
        self.running = False
        self.boxes = [
            TrackTypeBox(self),
            TrackAngleBox(self),
            TrackDistanceBox(self),
            TrackHeightBox(self),
        ]

    def show_page(self):
        super().show_page()
        self.auto_adjust_size()
        self.start_link()
        for i in self.boxes:
            i.appear()
    
    def hide_page(self):
        super().hide_page()
        for i in self.boxes:
            i.disappear()

    def auto_adjust_size(self):
        if not self.is_banned:
            return
        usable_rect = self.title_bar.get_usable_rect()
        if self.usable_rect == usable_rect:
            return
        self.usable_rect = usable_rect
        for i in self.boxes:
            i.auto_adjust_size()

    def start_link(self):
        if link.state == 'success':
            self.running = True
            link.send_read_data('Measure', self.show_results)

    def show_results(self, byte_data):
        match = re.search(
            r'TrackType:\s*([^,]+),\s*Angle:\s*([\d.]+),\s*Distance:\s*([\d.]+),\s*Height:\s*([\d.]+)',
            byte_data.decode('utf-8')
        )    
        if match:
            track_type = match.group(1)
            angle = float(match.group(2))
            distance = float(match.group(3))
            height = float(match.group(4))
            self.boxes[0].draw_track_type(track_type)
            self.boxes[1].set_angle(angle)
            self.boxes[2].add_data(distance)
            self.boxes[3].add_data(height)

        if self.running and link.state == 'success':
            time.sleep(0.2)
            link.send_read_data('Measure', self.show_results)
        else:
            self.running = False

class MeasureBox(fantas.Label):
    def __init__(self, ID, page_button, **anchor):
        self.ID = ID
        self.appeared = False
        self.page_button = page_button
        usable_rect = page_button.usable_rect
        size = ((usable_rect.w - PADDING * 3) // 2, (usable_rect.h - PADDING * 3) // 2)
        super().__init__(size, bg=colors.WHITE, bd=4, sc=colors.DARKBLUE, radius={'border_radius': 16}, **anchor)

        self.alpha = 0
        self.alpha_kf = fantas.UiKeyFrame(self, 'alpha', 255, 8, fantas.harmonic_curve)
        self.top_kf = fantas.RectKeyFrame(self, 'top', usable_rect.top + self.ID // 2 * (size[1] + PADDING), 16, u.REROUND_CURVE)
        if self.ID > 1:
            self.trigger = fantas.Trigger()

        self.auto_adjust_size()
        self.rect.top -= PADDING

    def auto_adjust_size(self):
        usable_rect = self.page_button.usable_rect
        size = ((usable_rect.w - PADDING * 3) // 2, (usable_rect.h - PADDING * 3) // 2)
        if self.size != size:
            self.set_size(size)
            self.mark_update()
        topleft = (usable_rect.left + PADDING + self.ID % 2 * (size[0] + PADDING), usable_rect.top + PADDING + self.ID // 2 * (size[1] + PADDING))
        if self.rect.topleft != topleft:
            self.rect.topleft = topleft
            self.mark_update()
        if not self.appeared:
            self.rect.top -= PADDING
        self.top_kf.value = self.rect.top

    def appear(self):
        self.appeared = True
        if self.ID > 1:
            self.trigger.bind_endupwith(self.appear_ani)
            self.trigger.launch(3)
        else:
            self.appear_ani()

    def disappear(self):
        self.appeared = False
        if self.ID > 1:
            self.trigger.bind_endupwith(self.disappear_ani)
            self.trigger.launch(3)
        else:
            self.disappear_ani()

    def appear_ani(self):
        self.join(u.root)
        self.alpha_kf.value = 255
        self.alpha_kf.bind_endupwith(None)
        self.alpha_kf.launch()
        self.top_kf.value += PADDING
        self.top_kf.launch()

    def disappear_ani(self):
        self.alpha_kf.value = 0
        self.alpha_kf.bind_endupwith(self.leave)
        self.alpha_kf.launch()
        self.top_kf.value -= PADDING
        self.top_kf.launch()

class TrackTypeBox(MeasureBox):
    def __init__(self, page_button):
        self.title_text = fantas.Text("轨道类型：无", u.fonts['maplemono'], {'size': 24, 'fgcolor': colors.DARKBLUE}, top=20)
        self.track = fantas.Ui(pygame.Surface((512, 512), pygame.SRCALPHA))
        super().__init__(0, page_button)
        self.track.join(self)
        self.title_text.join(self)

    def auto_adjust_size(self):
        super().auto_adjust_size()
        self.title_text.rect.centerx = self.rect.w / 2
        r = pygame.Rect(4, self.title_text.rect.bottom + 20, self.rect.w - 8, self.rect.h - self.title_text.rect.bottom - 36)
        self.track.rect.center = r.center
        if r.w > r.h:
            self.track.size = (r.h, r.h)
        else:
            self.track.size = (r.w, r.w)
        self.track.mark_update()

    def draw_track_type(self, track_type):
        self.track.img.fill(colors.WHITE)
        if track_type == 'None':
            self.title_text.text = "轨道类型：无"
            self.title_text.update_img()
        elif track_type == 'Straight':
            self.title_text.text = "轨道类型：直线"
            self.title_text.update_img()
            self.track.img.fill(colors.LIGHTBLUE2, (192, 0, 128, 512))
            self.track.img.fill(colors.DARKBLUE, (252, 0, 8, 512))
        elif track_type == 'Bend':
            self.title_text.text = "轨道类型：直角转弯"
            self.title_text.update_img()
            self.track.img.fill(colors.LIGHTBLUE2, (0, 0, 512 - 128, 128))
            self.track.img.fill(colors.DARKBLUE, (0, 60, 512 - 128, 8))
            self.track.img.fill(colors.LIGHTBLUE2, (512 - 128, 128, 128, 512 - 128))
            pygame.draw.circle(self.track.img, colors.LIGHTBLUE2, (512 - 128, 128), 128, draw_top_right=True)
            pygame.draw.circle(self.track.img, colors.DARKBLUE, (512 - 128, 128), 128 - 60, 8, draw_top_right=True)
            self.track.img.fill(colors.DARKBLUE, (512 - 128 + 60, 128, 8, 512 - 128))
        elif track_type == 'Arc':
            self.title_text.text = "轨道类型：圆弧"
            self.title_text.update_img()
            pygame.draw.circle(self.track.img, colors.LIGHTBLUE2, (0, 512), 512, 128, draw_top_right=True)
            pygame.draw.circle(self.track.img, colors.DARKBLUE, (0, 512), 512 - 60, 8, draw_top_right=True)
        self.track.mark_update()

class TrackAngleBox(MeasureBox):
    def __init__(self, page_button):
        self.title_text = fantas.Text("轨道角度：0°", u.fonts['maplemono'], {'size': 24, 'fgcolor': colors.DARKBLUE}, top=20)
        self.sensor = fantas.Ui(u.images['sensor'])
        self.sensor_angle = 0
        self.SENSOR_RATIO = self.sensor.origin_size[0] / self.sensor.origin_size[1]
        super().__init__(1, page_button)
        self.title_text.join(self)
        self.sensor.join(self)

    def auto_adjust_size(self):
        super().auto_adjust_size()
        self.title_text.rect.centerx = self.rect.w / 2
        self.update_sensor()
    
    def set_angle(self, angle):
        angle = round(angle % 360, 2)
        self.sensor_angle = angle
        self.title_text.text = f"轨道角度：{angle}°"
        self.title_text.update_img()
        self.sensor.angle = angle
        self.update_sensor()
    
    def update_sensor(self):
        r = pygame.Rect(4, self.title_text.rect.bottom + 20, self.rect.w - 8, self.rect.h - self.title_text.rect.bottom - 36)
        self.sensor.rect.center = r.center
        size = rotated_size(self.sensor.origin_size[0], self.sensor.origin_size[1], self.sensor_angle)
        if r.w / r.h > size[0] / size[1]:
            self.sensor.size = original_size(int(r.h * size[0] / size[1]), r.h, self.sensor_angle, self.SENSOR_RATIO)
        else:
            self.sensor.size = original_size(r.w, int(r.w * size[1] / size[0]), self.sensor_angle, self.SENSOR_RATIO)
        self.sensor.mark_update()

def rotated_size(w, h, angle):
    a = math.radians(angle)
    cos_a = math.cos(a)
    sin_a = math.sin(a)
    new_w = abs(w * cos_a) + abs(h * sin_a)
    new_h = abs(w * sin_a) + abs(h * cos_a)

    return int(new_w), int(new_h)

def original_size(rotated_w, rotated_h, angle, ratio):
    theta = math.radians(angle)
    abs_cos = abs(math.cos(theta))
    abs_sin = abs(math.sin(theta))
    h = (rotated_w / (ratio * abs_cos + abs_sin) + rotated_h / (ratio * abs_sin + abs_cos)) / 2

    return int(round(ratio * h)), int(round(h))


class TrackDataWaveBox(MeasureBox):
    def __init__(self, ID, page_button, title_text):
        self.text = title_text
        self.title_text = fantas.Text(title_text, u.fonts['maplemono'], {'size': 24, 'fgcolor': colors.DARKBLUE}, top=20)
        self.row_lines = []
        self.col_lines = []
        self.data_queue = []
        self.wave_surface = None
        super().__init__(ID, page_button)
        self.title_text.join(self)

    def auto_adjust_size(self):
        super().auto_adjust_size()
        self.title_text.rect.centerx = self.rect.w / 2
        rect = pygame.Rect(4, self.title_text.rect.bottom + 20, self.rect.w - 8, self.rect.h - self.title_text.rect.bottom - 36)
        r, c = debug_page.calc_rc_num(rect.size, 60)
        if len(self.row_lines) > r:
            for _ in range(len(self.row_lines) - r):
                self.row_lines[-1].leave()
                self.row_lines.pop()
        elif len(self.row_lines) < r:
            for _ in range(r - len(self.row_lines)):
                l = fantas.Label((self.rect.w - self.bd * 2, 1), bg=debug_page.WaveBox.LINE_COLOR, left=self.bd)
                l.join_to(self, 0)
                l.anchor = 'left'
                self.row_lines.append(l)
        if len(self.col_lines) > c:
            for _ in range(len(self.col_lines) - c):
                self.col_lines[-1].leave()
                self.col_lines.pop()
        elif len(self.col_lines) < c:
            for _ in range(c - len(self.col_lines)):
                l = fantas.Label((1, self.rect.h - 24), bg=debug_page.WaveBox.LINE_COLOR, top=rect.top)
                l.join_to(self, 0)
                l.anchor = 'top'
                self.col_lines.append(l)
        for i in range(r):
            self.row_lines[i].set_size((rect.w, 1))
            self.row_lines[i].rect.top = rect.top + rect.h * i // (r - 1)
        for i in range(c):
            self.col_lines[i].set_size((1, rect.h))
            self.col_lines[i].rect.left = rect.left + rect.w * (i + 1) // (c + 1)
        self.draw_curve(rect)

    def add_data(self, data):
        self.title_text.text = f"{self.text}：{data} mm"
        self.title_text.update_img()
        self.data_queue.append(data)
        if len(self.data_queue) > 128:
            self.data_queue.pop(0)
        self.draw_curve()
    
    def draw_curve(self, rect=None):
        if len(self.data_queue) < 2:
            return
        if rect is None:
            rect = pygame.Rect(4, self.title_text.rect.bottom + 20, self.rect.w - 8, self.rect.h - self.title_text.rect.bottom - 36)
        if self.wave_surface is None:
            self.wave_surface = fantas.Ui(pygame.Surface(rect.size, pygame.SRCALPHA), topleft=rect.topleft)
            self.wave_surface.join(self)
        else:
            self.wave_surface.img = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.lines(self.wave_surface.img, colors.CURVERED, False, self.get_points(rect), 3)
        self.wave_surface.mark_update()

    def get_points(self, rect, max_data=None, min_data=None):
        if max_data is None:
            max_data = max(self.data_queue)
        if min_data is None:
            min_data = min(self.data_queue)
        return [(round(2 + (rect.w - 4) * i / 127), round(2 + (rect.h - 4) * (1 - (self.data_queue[i] - min_data) / (max_data - min_data)))) for i in range(len(self.data_queue))]

class TrackDistanceBox(TrackDataWaveBox):
    def __init__(self, page_button):
        super().__init__(2, page_button, "轨道中心偏移")

    def auto_adjust_size(self):
        super().auto_adjust_size()
        center_index = (len(self.row_lines) - 1) // 2
        self.row_lines[center_index].set_size((self.row_lines[center_index].rect.w, 5))
        self.row_lines[center_index].rect.top -= 2
    
    def get_points(self, rect):
        max_data = max(self.data_queue)
        min_data = min(self.data_queue)
        if (abs(max_data) > abs(min_data)):
            min_data = -max_data
        else:
            max_data = -min_data
        if max_data == min_data:
            return [(round(2 + (rect.w - 4) * i / 127), rect.h // 2) for i in range(len(self.data_queue))]
        else:
            return [(round(2 + (rect.w - 4) * i / 127), round(2 + (rect.h - 4) * (1 - (self.data_queue[i] - min_data) / (max_data - min_data)))) for i in range(len(self.data_queue))]
    
class TrackHeightBox(TrackDataWaveBox):
    def __init__(self, page_button):
        super().__init__(3, page_button, "轨道中心高度")

    def auto_adjust_size(self):
        super().auto_adjust_size()
        self.row_lines[-1].set_size((self.row_lines[-1].rect.w, 5))
        self.row_lines[-1].rect.top -= 2
    
    def get_points(self, rect):
        min_data=0
        max_data = max(self.data_queue)
        if min_data == max_data:
            return [(round(2 + (rect.w - 4) * i / 127), rect.h) for i in range(len(self.data_queue))]
        else:
            return [(round(2 + (rect.w - 4) * i / 127), round(2 + (rect.h - 4) * (1 - (self.data_queue[i] - min_data) / (max_data - min_data)))) for i in range(len(self.data_queue))]

