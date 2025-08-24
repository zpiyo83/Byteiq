"""
输入处理模块
"""


import re
from colorama import Fore, Style
from .commands import filter_commands
from .modes import mode_manager

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import ANSI
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
    使用 prompt_toolkit 实现 Shift+Enter 换行, Enter 发送。
    """
    kb = KeyBindings()

    @kb.add('enter')
    def _(event):
        """ Enter键：提交输入 """
        event.app.exit(result=event.app.current_buffer.text)

    @kb.add('c-j')
    def _(event):
        """ Ctrl+J (Ctrl+Enter) 键：插入换行符 """
        event.app.current_buffer.insert_text('\n')

    @kb.add('c-l')
    def _(event):
        """ Ctrl+L: 切换模式 """
        event.app.exit(result="/mode")

    session = PromptSession(key_bindings=kb)
    prompt_text = ANSI(f"\n{Fore.GREEN}>>> {Style.RESET_ALL}")

    print(f"{Fore.CYAN}提示：按 Enter 发送，Ctrl+J (Ctrl+Enter) 换行。{Style.RESET_ALL}")

    try:
        text = session.prompt(prompt_text)
        return text
    except (EOFError, KeyboardInterrupt):
        print() # 确保在新的一行退出
        return "/exit"

def get_input_in_box():
    """在输入框内获取用户输入"""
    # 直接调用简化的、可靠的输入函数
    return get_input_with_claude_style()
