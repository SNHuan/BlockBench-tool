@echo off
chcp 65001
setlocal enabledelayedexpansion

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [31mPython未安装！请先安装Python 3.x[0m
    pause
    exit /b 1
)

:: 检查虚拟环境是否存在
if not exist "venv" (
    echo [32m正在创建虚拟环境...[0m
    python -m venv venv
    if errorlevel 1 (
        echo [31m创建虚拟环境失败！[0m
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
call venv\Scripts\activate

:: 检查依赖是否安装
pip show customtkinter >nul 2>&1
if errorlevel 1 (
    echo [32m正在安装依赖...[0m
    pip install customtkinter pillow CTkMessagebox darkdetect
    if errorlevel 1 (
        echo [31m安装依赖失败！[0m
        pause
        exit /b 1
    )
)

:: 启动程序
echo [32m正在启动程序...[0m
python main.py

:: 如果程序异常退出，暂停显示错误信息
if errorlevel 1 (
    echo [31m程序异常退出！[0m
    pause
)

:: 退出虚拟环境
deactivate 