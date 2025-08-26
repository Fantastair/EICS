import fantas
from fantas import uimanager as u

import colors
import iconmap

import page_button

PADDING = 40

class AboutPageButton(page_button.PageButton):
    def __init__(self, title_bar, **anchor):
        super().__init__(title_bar, '关于', iconmap.ABOUT, **anchor)
        self.usable_rect = title_bar.get_usable_rect()
        self.element_list = []    # [(Ui, top_kf, alpha_kf, delay, Trigger/None), ...]
        ts= {'size': 48, 'fgcolor': colors.DARKBLUE}
        e = fantas.Text("电磁轨道检测装置 - 上位机", u.fonts['maplemono'], ts, midleft=(self.usable_rect.left + PADDING, self.usable_rect.top + PADDING * 1.5))
        self.add_element(fantas.get_shadow(e, 4, color=colors.GRAY, offset=(4, 4)), 0)
        self.add_element(e, 0)
        e = fantas.Text("基于感应线圈传感器", u.fonts['maplemono'], ts, midleft=(self.usable_rect.left + PADDING, self.usable_rect.top + PADDING * 3.25))
        ts['size'] = 26
        self.add_element(fantas.get_shadow(e, 4, color=colors.GRAY, offset=(4, 4)), 0)
        self.add_element(e, 0)
        self.split_line = fantas.Label((self.usable_rect.w - PADDING * 2, 16), bg=colors.DARKBLUE, radius={'border_radius': 8}, midleft=(self.usable_rect.left + PADDING, self.usable_rect.top + PADDING * 4.75))
        self.split_line.anchor = 'topleft'
        self.add_element(self.split_line, 2)
        e = fantas.VectorImage("./assets/logo/Python.svg", (64, 64), midleft=(self.usable_rect.left + PADDING + 16, self.usable_rect.top + PADDING * 6.5))
        self.add_element(fantas.get_shadow(e, 4, color=colors.GRAY, offset=(4, 4)), 4)
        self.add_element(e, 4)
        ts['size'] = 28
        e = fantas.Text("Python 3.12.10", u.fonts['maplemono'], ts, midleft=(e.rect.right + PADDING + 16, self.usable_rect.top + PADDING * 6.5))
        self.add_element(fantas.get_shadow(e, 4, color=colors.GRAY, offset=(4, 4)), 4)
        self.add_element(e, 4)
        e = fantas.Text("Pygame-ce 2.5.5", u.fonts['maplemono'], ts, midleft=(e.rect.left, self.usable_rect.top + PADDING * 8.3))
        self.add_element(fantas.get_shadow(e, 4, color=colors.GRAY, offset=(4, 4)), 6)
        self.add_element(e, 6)
        e = fantas.Text("pyserial 3.5", u.fonts['maplemono'], ts, midleft=(e.rect.left, self.usable_rect.top + PADDING * 10))
        self.add_element(fantas.get_shadow(e, 4, color=colors.GRAY, offset=(4, 4)), 8)
        self.add_element(e, 8)
        e = fantas.VectorImage("./assets/logo/pygame_ce.svg", (128, 128), midleft=(self.usable_rect.left + PADDING - 15, self.usable_rect.top + PADDING * 8.3))
        self.add_element(fantas.get_shadow(e, 4, color=colors.GRAY, offset=(4, 4)), 6)
        self.add_element(e, 6)
        e = fantas.Text("项目开源链接：", u.fonts['maplemono'], ts, midleft=(self.usable_rect.left + PADDING, self.usable_rect.top + PADDING * 11.5))
        self.add_element(fantas.get_shadow(e, 4, color=colors.GRAY, offset=(4, 4)), 8)
        self.add_element(e, 8)
        e = fantas.WebURL("GitHub - EICS", "https://github.com/Fantastair/EICS", u.fonts['maplemono'], ts, midleft=(e.rect.right + 8, self.usable_rect.top + PADDING * 11.5))
        self.add_element(fantas.get_shadow(e, 4, color=colors.GRAY, offset=(4, 4)), 8)
        self.add_element(e, 8)
        e = fantas.Text("程序发布页：", u.fonts['maplemono'], ts, midleft=(self.usable_rect.left + PADDING, self.usable_rect.top + PADDING * 12.8))
        self.add_element(fantas.get_shadow(e, 4, color=colors.GRAY, offset=(4, 4)), 8)
        self.add_element(e, 10)
        e = fantas.WebURL("GitHub Releases", "https://github.com/Fantastair/EICS/releases", u.fonts['maplemono'], ts, midleft=(e.rect.right + 8, self.usable_rect.top + PADDING * 12.8))
        self.add_element(fantas.get_shadow(e, 4, color=colors.GRAY, offset=(4, 4)), 10)
        self.add_element(e, 10)

    def show_page(self):
        super().show_page()
        self.auto_adjust_size()
        for i in self.element_list:
            element, _, _, delay, trigger = i
            element.join(u.root)
            if trigger is not None and trigger.is_launched():
                trigger.stop()
            if delay > 0:
                trigger.bind_endupwith(self.element_appear, i)
                trigger.launch(delay)
            else:
                self.element_appear(i)

    def hide_page(self):
        super().hide_page()
        for i in self.element_list:
            _, _, _, delay, trigger = i
            if trigger is not None and trigger.is_launched():
                trigger.stop()
            if delay > 0:
                trigger.bind_endupwith(self.element_disappear, i)
                trigger.launch(delay)
            else:
                self.element_disappear(i)

    def auto_adjust_size(self):
        if not self.is_banned:
            return
        usable_rect = self.title_bar.get_usable_rect()
        if self.usable_rect == usable_rect:
            return
        self.usable_rect = usable_rect
        self.split_line.set_size((self.usable_rect.w - PADDING * 2, 16))

    def add_element(self, element, delay):
        element.rect.top -= PADDING
        element.alpha = 0
        top_kf = fantas.RectKeyFrame(element, 'top', element.rect.top, 12, u.REROUND_CURVE)
        alpha_kf = fantas.UiKeyFrame(element, 'alpha', 255, 8, fantas.harmonic_curve)
        self.element_list.append((element, top_kf, alpha_kf, delay, None if delay == 0 else fantas.Trigger()))
    
    def element_appear(self, element):
        _, top_kf, alpha_kf, _, _ = element
        alpha_kf.value = 255
        alpha_kf.launch()
        alpha_kf.bind_endupwith(None)
        top_kf.value += PADDING
        top_kf.curve = u.REROUND_CURVE
        top_kf.launch()

    def element_disappear(self, element):
        element, top_kf, alpha_kf, _, _ = element
        alpha_kf.value = 0
        alpha_kf.bind_endupwith(element.leave)
        alpha_kf.launch()
        top_kf.value -= PADDING
        top_kf.curve = fantas.faster_curve
        top_kf.launch()
