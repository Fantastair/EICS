@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo === Windows �����Զ�����ű� ===
echo - ��Ҫ Python ���⻷��
echo - ��Ҫ pygame-ce 2.5.5
echo - ��Ҫ pyserial 3.5
echo - ��Ҫ PyInstaller
echo - ���ʱ������Ҫ���� y �����س�ȷ�ϣ������������
echo.

set /p VENV_PATH=���������⻷����Ŀ¼: 

set "ACTIVATE_PATH=%VENV_PATH%\Scripts\activate.bat"

if not exist "%ACTIVATE_PATH%" (
    echo ���⻷��������: %ACTIVATE_PATH%
    pause
    exit /b 1
)

call "%ACTIVATE_PATH%"

pyinstaller main.spec --clean
python after_pack.py

echo === ������ ===
pause
