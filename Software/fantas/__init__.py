import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'              # 隐藏 Pygame 支持提示
os.environ['SDL_IME_SHOW_UI'] = '1'                         # 显示输入法编辑器 (IME) 界面
os.environ['SDL_VIDEO_ALLOW_SCREENSAVER'] = '1'             # 允许屏幕保护程序
os.environ['SDL_WINDOWS_DPI_AWARENESS'] = 'permonitorv2'    # 启用每个监视器（V2）的 DPI 感知
del os
import pygame
import pygame.freetype
pygame.init()
pygame.freetype.init()
del pygame

from .resource import *
from .abstract import *
from .framework import *

# 预设曲线
# y = x
curve = Curve()
# 渐快(加速)
faster_curve = FormulaCurve('x**2')
# 渐慢(刹车/弹射)
slower_curve = FormulaCurve('2*x-x**2')
# 简谐(平滑/惯性)(有一条高度重合的三次曲线：3*x**2-2*x**3，计算速度稍快)
harmonic_curve = FormulaCurve('(1-math.cos(math.pi*x))/2')
# 正弦(抖动/原地)
# sin_curve = FormulaCurve('math.sin(math.pi*x*2)')
# 抛物线(最高点1)
# parabola1 = FormulaCurve('4*x-4*x**2')
# 越界回弹线
# rebound_curve = FormulaCurve('-2*x**2+3*x')
# 尺寸回转线
# cos_curve = FormulaCurve('math.cos(math.pi*x*3)/2+0.5')
# 圆弧曲线(中段极为陡峭)
radius_curve = SuperCurve(
    curves=(
        FormulaCurve('0.5-math.sqrt(0.25-x**2)'),
        FormulaCurve('math.sqrt(0.25-(x-1)**2)+0.5'),
    ),
    splits=(0.5,)
)

import platform
PLATFORM = platform.system()
del platform

from .basicui import *
from .basicwidget import *
from .keyframe import *
from .uiwidget import *
