@echo off
chcp 65001 >nul
title ByteIQ Web GUI
echo ================================================
echo 🧠 ByteIQ Web GUI 启动器
echo ================================================
echo.

echo 📦 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo ✅ Python环境正常
echo.

echo 🚀 启动Web GUI...
python start_gui.py

echo.
echo 按任意键退出...
pause >nul
