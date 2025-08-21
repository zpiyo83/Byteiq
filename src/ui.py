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
    from src.theme import theme_manager

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
    blue = Fore.CYAN
    white = Fore.WHITE
    yellow = Fore.YELLOW

    # 先打印ASCII艺术字标题
    ascii_art = get_forge_ai_ascii()
    for line in ascii_art:
        print(f"{light_blue}{line}{Style.RESET_ALL}")

    print()

    # 打印欢迎信息
    print(f"{light_blue}{'='*60}{Style.RESET_ALL}")
    print(f"{white}Welcome to {light_blue}Forge AI Code{Style.RESET_ALL}")
    print(f"{light_blue}{'='*60}{Style.RESET_ALL}")
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
    print()

    # 不在欢迎界面显示输入框，让主循环统一处理

def print_input_box():
    """打印输入框"""
    gray = Fore.LIGHTBLACK_EX  # 灰色

    # 输入框宽度
    input_box_width = 80

    # 输入框顶部边框（圆角，灰色）
    print(f"{gray}╭{'─' * (input_box_width - 2)}╮{Style.RESET_ALL}")

    # 输入框内容行 - 空的，没有占位符
    print(f"{gray}│{' ' * (input_box_width - 2)}│{Style.RESET_ALL}")

    # 输入框底部边框（圆角，灰色）
    print(f"{gray}╰{'─' * (input_box_width - 2)}╯{Style.RESET_ALL}")

    # 当前模式提示文字（灰色）
    from src.modes import mode_manager
    current_mode = mode_manager.get_current_mode()
    print(f"{gray}? {current_mode}{Style.RESET_ALL}")

def position_cursor_for_input():
    """定位光标到输入框内"""
    # 由于终端兼容性问题，我们简化实现
    # 直接在输入框下方显示提示符
    pass
