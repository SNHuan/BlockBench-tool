@echo off
chcp 65001 > nul
echo 正在检查 Python 环境...

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo Python未安装！请先安装Python 3.8或更高版本。
    pause
    exit
)

:: 检查虚拟环境是否存在
if not exist "venv" (
    echo 正在创建虚拟环境...
    python -m venv venv
    echo 正在安装依赖...
    :: 使用完整路径调用 activate
    call "%~dp0venv\Scripts\activate.bat"
    pip install -r requirements.txt
) else (
    :: 使用完整路径调用 activate
    call "%~dp0venv\Scripts\activate.bat"
)

:: 启动程序
echo 正在启动程序...
python main.py

call "%~dp0venv\Scripts\deactivate.bat"
pause