from pathlib import Path
import os
work_dir = Path(os.getcwd())
if work_dir.name != "Software":
    work_dir /= "Software"
    os.chdir(work_dir)

import fantas
from fantas import uimanager as u
import pygame

import pool
def load_font():
    u.fonts = fantas.load_res_group("./assets/fonts/")
_font = pool.POOL.submit(load_font)

import link
link.init()

import colors
import textstyle

import title_bar
import connect_bar

screen_size = pygame.display.get_desktop_sizes()[0]
if (screen_size[0] > 1920 and screen_size[1] > 1080):
    screen_size = (1920, 1080)
elif screen_size[0] > 1280 and screen_size[1] > 720:
    screen_size = (1280, 720)
else:
    screen_size = (1120, 630)

u.init("感应线圈传感器", screen_size, borderless=True, resizable=True)

def load_image():
    u.images = fantas.load_res_group("./assets/images/")
_image = pool.POOL.submit(load_image)

u.root = fantas.Root(colors.LIGHTBLUE1)

title_ani = None
title_text = None
def load_start_ani():
    global title_ani, title_text
    title_ani = fantas.Animation("./assets/ani/title.webp", center=(u.window.size[0] / 2, u.window.size[1] / 2))
    title_ani.join_to(u.root, 0)
    title_ani.bind_stop_callback(title_ani.leave)
    title_ani.play(1)
    class TiTleAniWidget(fantas.Widget):
        def __init__(self, ani):
            super().__init__(ani)
            self.ani = ani
        
        def handle(self, event):
            if event.type == pygame.WINDOWSIZECHANGED:
                self.ani.rect.center = (u.window.size[0] / 2, u.window.size[1] / 2)
                if title_text is not None:
                    title_text.rect.center = (u.window.size[0] / 2, u.window.size[1] / 2)
    TiTleAniWidget(title_ani).apply_event()
pool.POOL.submit(load_start_ani)

_font.result()
title_bar = title_bar.TitleBar()
title_bar.join(u.root)

title_text = fantas.Text("EICS", u.fonts['maplemono'], textstyle.TITLE_TEXT, center=(u.window.size[0] / 2, u.window.size[1] / 2))
title_text.join(u.root)
title_text.alpha = 0
tt_alpha_kf = fantas.UiKeyFrame(title_text, 'alpha', 255, 90, fantas.harmonic_curve)
tt_size_kf = fantas.TextKeyFrame(title_text, 'size', 48, 30, fantas.radius_curve)
tt_midleft_kf = fantas.RectKeyFrame(title_text, 'midleft', (title_bar.rect.h / 4, title_bar.rect.h / 2), 30, fantas.radius_curve)
tt_midleft_kf.bind_endupwith(title_bar.enable_set_page)
tt_fgcolor_kf = fantas.TextKeyFrame(title_text, 'fgcolor', colors.LIGHTBLUE1, 30, fantas.radius_curve)
tt_fgcolor_kf.bind_endupwith(title_bar.set_page, '检测')

connect_bar = connect_bar.ConnectBar(title_bar)
connect_bar.join_to(u.root, 0)
tt_size_kf.bind_endupwith(connect_bar.appear)

fantas.Trigger(tt_alpha_kf.launch).launch(180)
# fantas.Trigger(tt_alpha_kf.launch).launch(1)
def title_text_return():
    tt_size_kf.launch()
    tt_midleft_kf.launch()
    tt_fgcolor_kf.launch()
tt_alpha_kf .bind_endupwith(title_text_return)

_image.result()
u.window.set_icon(u.images['icon'])

try:
    u.mainloop()
except Exception:
    import traceback
    traceback.print_exc()
finally:
    u.quit()
