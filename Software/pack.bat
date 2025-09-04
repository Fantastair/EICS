@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo === Windows 环境自动打包脚本 ===
echo - 需要 Python 虚拟环境
echo - 需要 pygame-ce 2.5.5
echo - 需要 pyserial 3.5
echo - 需要 PyInstaller
echo - 打包时可能需要输入 y 并按回车确认，用于清除缓存
echo.

set /p VENV_PATH=请输入虚拟环境根目录: 

set "ACTIVATE_PATH=%VENV_PATH%\Scripts\activate.bat"

if not exist "%ACTIVATE_PATH%" (
    echo 虚拟环境不存在: %ACTIVATE_PATH%
    pause
    exit /b 1
)

call "%ACTIVATE_PATH%"

pyinstaller main.spec --clean
python after_pack.py

echo === 打包完成 ===
pause
