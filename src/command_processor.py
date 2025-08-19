"""
命令处理模块
"""

import os
from colorama import Fore, Style
from .commands import show_help, show_status, handle_todo_command, show_todos
from .config import show_settings, load_config
from .modes import mode_manager
from .ui import print_welcome_screen, print_input_box
from .ai_client import ai_client
from .ai_tools import ai_tool_processor

def process_ai_conversation(user_input):
    """处理AI对话"""
    # 检查是否配置了API密钥
    config = load_config()
    if not config.get('api_key'):
        print(f"{Fore.RED}错误：请先设置API密钥。使用 /s 命令进入设置。{Style.RESET_ALL}")
        return

    print(f"{Fore.CYAN}🤖 AI助手正在处理您的请求...{Style.RESET_ALL}")

    # 发送消息给AI
    ai_response = ai_client.send_message(user_input)

    # 处理AI响应和工具调用
    while True:
        result = ai_tool_processor.process_response(ai_response)

        # 显示AI的意图（过滤XML）
        if result['display_text'].strip():
            print(f"\n{Fore.GREEN}🤖 AI: {result['display_text']}{Style.RESET_ALL}")

        # 如果有工具调用，显示结果
        if result['has_tool'] and result['tool_result']:
            print(f"{Fore.YELLOW}📋 执行结果: {result['tool_result']}{Style.RESET_ALL}")

        # 如果需要继续（有工具调用且未完成），继续对话
        if result['should_continue']:
            print(f"\n{Fore.CYAN}🤖 AI继续处理...{Style.RESET_ALL}")
            # 将工具执行结果发送回AI
            ai_response = ai_client.send_message(f"工具执行结果: {result['tool_result']}", include_structure=False)
        else:
            break

    print()  # 空行分隔

def process_command(user_input):
    """处理用户命令

    Returns:
        bool: True 表示继续运行，False 表示退出程序
    """
    # 过滤掉特殊字符
    user_input = user_input.replace('\n', '').replace('\r', '').strip()
    if not user_input:
        return True

    # 检查是否是命令（以/开头）
    if not user_input.startswith('/'):
        # 不是命令，发送给AI处理
        process_ai_conversation(user_input)
        print_input_box()
        return True

    # 检查模式切换命令
    if mode_manager.handle_mode_switch_command(user_input):
        # 重新显示输入框
        print_input_box()
        return True

    command_parts = user_input.split()
    command = command_parts[0].lower()

    # 退出命令
    if command in ['/exit', '/quit']:
        print(f"{Fore.LIGHTCYAN_EX}再见！感谢使用 Forge AI Code!{Style.RESET_ALL}")
        return False

    # 帮助命令
    elif command == '/help':
        show_help()

    # 状态命令
    elif command == '/status':
        show_status()

    # 设置命令
    elif command == '/s':
        show_settings()

    # AI相关命令
    elif command == '/clear-history':
        ai_client.clear_history()
        print(f"{Fore.GREEN}✓ AI对话历史已清除{Style.RESET_ALL}")

    # TODO相关命令
    elif command == '/todo':
        handle_todo_command()

    elif command == '/todos':
        show_todos()

    # 清屏命令
    elif command == '/clear':
        print_welcome_screen()
        return True  # 跳过重新显示输入框，因为print_welcome_screen已经包含了

    # 目录相关命令
    elif command == '/pwd':
        print(f"{Fore.CYAN}{os.getcwd()}{Style.RESET_ALL}")

    elif command == '/ls':
        try:
            files = os.listdir('.')
            for file in sorted(files):
                if os.path.isdir(file):
                    print(f"{Fore.LIGHTCYAN_EX}{file}/{Style.RESET_ALL}")
                else:
                    print(f"{Fore.WHITE}{file}{Style.RESET_ALL}")
        except PermissionError:
            print(f"{Fore.RED}权限错误：无法访问当前目录{Style.RESET_ALL}")

    elif command == '/cd':
        if len(command_parts) > 1:
            try:
                os.chdir(command_parts[1])
                print(f"{Fore.CYAN}已切换到: {os.getcwd()}{Style.RESET_ALL}")
            except FileNotFoundError:
                print(f"{Fore.RED}错误：目录 '{command_parts[1]}' 不存在{Style.RESET_ALL}")
            except PermissionError:
                print(f"{Fore.RED}权限错误：无法访问目录 '{command_parts[1]}'{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}用法: /cd <目录名>{Style.RESET_ALL}")
    
    # 未知命令
    else:
        print(f"{Fore.RED}未知命令: {command}. 输入 '/help' 或 'help' 查看可用命令{Style.RESET_ALL}")

    # 在每个命令执行后重新显示输入框
    print()
    print_input_box()
    return True
