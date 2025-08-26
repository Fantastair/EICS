import pygame
import fantas
from fantas import uimanager as u

import link

import colors
import iconmap
import buttonstyle
import textstyle

import connect_bar

import page_button
import debug_page
import about_page

class TitleBar(fantas.Label):
    HEIGHT = 80
    BUTTON_RADIUS = 20

    def __init__(self):
        super().__init__((u.window.size[0], TitleBar.HEIGHT), bg=colors.THEMEBLUE, topleft=(0, 0))
        self.anchor = 'topleft'

        self.close_window_button = fantas.CircleButton(TitleBar.BUTTON_RADIUS, buttonstyle.TITLEBAR_CLOSE_BUTTON, center=(self.rect.w - self.rect.h / 2, self.rect.h / 2))
        self.close_window_button.join(self)
        self.close_window_button.bind(self.click_close)
        fantas.IconText(iconmap.CLOSE_WINDOW, u.fonts['iconfont'], textstyle.TITLEBAR_WINDOWBUTTON_ICONTEXT, center=(self.close_window_button.rect.w / 2, self.close_window_button.rect.h / 2)).join(self.close_window_button)

        self.maximize_window_button = fantas.CircleButton(TitleBar.BUTTON_RADIUS, buttonstyle.TITLEBAR_WINDOW_BUTTON, center=(self.rect.w - self.rect.h / 2 - TitleBar.BUTTON_RADIUS * 3, self.rect.h / 2))
        self.maximize_window_button.join(self)
        self.maximize_window_button.bind(self.click_maximize)
        fantas.IconText(iconmap.MAXIMIZE_WINDOW, u.fonts['iconfont'], textstyle.TITLEBAR_WINDOWBUTTON_ICONTEXT, center=(self.maximize_window_button.rect.w / 2, self.maximize_window_button.rect.h / 2)).join(self.maximize_window_button)

        self.minimize_window_button = fantas.CircleButton(TitleBar.BUTTON_RADIUS, buttonstyle.TITLEBAR_WINDOW_BUTTON, center=(self.rect.w - self.rect.h / 2 - TitleBar.BUTTON_RADIUS * 6, self.rect.h / 2))
        self.minimize_window_button.join(self)
        self.minimize_window_button.bind(self.click_minimize)
        fantas.IconText(iconmap.MINIMIZE_WINDOW, u.fonts['iconfont'], textstyle.TITLEBAR_WINDOWBUTTON_ICONTEXT, center=(self.minimize_window_button.rect.w / 2, self.minimize_window_button.rect.h / 2)).join(self.minimize_window_button)

        self.normal_state = (u.window.position, u.window.size)
        self.maximized = False

        self.mousewidget = TitleBarWidget(self)
        self.mousewidget.apply_event()

        self.shadow = fantas.Ui(self.get_shadow(), midtop=self.rect.midbottom)
        self.shadow.anchor = 'topleft'

        self.page_enable = False
        self.page_buttons = {
            '检测': page_button.PageButton(self, '检测', iconmap.MEASURE, center=(self.rect.w / 2 - 160, self.rect.h / 2)),
            '调试': debug_page.DebugPageButton(self, center=(self.rect.w / 2, self.rect.h / 2)),
            '关于': about_page.AboutPageButton(self, center=(self.rect.w / 2 + 160, self.rect.h / 2)),
        }
        for i in self.page_buttons:
            self.page_buttons[i].join(self)
        self.last_window_height = u.window.size[1]

    def click_close(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def click_minimize(self):
        u.window.minimize()

    def click_maximize(self):
        if self.maximized:
            u.window.position, u.window.size = self.normal_state
            self.maximized = False
            self.maximize_window_button.kidgroup[0].text = iconmap.MAXIMIZE_WINDOW
            self.maximize_window_button.kidgroup[0].update_img()
        else:
            r = fantas.get_display_usable_bounds()
            u.window.position = (r.x, r.y)
            u.window.size = (r.w, r.h)
            self.maximized = True
            self.maximize_window_button.kidgroup[0].text = iconmap.CANCEL_MAXIMIZE_WINDOW
            self.maximize_window_button.kidgroup[0].update_img()
    
    def auto_set_width(self):
        if u.window.size[0] != self.rect.w:
            self.set_size((u.window.size[0], self.rect.h))
            self.close_window_button.rect.centerx = self.rect.w - self.rect.h / 2
            self.maximize_window_button.rect.centerx = self.rect.w - self.rect.h / 2 - TitleBar.BUTTON_RADIUS * 3
            self.minimize_window_button.rect.centerx = self.rect.w - self.rect.h / 2 - TitleBar.BUTTON_RADIUS * 6
            self.shadow.img = self.get_shadow()
            self.shadow.mark_update()
            self.page_buttons['检测'].rect.centerx = self.rect.w / 2 - 160
            self.page_buttons['调试'].rect.centerx = self.rect.w / 2
            self.page_buttons['关于'].rect.centerx = self.rect.w / 2 + 160
            for i in self.page_buttons:
                self.page_buttons[i].auto_adjust_size()
        elif u.window.size[1] != self.last_window_height:
            for i in self.page_buttons:
                self.page_buttons[i].auto_adjust_size()
        self.last_window_height = u.window.size[1]

    def get_shadow(self):
        s = pygame.Surface((self.rect.w, 24), flags=pygame.SRCALPHA).convert_alpha()
        s.fill((0, 0, 0, 255), (0, 0, s.get_width(), 3))
        return pygame.transform.gaussian_blur(s, 6)

    def join(self, node):
        self.shadow.join(node)
        super().join(node)
    
    def leave(self):
        super().leave()
        self.shadow.leave()
    
    def mouse_on_blank(self):
        result = not (self.close_window_button.mousewidget.mouseon or \
                      self.maximize_window_button.mousewidget.mouseon or \
                      self.minimize_window_button.mousewidget.mouseon)
        if not result:
            return False
        result = not any(self.page_buttons[i].mousewidget.mouseon for i in self.page_buttons)
        return result
    
    def set_page(self, page):
        self.page = page
        if not self.page_enable:
            return
        for i in self.page_buttons:
            if i == page:
                self.page_buttons[i].ban()
                self.page_buttons[i].show_page()
            elif self.page_buttons[i].is_banned:
                self.page_buttons[i].recover()
                self.page_buttons[i].hide_page()

    def enable_set_page(self):
        self.page_enable = True
    
    def get_usable_rect(self):
        return pygame.Rect(connect_bar.ConnectBar.WIDTH, TitleBar.HEIGHT, u.window.size[0] - connect_bar.ConnectBar.WIDTH, u.window.size[1] - TitleBar.HEIGHT)


class TitleBarWidget(fantas.MouseBase):
    EDGE = 10
    MINISIZE = (1120, 630)
    
    def __init__(self, title_bar):
        super().__init__(title_bar, 2)
        self.title_bar = title_bar
        self.start_pos = None
        self.dragging_edge = None
        self.cursor = '^'
    
    def handle(self, event):
        super().handle(event)
        if event.type == pygame.WINDOWSIZECHANGED:
            self.title_bar.auto_set_width()

    def mousepress(self, pos, button):
        if button == pygame.BUTTON_LEFT:
            if not self.title_bar.maximized and (self.dragging_edge is not None or (self.mousedown == pygame.BUTTON_LEFT and self.title_bar.mouse_on_blank())):
                self.start_pos = fantas.get_mouse_position_on_screen()

    def mouserelease(self, pos, button):
        if self.start_pos is not None:
            self.start_pos = None
            self.title_bar.normal_state = (u.window.position, u.window.size)

    def mousemove(self, pos):
        if self.title_bar.maximized:
            return
        if self.start_pos is not None:
            pos = fantas.get_mouse_position_on_screen()
            if self.dragging_edge is not None:
                origin_pos = (self.title_bar.normal_state[0][0], self.title_bar.normal_state[0][1])
                origin_size = (self.title_bar.normal_state[1][0], self.title_bar.normal_state[1][1])
                drag_offset = (pos[0] - self.start_pos[0], pos[1] - self.start_pos[1])
                if 'left' in self.dragging_edge:
                    w = origin_size[0] - drag_offset[0]
                    if w < TitleBarWidget.MINISIZE[0]:
                        w = TitleBarWidget.MINISIZE[0]
                    u.window.size = (w, u.window.size[1])
                    u.window.position = (origin_pos[0] + origin_size[0] - w, u.window.position[1])
                elif 'right' in self.dragging_edge:
                    w = origin_size[0] + drag_offset[0]
                    if w < TitleBarWidget.MINISIZE[0]:
                        w = TitleBarWidget.MINISIZE[0]
                    u.window.size = (w, u.window.size[1])
                if 'top' in self.dragging_edge:
                    h = origin_size[1] - drag_offset[1]
                    if h < TitleBarWidget.MINISIZE[1]:
                        h = TitleBarWidget.MINISIZE[1]
                    u.window.size = (u.window.size[0], h)
                    u.window.position = (u.window.position[0], origin_pos[1] + origin_size[1] - h)
                elif 'bottom' in self.dragging_edge:
                    h = origin_size[1] + drag_offset[1]
                    if h < TitleBarWidget.MINISIZE[1]:
                        h = TitleBarWidget.MINISIZE[1]
                    u.window.size = (u.window.size[0], h)
                self.title_bar.auto_set_width()
            else:
                u.window.position = (self.title_bar.normal_state[0][0] + pos[0] - self.start_pos[0], self.title_bar.normal_state[0][1] + pos[1] - self.start_pos[1])
        else:
            on_left = pos[0] <= self.EDGE
            on_top = pos[1] <= self.EDGE
            on_right = pos[0] >= u.window.size[0] - self.EDGE
            on_bottom = pos[1] >= u.window.size[1] - self.EDGE
            if on_left:
                if on_top:
                    self.dragging_edge = 'top_left'
                    self.set_cursor('\\')
                elif on_bottom:
                    self.dragging_edge = 'bottom_left'
                    self.set_cursor('/')
                else:
                    self.dragging_edge = 'left'
                    self.set_cursor('-')
            elif on_right:
                if on_top:
                    self.dragging_edge = 'top_right'
                    self.set_cursor('/')
                elif on_bottom:
                    self.dragging_edge = 'bottom_right'
                    self.set_cursor('\\')
                else:
                    self.dragging_edge = 'right'
                    self.set_cursor('-')
            elif on_top:
                self.dragging_edge = 'top'
                self.set_cursor('|')
            elif on_bottom:
                self.dragging_edge = 'bottom'
                self.set_cursor('|')
            elif self.cursor != '^':
                self.set_cursor('^')
                self.dragging_edge = None
    
    def set_cursor(self, cursor):
        pygame.mouse.set_cursor(u.cursor_map[cursor])
        self.cursor = cursor
