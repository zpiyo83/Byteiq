"""
用户界面模块
"""

import os
from colorama import Fore, Style
from .modes import mode_manager

def get_wave_icon():
    """生成音符条样式的图标 - 3个点横向排列"""
    return ["●●●"]

def get_forge_ai_ascii():
    """生成FORGE AI CODE的ASCII艺术字"""
    ascii_art = [
        "███████╗ ██████╗ ██████╗  ██████╗ ███████╗",
        "██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝",
        "█████╗  ██║   ██║██████╔╝██║  ███╗█████╗  ",
        "██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  ",
        "██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗",
        "╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝",
        "",
        " █████╗ ██╗     ██████╗  ██████╗ ██████╗ ███████╗",
        "██╔══██╗██║    ██╔════╝ ██╔═══██╗██╔══██╗██╔════╝",
        "███████║██║    ██║      ██║   ██║██║  ██║█████╗  ",
        "██╔══██║██║    ██║      ██║   ██║██║  ██║██╔══╝  ",
        "██║  ██║██║    ╚██████╗ ╚██████╔╝██████╔╝███████╗",
        "╚═╝  ╚═╝╚═╝     ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝"
    ]
    return ascii_art

def print_welcome_screen():
    """打印欢迎界面"""
    # 清屏
    os.system('cls' if os.name == 'nt' else 'clear')

    # 导入配置和主题管理器
    from src.config import load_config


    # 获取当前工作目录
    current_dir = os.getcwd()

    # 加载配置
    config = load_config()

    # 获取配置信息
    model = config.get("model", "gpt-3.5-turbo")
    language = config.get("language", "zh-CN")
    theme = config.get("theme", "default")

    # 淡蓝色主题颜色
    light_blue = Fore.LIGHTCYAN_EX

    white = Fore.WHITE
    yellow = Fore.YELLOW

    # 先打印ASCII艺术字标题
    ascii_art = get_forge_ai_ascii()
    for line in ascii_art:
        print(f"{light_blue}{line}{Style.RESET_ALL}")

    print()

    # 动态获取终端宽度
    import shutil
    try:
        terminal_width = shutil.get_terminal_size().columns
    except OSError:
        terminal_width = 80 # 如果无法获取，则使用默认值

    # 打印欢迎信息
    welcome_text = "Welcome to Forge AI Code"
    # 居中显示欢迎文本
    centered_welcome_text = welcome_text.center(terminal_width)

    print(f"{light_blue}{'=' * terminal_width}{Style.RESET_ALL}")
    print(f"{white}{centered_welcome_text}{Style.RESET_ALL}")
    print()

    # 打印基础配置信息
    print(f"{light_blue}Configuration:{Style.RESET_ALL}")
    print(f"  {white}Model:{Style.RESET_ALL} {model}")
    print(f"  {white}Language:{Style.RESET_ALL} {language}")
    print(f"  {white}Theme:{Style.RESET_ALL} {theme}")
    print(f"  {white}Directory:{Style.RESET_ALL} {current_dir}")
    print(f"  {white}Mode:{Style.RESET_ALL} {mode_manager.get_current_mode()}")
    print()

    # 打印使用提示
    print(f"{light_blue}Usage Tips:{Style.RESET_ALL}")
    print(f"  {white}*{Style.RESET_ALL} Type your coding requests directly")
    print(f"  {white}*{Style.RESET_ALL} Type {yellow}/help{Style.RESET_ALL} for available commands")
    print(f"  {white}*{Style.RESET_ALL} Type {yellow}/s{Style.RESET_ALL} for settings")
    print(f"  {white}*{Style.RESET_ALL} Type {yellow}/mode{Style.RESET_ALL} to switch modes")
    print(f"{light_blue}{'=' * terminal_width}{Style.RESET_ALL}")
    print()

    # 不在欢迎界面显示输入框，让主循环统一处理

def print_input_box():
    """打印一个简单的输入提示符，而不是一个完整的框。"""
    # 这个函数现在不再打印一个框，主循环将处理提示符的显示
    pass

def position_cursor_for_input():
    """这个函数不再需要，但保留为空以避免导入错误。"""
    pass
