import time

import fantas
from fantas import uimanager as u

import link

import colors
import iconmap
import textstyle
import buttonstyle

import page_button

class MeasurePageButton(page_button.PageButton):
    def __init__(self, title_bar, **anchor):
        super().__init__(title_bar, '检测', iconmap.MEASURE, **anchor)
        self.usable_rect = title_bar.get_usable_rect()
        self.running = False

    def show_page(self):
        super().show_page()
        self.auto_adjust_size()
        self.start_link()
    
    def hide_page(self):
        super().hide_page()

    def auto_adjust_size(self):
        if not self.is_banned:
            return
        usable_rect = self.title_bar.get_usable_rect()
        if self.usable_rect == usable_rect:
            return
        self.usable_rect = usable_rect
    
    def start_link(self):
        if link.state == 'success':
            self.running = True
            link.send_read_data('Measure', self.show_results)

    def show_results(self, byte_data):
        print(byte_data)
        if self.running and link.state == 'success':
            time.sleep(0.2)
            link.send_read_data('Measure', self.show_results)
        else:
            self.running = False

