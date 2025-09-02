# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import shutil
import subprocess

# ---------- 基础路径 ----------
BASE_DIR   = os.path.abspath(SPECPATH)
ENTRY_FILE = os.path.join(BASE_DIR, 'main.py')
DIST_DIR   = os.path.join(BASE_DIR, 'dist')
BUILD_DIR  = os.path.join(BASE_DIR, 'build')

# ---------- 平台相关 ----------
if sys.platform.startswith('win'):
    ICON_FILE = os.path.join(BASE_DIR, 'icon.ico')
    EXE_NAME  = 'EICS.exe'
elif sys.platform == 'darwin':
    ICON_FILE = os.path.join(BASE_DIR, 'icon.icns')
    EXE_NAME  = 'EICS.app'
else:
    ICON_FILE = None
    EXE_NAME  = 'EICS'

# ---------- 资源目录 ----------
ASSETS_SRC = os.path.join(BASE_DIR, 'assets', 'data')        # 源资源目录
ASSETS_DST = os.path.join(DIST_DIR, EXE_NAME, 'assets')      # 目标目录

# ---------- 1. 清理旧产物 ----------
# def clean_old():
#     for d in (BUILD_DIR, DIST_DIR):
#         if os.path.isdir(d):
#             shutil.rmtree(d)
# 
# clean_old()

# ---------- 2. 常规 PyInstaller 配置 ----------
a = Analysis(
    [ENTRY_FILE],
    pathex=[],
    binaries=[],
    datas=[],                 # 若资源已在 assets 目录，这里无需再写
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EICS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_FILE or None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EICS',
)

# ---------- 3. macOS 专属 .app ----------
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='EICS.app',
        icon=ICON_FILE,
        bundle_identifier='com.example.myapp',
        info_plist={
            'CFBundleDisplayName': 'EICS',
            'CFBundleShortVersionString': '1.0.0',
            'LSUIElement': False,   # 不显示 Dock 图标（按需调整）
        },
    )

# ---------- 4. 打包后复制资源 ----------
# def copy_assets():
#     if not os.path.isdir(ASSETS_SRC):
#         print('资源目录不存在，跳过复制：', ASSETS_SRC)
#         return
# 
#     # 确保目标目录存在
#     os.makedirs(ASSETS_DST, exist_ok=True)
# 
#     # 拷贝所有文件/子目录
#     shutil.copy2(os.path.join(BASE_DIR, 'keymap'), os.path.join(BASE_DIR, EXE_NAME))
#     for item in os.listdir(ASSETS_SRC):
#         src_path = os.path.join(ASSETS_SRC, item)
#         dst_path = os.path.join(ASSETS_DST, item)
#         if os.path.isdir(src_path):
#             shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
#         else:
#             shutil.copy2(src_path, dst_path)
#     print('资源文件已复制到：', ASSETS_DST)

# 使用 PyInstaller 的 hook 机制，在打包流程完成后执行
# import PyInstaller.config
# PyInstaller.config.CONF['postbuild_hook'] = copy_assets
