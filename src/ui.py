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

    # 获取终端宽度并计算输入框宽度（保留左右边距）
    try:
        import shutil
        terminal_width = shutil.get_terminal_size().columns
        input_box_width = min(terminal_width - 4, 120)  # 最大宽度120，保留4列边距
    except:
        input_box_width = 110  # 默认宽度

    # 输入框顶部边框（圆角，灰色）
    print(f"{gray}╭{'─' * (input_box_width - 2)}╮{Style.RESET_ALL}")

    # 输入框内容行 - 空的，没有占位符
    print(f"{gray}│{' ' * (input_box_width - 2)}│{Style.RESET_ALL}")

    # 输入框底部边框（圆角，灰色）
    print(f"{gray}╰{'─' * (input_box_width - 2)}╯{Style.RESET_ALL}")

    # 保存当前光标位置（作为输入框左上角参考点）
    # 放在输入框之后，以便正确定位到输入位置
    print('\033[s', end='', flush=True)

def position_cursor_for_input():
    """恢复到输入框起点，再相对移动到内容行内的提示符位置"""
    # 恢复到 print_input_box 保存的位置（输入框左上角）
    print('\033[u', end='', flush=True)
    # 上移2行到内容行，右移2列到竖线内侧（为'>'符号留出空间）
    print('\033[2A\033[2C', end='', flush=True)
