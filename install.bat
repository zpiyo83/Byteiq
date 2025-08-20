@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Forge AI Code Windows 一键安装脚本

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🤖 Forge AI Code                         ║
echo ║                   智能AI编程助手                              ║
echo ║                   Windows 一键安装                           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: 检查Python
echo [INFO] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到Python。请先安装Python 3.8或更高版本。
    echo [INFO] 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 获取Python版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python版本检查通过: %PYTHON_VERSION%

:: 检查pip
echo [INFO] 检查pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到pip。请确保pip已正确安装。
    pause
    exit /b 1
)
echo [SUCCESS] pip检查通过

:: 升级pip
echo [INFO] 升级pip到最新版本...
python -m pip install --upgrade pip

:: 安装Forge AI Code
echo [INFO] 开始安装Forge AI Code...

:: 方法1: 从PyPI安装
echo [INFO] 尝试从PyPI安装...
pip install forge-ai-code --upgrade >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] 从PyPI安装成功
    goto verify
)

:: 方法2: 从GitHub安装
echo [WARNING] PyPI安装失败，尝试从GitHub安装...
pip install git+https://github.com/forge-ai/forge-ai-code.git >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] 从GitHub安装成功
    goto verify
)

:: 方法3: 手动指导
echo [WARNING] 自动安装失败，请手动安装:
echo.
echo 1. 下载源码: https://github.com/forge-ai/forge-ai-code/archive/main.zip
echo 2. 解压到任意目录
echo 3. 在解压目录中运行: pip install .
echo.
pause
exit /b 1

:verify
:: 验证安装
echo [INFO] 验证安装...
forge-ai-code --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] 安装验证成功!
    goto success
)

fac --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] 安装验证成功!
    goto success
)

echo [ERROR] 安装验证失败
pause
exit /b 1

:success
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🎉 安装成功!                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo [INFO] 使用方法:
echo.
echo   启动程序:
echo     forge-ai-code
echo     或者: fac
echo.
echo   首次使用:
echo     1. 设置OpenAI API密钥
echo     2. 选择工作模式
echo     3. 开始AI编程
echo.
echo   获取帮助:
echo     forge-ai-code --help
echo.
echo   更多信息:
echo     GitHub: https://github.com/forge-ai/forge-ai-code
echo.
echo 🚀 享受AI编程之旅!
echo.
pause
