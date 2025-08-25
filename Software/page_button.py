import fantas
from fantas import uimanager as u

import colors
import textstyle
import buttonstyle

class PageButton(fantas.SmoothColorButton):
    SIZE = (120, 40)

    def __init__(self, title_bar, text, icon, **anchor):
        super().__init__(PageButton.SIZE, buttonstyle.TITLEBAR_PAGE_BUTTON, radius={'border_radius': PageButton.SIZE[1] // 2}, **anchor)
        self.text = fantas.Text(text, u.fonts['maplemono'], textstyle.TITLEBAR_BUTTON_TEXT, midright=(self.rect.w - self.rect.h / 2 + 4, self.rect.h / 2))
        self.text.join(self)
        self.icon = fantas.IconText(icon, u.fonts['iconfont'], textstyle.TITLEBAR_BUTTON_ICONTEXT, center=(self.rect.h / 2 + 10, self.rect.h / 2))
        self.icon.join(self)
        self.title_bar = title_bar
        self.bind(title_bar.set_page, text)
        self.text_color_kf = fantas.TextKeyFrame(self.text, 'fgcolor', colors.THEMEBLUE, 10, fantas.harmonic_curve)
        self.icon_color_kf = fantas.TextKeyFrame(self.icon, 'fgcolor', colors.THEMEBLUE, 10, fantas.harmonic_curve)
    
    def show_page(self):
        self.text_color_kf.value = self.icon_color_kf.value = colors.THEMEBLUE
        self.text_color_kf.launch()
        self.icon_color_kf.launch()

    def hide_page(self):
        self.text_color_kf.value = self.icon_color_kf.value = colors.FAKEWHITE
        self.text_color_kf.launch()
        self.icon_color_kf.launch()
    
    def auto_adjust_size(self):
        pass

    def start_link(self):
        pass
