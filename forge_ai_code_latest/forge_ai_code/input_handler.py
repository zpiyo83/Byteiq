"""
输入处理模块
"""

import os
from colorama import Fore, Style
from .ui import position_cursor_for_input
from .commands import filter_commands

# 尝试导入实时输入相关的库
try:
    import msvcrt  # Windows
    WINDOWS = True
except ImportError:
    try:
        import termios
        import tty
        import select
        WINDOWS = False
    except ImportError:
        WINDOWS = None  # 不支持实时输入

def show_command_suggestions(partial_input):
    """显示命令建议"""
    if not partial_input.startswith('/'):
        return
    
    matching_commands = filter_commands(partial_input)
    if not matching_commands:
        return
    
    # 显示第一个匹配的命令作为主要建议
    main_cmd, main_desc = matching_commands[0]
    print(f"\n{Fore.YELLOW}💡 建议: {main_cmd} - {main_desc}{Style.RESET_ALL}")
    
    # 如果有多个匹配，显示其他选项
    if len(matching_commands) > 1:
        other_cmds = [cmd for cmd, _ in matching_commands[1:]]
        print(f"   其他选项: {', '.join(other_cmds)}")
    
    print(f"\n按Enter使用建议，或输入其他命令:")

def get_input_with_suggestions():
    """带建议的输入函数（简化版）"""
    position_cursor_for_input()
    print("> ", end="", flush=True)
    
    user_input = input()
    
    # 如果输入以 / 开头且不完整，显示建议
    if user_input.startswith('/') and len(user_input) > 1:
        matching_commands = filter_commands(user_input)
        if matching_commands and user_input != matching_commands[0][0]:
            show_command_suggestions(user_input)
            # 重新获取输入
            position_cursor_for_input()
            print("> ", end="", flush=True)
            return input()
    
    return user_input

def get_input_with_claude_style():
    """Claude风格的输入处理（高级版）"""
    position_cursor_for_input()
    print("> ", end="", flush=True)
    
    if WINDOWS is None:
        # 不支持实时输入，回退到简单模式
        return input()
    
    user_input = ""
    suggestion_shown = False
    
    try:
        while True:
            if WINDOWS:
                # Windows实现
                if msvcrt.kbhit():
                    char = msvcrt.getch()
                    if char == b'\r':  # Enter键
                        print()  # 换行
                        break
                    elif char == b'\x08':  # Backspace键
                        if user_input:
                            user_input = user_input[:-1]
                            print('\b \b', end='', flush=True)
                            suggestion_shown = False
                    elif char == b'\x1b':  # ESC键，跳过特殊键序列
                        continue
                    else:
                        try:
                            char_str = char.decode('utf-8')
                            user_input += char_str
                            print(char_str, end='', flush=True)
                            
                            # 检查是否需要显示建议
                            if user_input.startswith('/') and len(user_input) > 1 and not suggestion_shown:
                                matching_commands = filter_commands(user_input)
                                if matching_commands and user_input != matching_commands[0][0]:
                                    show_command_suggestions(user_input)
                                    suggestion_shown = True
                        except UnicodeDecodeError:
                            continue
            else:
                # Linux/Mac实现（简化）
                return input()
                
    except KeyboardInterrupt:
        print()
        return ""
    except:
        # 出错时回退到简单输入
        return input()
    
    return user_input

def get_input_in_box():
    """在输入框内获取用户输入"""
    try:
        # 尝试使用Claude风格输入
        return get_input_with_claude_style()
    except:
        # 如果失败，回退到简单建议
        return get_input_with_suggestions()
