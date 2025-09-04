import os
import sys

BASE_DIR   = os.path.abspath(SPECPATH)
ENTRY_FILE = os.path.join(BASE_DIR, 'main.py')

if sys.platform == 'darwin':
    ICON_FILE = os.path.join(BASE_DIR, 'icon.icns')
else:
    ICON_FILE = os.path.join(BASE_DIR, 'icon.ico')

a = Analysis(
    [ENTRY_FILE],
    pathex=[],
    binaries=[],
    datas=[],
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

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='EICS.app',
        icon=ICON_FILE,
        bundle_identifier='com.example.myapp',
        info_plist={
            'CFBundleDisplayName': 'EICS',
            'CFBundleShortVersionString': '1.0.0',
        },
    )
