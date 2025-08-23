import pygame
import fantas
from fantas import uimanager as u

import colors
import textstyle
import buttonstyle

import title_bar


class ConnectBar(fantas.Label):
    WIDTH = 320
    
    def __init__(self):
        super().__init__((ConnectBar.WIDTH, u.window.size[1] - title_bar.TitleBar.HEIGHT), bg=colors.WHITE, topright=(-24, title_bar.TitleBar.HEIGHT))
        self.anchor = 'topleft'
        self.shadow = fantas.Ui(self.get_shadow(), topleft=self.rect.topright)
        self.shadow.anchor = 'topleft'
        self.left_kf = fantas.RectKeyFrame(self, 'left', 0, 20, fantas.radius_curve)
        self.shadow_left_kf = fantas.RectKeyFrame(self.shadow, 'left', ConnectBar.WIDTH, 20, fantas.radius_curve)
        self.widget = ConnectBarWidget(self)
        self.widget.apply_event()

        fantas.Text("电磁轨道检测装置", u.fonts['maplemono'], textstyle.CONNECTBAR_NORMAL_TEXT, center=(self.rect.w / 2, 60)).join(self)
        self.search_button = fantas.SmoothColorButton((280, 100), buttonstyle.CONNECTBAR_BUTTON, radius={"border_radius": 16}, center=(self.rect.w / 2, self.rect.h - 70))
        self.search_button.join(self)
        fantas.Text("连接传感器", u.fonts['maplemono'], textstyle.CONNECTBAR_NORMAL_TEXT, center=(self.search_button.rect.w / 2, self.search_button.rect.h / 2)).join(self.search_button)

    def get_shadow(self):
        s = pygame.Surface((24, self.rect.h), flags=pygame.SRCALPHA).convert_alpha()
        s.fill((0, 0, 0, 255), (0, 0, 3, s.get_height()))
        return pygame.transform.gaussian_blur(s, 6)

    def join(self, node):
        self.shadow.join(node)
        super().join(node)
    
    def join_to(self, node, index):
        self.shadow.join_to(node, index)
        super().join_to(node, index)
    
    def leave(self):
        super().leave()
        self.shadow.leave()
    
    def appear(self):
        self.left_kf.launch()
        self.shadow_left_kf.launch()
    
    def auto_set_height(self):
        if u.window.size[1] != self.rect.h:
            self.set_size((self.rect.w, u.window.size[1] - title_bar.TitleBar.HEIGHT))
            self.shadow.img = self.get_shadow()
            self.search_button.rect.centery = self.rect.h - 70
            self.shadow.mark_update()


class ConnectBarWidget(fantas.Widget):
    def __init__(self, connect_bar):
        super().__init__(connect_bar)
        self.connect_bar = connect_bar

    def handle(self, event):
        if event.type == pygame.WINDOWSIZECHANGED:
            self.connect_bar.auto_set_height()