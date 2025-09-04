import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR   = os.getcwd()
DIST_DIR   = os.path.join(BASE_DIR, 'dist')
ASSETS_SRC = os.path.join(BASE_DIR, 'assets')

if sys.platform == 'darwin':
    WORK_DIR = os.path.join(DIST_DIR, 'EICS.app', 'Contents')
else:
    WORK_DIR = os.path.join(DIST_DIR, 'EICS')

def copy_assets():
    print('开始复制资源文件')
    os.makedirs(os.path.join(WORK_DIR, 'assets'), exist_ok=True)
    shutil.copy2(os.path.join(BASE_DIR, 'keymap'), WORK_DIR)
    for item in os.listdir(ASSETS_SRC):
        src_path = os.path.join(ASSETS_SRC, item)
        dst_path = os.path.join(WORK_DIR, 'assets', item)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dst_path)
    if sys.platform == 'darwin':
        libintl = Path(WORK_DIR) / 'Frameworks' / 'pygame' / '__dot__dylibs' / 'libintl.8.dylib'
        if libintl.exists():
            libintl.unlink()

        def get_libintl_path():
            try:
                prefix = subprocess.check_output(
                    ["brew", "--prefix", "gettext"],
                    stderr=subprocess.DEVNULL,
                    text=True
                ).strip()
                libintl_path = os.path.join(prefix, "lib", "libintl.8.dylib")
                if os.path.isfile(libintl_path):
                    return Path(libintl_path)
            except subprocess.CalledProcessError:
                pass
            return None

        sys_libintl = get_libintl_path()
        if sys_libintl:
            shutil.copy2(sys_libintl, libintl)

    print('资源文件复制成功')

copy_assets()
