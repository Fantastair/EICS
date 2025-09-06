@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

:: 移动到脚本所在目录
cd /d "%~dp0"

echo === Windows 环境自动打包脚本 ===
echo 需要 Python 环境（已配置到 PATH）
python --version >nul 2>&1 || (
    echo 未检测到 python 命令，请先安装 Python 并将其加入 PATH
    pause
    exit /b 1
)

set "PYGAME_VERSION=2.5.5"
set "PYSERIAL_VERSION=3.5"

:menu
echo.
echo "选择操作（建议使用虚拟环境打包）："
echo "1.输入已有虚拟环境根目录（内部必须包含 Scripts\activate.bat）"
echo "2.在当前目录自动创建虚拟环境（.venv，已存在可以重复使用）"
echo "3.使用全局环境（不推荐）"
echo "4.退出"
echo.

set /p OPTION=请输入选项（1-4）: || goto menu
if "%OPTION%"=="1" goto use_exist_venv
if "%OPTION%"=="2" goto create_venv
if "%OPTION%"=="3" goto use_global
if "%OPTION%"=="4" exit /b 0
goto menu

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:use_exist_venv
set /p VENV_PATH=请输入虚拟环境根目录（绝对/相对路径均可）: 
set "ACTIVATE_PATH=%VENV_PATH%\Scripts\activate.bat"
if not exist "%ACTIVATE_PATH%" (
    echo 错误：未找到激活脚本 "%ACTIVATE_PATH%"
    pause
    exit /b 1
)
goto activate_and_install

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:create_venv
set "VENV_PATH=.venv"
set "ACTIVATE_PATH=%VENV_PATH%\Scripts\activate.bat"
if exist "%ACTIVATE_PATH%" (
    echo 虚拟环境已存在：%VENV_PATH%
    goto activate_and_install
)
echo 正在创建虚拟环境 %VENV_PATH% ...
python -m venv "%VENV_PATH%"
if errorlevel 1 (
    echo 创建虚拟环境失败
    pause
    exit /b 1
)
goto activate_and_install

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:use_global
echo 警告：使用全局环境，可能影响系统其他项目
goto install_deps

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:activate_and_install
call "%ACTIVATE_PATH%"
if errorlevel 1 (
    echo 激活虚拟环境失败
    pause
    exit /b 1
)
echo 已激活虚拟环境：%VENV_PATH%

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:install_deps
echo 正在安装/更新依赖 ...
python -m pip install --upgrade pip
python -m pip install pygame-ce==%PYGAME_VERSION% pyserial==%PYSERIAL_VERSION% pyinstaller
if errorlevel 1 (
    echo 依赖安装失败，请检查网络或权限
    pause
    exit /b 1
)

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:build
echo.
echo 开始打包（可能需要输入 y 确认清除缓存）...
pyinstaller main.spec --clean
if errorlevel 1 (
    echo 打包失败
    pause
    exit /b 1
)
python after_pack.py
if errorlevel 1 (
    echo after_pack.py 执行失败
    pause
    exit /b 1
)

:: 清理中间产物
if exist "build" rmdir /s /q build
if exist "__pycache__" rmdir /s /q __pycache__

echo.
echo === 打包完成 ===
if "%OPTION%"=="2" (
    echo.
    set /p DELETE_VENV=是否删除临时创建的虚拟环境 .venv ？(y/n): || set "DELETE_VENV=n"
    if /i "!DELETE_VENV!"=="y" (
        if exist ".venv" (
            rmdir /s /q ".venv"
            echo 虚拟环境 .venv 已删除
        ) else (
            echo .venv 不存在，无需删除
        )
    )
)
pause
exit /b 0
