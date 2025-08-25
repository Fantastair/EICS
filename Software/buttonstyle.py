import pygame
import colors

TITLEBAR_CLOSE_BUTTON = {
    'origin_bg': colors.THEMEBLUE - pygame.Color(0, 0, 0, 255),
    'origin_bd': 0,
    'origin_sc': None,

    'hover_bg': colors.WARNRED,
    'hover_bd': 0,
    'hover_sc': None,

    'press_bg': colors.WARNRED - colors.offset_color,
    'press_bd': 0,
    'press_sc': None,
}

TITLEBAR_WINDOW_BUTTON = {
    'origin_bg': colors.THEMEBLUE - pygame.Color(0, 0, 0, 255),
    'origin_bd': 0,
    'origin_sc': None,

    'hover_bg': colors.LIGHTBLUE2,
    'hover_bd': 0,
    'hover_sc': None,

    'press_bg': colors.LIGHTBLUE3,
    'press_bd': 0,
    'press_sc': None,
}

TITLEBAR_PAGE_BUTTON = {
    'origin_bg': colors.THEMEBLUE,
    'origin_bd': 0,
    'origin_sc': None,

    'hover_bg': colors.LIGHTBLUE2,
    'hover_bd': 0,
    'hover_sc': None,

    'press_bg': colors.LIGHTBLUE3,
    'press_bd': 0,
    'press_sc': None,

    'ban_bg': colors.FAKEWHITE,
    'ban_bd': 0,
    'ban_sc': None
}

CONNECTBAR_BUTTON = {
    'origin_bg': colors.WHITE,
    'origin_bd': 2,
    'origin_sc': colors.DARKBLUE,

    'hover_bg': colors.LIGHTBLUE1,
    'hover_bd': 2,
    'hover_sc': colors.DARKBLUE,

    'press_bg': colors.LIGHTBLUE2,
    'press_bd': 2,
    'press_sc': colors.DARKBLUE,
}

del colors, pygame
