from pathlib import Path
import os, sys, platform

if getattr(sys, 'frozen', False):    # 打包发布环境
    if platform.system() == 'Darwin':
        os.chdir(Path(sys.executable).parent.parent)
else:                                # 开发环境
    os.chdir(Path(os.getcwd()) / 'Software')

import fantas
from fantas import uimanager as u

if fantas.PLATFORM == "Darwin":
    u.dpi_ratio = 2
else:
    u.dpi_ratio = 1

import pygame
import pygame.freetype

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

u.init("电磁轨道检测装置 - 上位机", screen_size, borderless=True, resizable=True, allow_high_dpi=True)

def load_image():
    u.images = fantas.load_res_group("./assets/images/")
_image = pool.POOL.submit(load_image)

u.root = fantas.Root(colors.LIGHTBLUE1)

title_ani = None
title_text = None
def load_start_ani():
    global title_ani, title_text
    title_ani = fantas.Animation("./assets/ani/title.webp", center=(u.window.size[0] * u.dpi_ratio / 2, u.window.size[1] * u.dpi_ratio / 2))
    title_ani.join_to(u.root, 0)
    title_ani.bind_stop_callback(title_ani.leave)
    title_ani.play(1)
    author_sign = fantas.Text("Written By Fantastair", u.fonts['maplemono'], {'size': 20, 'fgcolor': colors.DARKBLUE, 'style': pygame.freetype.STYLE_OBLIQUE}, midbottom=(u.window.size[0] * u.dpi_ratio / 2, u.window.size[1] * u.dpi_ratio - 20))
    author_sign.join(u.root)
    author_sign.alpha = 0
    curve = fantas.SuperCurve(
    (
        fantas.FormulaCurve(f"{1/0.33}*x"),
        fantas.FormulaCurve("1"),
        fantas.FormulaCurve(f"{-1/(1-0.66)}*x+{1/(1-0.66)}")
    ),
        (0.33, 0.66)
    )
    as_alpha_kf = fantas.UiKeyFrame(author_sign, 'alpha', 255, 270, curve)
    as_alpha_kf.bind_endupwith(author_sign.leave)
    as_alpha_kf.launch()
    class TiTleAniWidget(fantas.Widget):
        def __init__(self, ani):
            super().__init__(ani)
            self.ani = ani

        def handle(self, event):
            if event.type == pygame.WINDOWSIZECHANGED:
                self.ani.rect.center = (u.window.size[0] * u.dpi_ratio / 2, u.window.size[1] * u.dpi_ratio / 2)
                if title_text is not None:
                    title_text.rect.center = (u.window.size[0] * u.dpi_ratio / 2, u.window.size[1] * u.dpi_ratio / 2)
                author_sign.rect.midbottom = (u.window.size[0] * u.dpi_ratio / 2, u.window.size[1] * u.dpi_ratio - 20)
    TiTleAniWidget(title_ani).apply_event()
pool.POOL.submit(load_start_ani)

_font.result()
_image.result()
title_bar = title_bar.TitleBar()
title_bar.join(u.root)

title_text = fantas.Text("EICS", u.fonts['maplemono'], textstyle.TITLE_TEXT, center=(u.window.size[0] * u.dpi_ratio / 2, u.window.size[1] * u.dpi_ratio / 2))
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

# tt_alpha_kf.launch()
fantas.Trigger(tt_alpha_kf.launch).launch(180)
def title_text_return():
    tt_size_kf.launch()
    tt_midleft_kf.launch()
    tt_fgcolor_kf.launch()
tt_alpha_kf .bind_endupwith(title_text_return)

u.window.set_icon(u.images['icon'])

try:
    u.mainloop()
except Exception:
    import traceback
    traceback.print_exc()
finally:
    u.quit()
