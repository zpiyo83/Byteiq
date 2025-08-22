"""
输入处理模块
"""

import os
import re
from colorama import Fore, Style
from .commands import filter_commands

# 由于输入逻辑已简化，不再需要实时输入库
WINDOWS = None

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



def get_input_with_claude_style():
    """
    一个简化的、可靠的输入函数，取代了复杂的实时处理。
    直接使用Python的input()，并显示一个简单的提示符。
    """
    try:
        # 直接使用标准input，这是最可靠的方式
        return input(f"\n{Fore.GREEN}>>> {Style.RESET_ALL}")
    except (EOFError, KeyboardInterrupt):
        # 优雅地处理Ctrl+D或Ctrl+C
        print() # 确保在新的一行退出
        return "/exit"

def get_input_in_box():
    """在输入框内获取用户输入"""
    # 直接调用简化的、可靠的输入函数
    return get_input_with_claude_style()
