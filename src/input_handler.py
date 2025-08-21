"""
输入处理模块
"""

import os
import shutil
import re
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

def get_visible_length(text):
    """计算去除ANSI转义序列后的字符串显示长度"""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return len(ansi_escape.sub('', text))

def get_input_with_suggestions():
    """带建议的输入函数（简化版）"""
    position_cursor_for_input()
    print("> ", end="", flush=True)
    
    try:
        user_input = input()
    except EOFError:
        return ""
    
    # 如果输入以 / 开头且不完整，显示建议
    if user_input.startswith('/') and len(user_input) > 1:
        matching_commands = filter_commands(user_input)
        if matching_commands and user_input != matching_commands[0][0]:
            show_command_suggestions(user_input)
            # 重新获取输入
            position_cursor_for_input()
            print("> ", end="", flush=True)
            try:
                return input()
            except EOFError:
                return ""
    
    return user_input

def get_input_with_claude_style():
    """Claude风格的输入处理（高级版）"""
    position_cursor_for_input()
    print("> ", end="", flush=True)
    
    if WINDOWS is None:
        # 不支持实时输入，回退到简单模式
        try:
            return input()
        except EOFError:
            return ""
    
    user_input = ""
    suggestion_shown = False
    current_line_length = 0  # 当前行可见字符长度
    
    try:
        while True:
            # 动态获取终端宽度
            term_width = shutil.get_terminal_size().columns
            available_width = term_width - 4  # 保留左右边距各2列
            
            if WINDOWS:
                if msvcrt.kbhit():
                    char = msvcrt.getch()
                    if char == b'\r':  # Enter
                        print()
                        break
                    elif char == b'\x08':  # Backspace
                        if user_input:
                            last_char = user_input[-1]
                            char_length = get_visible_length(last_char)
                            user_input = user_input[:-1]
                            
                            # 重新绘制输入行
                            term_width = shutil.get_terminal_size().columns
                            input_box_width = term_width - 4
                            visible_input = user_input
                            if get_visible_length(user_input) > (input_box_width - 4):
                                visible_start = 0
                                current_length = 0
                                for i, c in enumerate(user_input):
                                    c_len = get_visible_length(c)
                                    if current_length + c_len > (input_box_width - 4):
                                        visible_start = i
                                        break
                                    current_length += c_len
                                visible_input = user_input[visible_start:]
                            position_cursor_for_input()
                            padding = input_box_width - 4 - get_visible_length(visible_input)
                            if padding < 0:
                                padding = 0
                            print("> " + visible_input + " " * padding, end='', flush=True)
                            print('\r> ' + visible_input, end='', flush=True)
                            current_line_length = get_visible_length(visible_input)
                            suggestion_shown = False
                    elif char == b'\x1b':  # ESC
                        continue
                    else:
                        try:
                            char_str = char.decode('utf-8')
                            char_length = get_visible_length(char_str)
                            
                            user_input += char_str
                            
                            # 重新绘制输入行，实现滚动显示
                            term_width = shutil.get_terminal_size().columns
                            input_box_width = term_width - 4  # 输入框内容区域宽度
                            visible_input = user_input
                            if get_visible_length(user_input) > (input_box_width - 4):
                                # 计算可见起始位置（考虑提示符占位）
                                visible_start = 0
                                current_length = 0
                                for i, c in enumerate(user_input):
                                    c_len = get_visible_length(c)
                                    if current_length + c_len > (input_box_width - 4):
                                        visible_start = i
                                        break
                                    current_length += c_len
                                visible_input = user_input[visible_start:]
                            
                            # 重新定位光标并绘制
                            position_cursor_for_input()
                            # 计算正确填充空格数量（考虑提示符占位）
                            padding = input_box_width - 4 - get_visible_length(visible_input)
                            if padding < 0:
                                padding = 0
                            print("> " + visible_input + " " * padding, end='', flush=True)
                            # 将光标移回正确位置
                            print('\r> ' + visible_input, end='', flush=True)
                            current_line_length = get_visible_length(visible_input)
                            
                            # 检查是否需要显示建议
                            if user_input.startswith('/') and len(user_input) > 1 and not suggestion_shown:
                                matching_commands = filter_commands(user_input)
                                if matching_commands and user_input != matching_commands[0][0]:
                                    show_command_suggestions(user_input)
                                    suggestion_shown = True
                        except UnicodeDecodeError:
                            continue
            else:
                try:
                    return input()
                except EOFError:
                    return ""
                
    except KeyboardInterrupt:
        print()
        return ""
    except Exception as e:
        print(f"Input error: {str(e)}")
        try:
            return input()
        except EOFError:
            return ""
    
    return user_input

def get_input_in_box():
    """在输入框内获取用户输入"""
    try:
        # 尝试使用Claude风格输入
        return get_input_with_claude_style()
    except:
        # 如果失败，回退到简单建议
        return get_input_with_suggestions()
