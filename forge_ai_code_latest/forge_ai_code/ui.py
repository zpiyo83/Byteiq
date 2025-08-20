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

    # 获取当前工作目录
    current_dir = os.getcwd()

    # 淡蓝色主题颜色
    light_blue = Fore.LIGHTCYAN_EX
    blue = Fore.CYAN
    white = Fore.WHITE

    # 先打印ASCII艺术字标题
    ascii_art = get_forge_ai_ascii()
    for line in ascii_art:
        print(f"{light_blue}{line}{Style.RESET_ALL}")

    print()

    # 打印带边框的欢迎信息框
    box_width = 50

    # 获取图标
    icon = get_wave_icon()

    # 顶部边框（圆角）
    print(f"{light_blue}╭{'─' * (box_width - 2)}╮{Style.RESET_ALL}")

    # 图标和欢迎信息行
    print(f"{light_blue}│{Style.RESET_ALL}{light_blue}{icon[0]}{Style.RESET_ALL} {white}Welcome to Forge AI Code!{' ' * (box_width - len(icon[0]) - 26)}{light_blue}│{Style.RESET_ALL}")

    # 空行
    print(f"{light_blue}│{' ' * (box_width - 2)}│{Style.RESET_ALL}")

    # 帮助信息行
    help_text = "/help for help, /status for your current setup"
    print(f"{light_blue}│{Style.RESET_ALL} {blue}{help_text}{' ' * (box_width - len(help_text) - 3)}{Style.RESET_ALL}{light_blue}│{Style.RESET_ALL}")

    # 空行
    print(f"{light_blue}│{' ' * (box_width - 2)}│{Style.RESET_ALL}")

    # 当前目录行
    cwd_text = f"cwd: {current_dir}"
    if len(cwd_text) > box_width - 3:
        cwd_text = f"cwd: ...{current_dir[-(box_width - 10):]}"
    print(f"{light_blue}│{Style.RESET_ALL} {white}{cwd_text}{' ' * (box_width - len(cwd_text) - 3)}{Style.RESET_ALL}{light_blue}│{Style.RESET_ALL}")

    # 空行
    print(f"{light_blue}│{' ' * (box_width - 2)}│{Style.RESET_ALL}")

    # 当前模式行
    mode_text = f"Mode: {mode_manager.get_current_mode()} (Alt+L to switch)"
    print(f"{light_blue}│{Style.RESET_ALL} {Fore.YELLOW}{mode_text}{' ' * (box_width - len(mode_text) - 3)}{Style.RESET_ALL}{light_blue}│{Style.RESET_ALL}")

    # 底部边框（圆角）
    print(f"{light_blue}╰{'─' * (box_width - 2)}╯{Style.RESET_ALL}")
    print()

    # 显示输入框
    print_input_box()

def print_input_box():
    """打印输入框，并保存起始光标位置以便后续精确定位"""
    gray = Fore.LIGHTBLACK_EX  # 灰色

    # 保存当前光标位置（作为输入框左上角参考点）
    print('\033[s', end='', flush=True)

    # 输入框宽度 - 增加长度以匹配图片要求
    input_box_width = 110

    # 输入框顶部边框（圆角，灰色）
    print(f"{gray}╭{'─' * (input_box_width - 2)}╮{Style.RESET_ALL}")

    # 输入框内容行 - 空的，没有占位符
    print(f"{gray}│{' ' * (input_box_width - 2)}│{Style.RESET_ALL}")

    # 输入框底部边框（圆角，灰色）
    print(f"{gray}╰{'─' * (input_box_width - 2)}╯{Style.RESET_ALL}")

    # Ask 提示文字（灰色）
    print(f"{gray}? Ask{Style.RESET_ALL}")

def position_cursor_for_input():
    """恢复到输入框起点，再相对移动到内容行内的提示符位置"""
    # 恢复到 print_input_box 保存的位置（输入框左上角）
    print('\033[u', end='', flush=True)
    # 下移1行到内容行，右移2列到竖线内侧
    print('\033[1B\033[2C', end='', flush=True)
