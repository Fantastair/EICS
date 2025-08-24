import pygame
import fantas
from fantas import uimanager as u

import pool
import link

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
        self.search_button.bind(self.search)
        self.search_button.join(self)
        fantas.Text("连接传感器", u.fonts['maplemono'], textstyle.CONNECTBAR_NORMAL_TEXT, center=(self.search_button.rect.w / 2, self.search_button.rect.h / 2)).join(self.search_button)

        self.ani = {
            'no2search': None,
            'search2search': None,
            'search2success': None,
            'search2no': None,
            'success2no': None
        }
        for name in self.ani:
            pool.POOL.submit(self.load_ani, name)

    def load_ani(self, name):
        self.ani[name] = fantas.Animation(f"./assets/ani/{name}.webp", center=(self.rect.w / 2, 120 + (self.rect.h - 260) / 2))
        if name == 'no2search':
            self.ani['no2search'].join(self)
            self.ani['no2search'].bind_stop_callback(self.search_callback)
        elif name == 'search2search':
            self.ani['search2search'].bind_stop_callback(self.search_callback)

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
            self.shadow.mark_update()
            self.search_button.rect.centery = self.rect.h - 70
            for i in self.ani:
                self.ani[i].rect.centery = 120 + (self.rect.h - 260) / 2

    def search(self):
        if link.state == 'no':
            self.show_ani('no2search')
            self.ani['no2search'].play(1)
            pool.POOL.submit(link.auto_connect)

    def show_ani(self, name):
        if self.ani[name].is_root():
            self.ani[name].join(self)
        for i in self.ani:
            if self.ani[i].current_frame != 0:
                self.ani[i].set_frame(0)
            if i != name and not self.ani[i].is_root():
                self.ani[i].leave()

    def search_callback(self):
        if link.state == 'search':
            self.temp = 1
            self.show_ani('search2search')
            fantas.Trigger(self.ani['search2search'].play, 1).launch(30)
        elif link.state == 'no':
            self.show_ani('search2no')
            self.ani['search2no'].play(1)
        else:
            self.show_ani('search2success')
            self.ani['search2success'].play(1)
    
    def offline(self):
        self.show_ani('success2no')
        self.ani['success2no'].play(1)


class ConnectBarWidget(fantas.Widget):
    def __init__(self, connect_bar):
        super().__init__(connect_bar)
        self.connect_bar = connect_bar

    def handle(self, event):
        if event.type == pygame.WINDOWSIZECHANGED:
            self.connect_bar.auto_set_height()
        elif event.type == link.OFFLINE:
            self.connect_bar.offline()
