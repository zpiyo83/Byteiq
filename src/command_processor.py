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
from .output_monitor import start_output_monitoring, stop_output_monitoring, enable_print_monitoring

def process_ai_conversation(user_input):
    """处理AI对话"""
    # 检查是否配置了API密钥
    config = load_config()
    if not config.get('api_key'):
        print(f"{Fore.RED}错误：请先设置API密钥。使用 /s 命令进入设置。{Style.RESET_ALL}")
        return

    print(f"{Fore.CYAN}🤖 AI助手正在处理您的请求...{Style.RESET_ALL}")

    # 启用输出监控
    enable_print_monitoring()

    # 自动恢复标志和计数器
    auto_recovery_triggered = False
    recovery_count = 0
    max_recoveries = 3

    def on_output_timeout():
        """输出超时时的自动恢复回调"""
        nonlocal auto_recovery_triggered, recovery_count
        if recovery_count < max_recoveries:
            recovery_count += 1
            auto_recovery_triggered = True
            print(f"{Fore.YELLOW}🔄 自动恢复 ({recovery_count}/{max_recoveries})...{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}⚠️ 已达到最大恢复次数 ({max_recoveries})，停止自动恢复{Style.RESET_ALL}")
            stop_output_monitoring()

    # 发送消息给AI（使用非阻塞方法）
    ai_response = ai_client.send_message_non_blocking(user_input)

    # 处理AI响应和工具调用，添加循环计数器防止无限循环
    max_iterations = 20  # 最大迭代次数
    iteration_count = 0

    try:
        # 启动输出监控
        start_output_monitoring(on_output_timeout, timeout_seconds=15)

        while iteration_count < max_iterations:
            iteration_count += 1

            # 检查是否触发了自动恢复
            if auto_recovery_triggered:
                print(f"{Fore.YELLOW}🔄 执行自动恢复 ({recovery_count}/{max_recoveries})...{Style.RESET_ALL}")

                # 根据恢复次数选择不同的恢复策略
                if recovery_count == 1:
                    recovery_message = "检测到可能的卡死情况。请继续完成当前任务，如果遇到问题请分析并解决。"
                elif recovery_count == 2:
                    recovery_message = "再次检测到无响应。请检查当前状态，如果有错误请修复，然后继续任务。"
                else:
                    recovery_message = "多次检测到无响应。请总结当前进度，如果任务已完成请使用task_complete结束。"

                ai_response = ai_client.send_message_non_blocking(recovery_message, include_structure=False)
                auto_recovery_triggered = False

                # 如果恢复失败，停止处理
                if not ai_response or any(error_keyword in ai_response.lower() for error_keyword in
                                        ['超时', 'timeout', '网络错误', '发生错误']):
                    print(f"{Fore.RED}⚠️ 自动恢复失败，停止处理{Style.RESET_ALL}")
                    break

            result = ai_tool_processor.process_response(ai_response)

            # 显示AI的意图（过滤XML）
            if result['display_text'].strip():
                print(f"\n{Fore.GREEN}🤖 AI: {result['display_text']}{Style.RESET_ALL}")

            # 如果有工具调用，显示结果
            if result['has_tool'] and result['tool_result']:
                print(f"{Fore.YELLOW}📋 执行结果: {result['tool_result']}{Style.RESET_ALL}")

            # 如果需要继续（有工具调用且未完成），继续对话
            if result['should_continue']:
                print(f"\n{Fore.CYAN}🤖 AI继续处理... (步骤 {iteration_count}/{max_iterations}){Style.RESET_ALL}")

                # 构建更详细的反馈信息给AI
                feedback_message = f"工具执行结果: {result['tool_result']}"

                # 如果是错误结果，添加更多上下文
                if result['tool_result'] and any(error_keyword in result['tool_result'].lower() for error_keyword in
                                               ['失败', '错误', 'error', 'failed', '异常', 'exception']):
                    feedback_message += "\n\n请分析错误原因并尝试修复。"

                # 将工具执行结果发送回AI（使用非阻塞方法）
                ai_response = ai_client.send_message_non_blocking(feedback_message, include_structure=False)

                # 检查AI响应是否为错误信息（可能是网络问题或超时）
                if ai_response and any(error_keyword in ai_response.lower() for error_keyword in
                                     ['超时', 'timeout', '网络错误', '发生错误', '任务已被用户中断']):
                    print(f"\n{Fore.RED}⚠️ AI处理出现问题: {ai_response}{Style.RESET_ALL}")
                    break
            else:
                break

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ 用户中断了处理流程{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}⚠️ 处理过程中出现异常: {str(e)}{Style.RESET_ALL}")
    finally:
        # 确保停止输出监控
        try:
            stop_output_monitoring()
        except:
            pass

    # 如果达到最大迭代次数，给出提示
    if iteration_count >= max_iterations:
        print(f"\n{Fore.YELLOW}⚠️ 已达到最大处理步骤数 ({max_iterations})，任务可能需要手动干预。{Style.RESET_ALL}")

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
        return True

    # 检查模式切换命令
    if mode_manager.handle_mode_switch_command(user_input):
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

    # 在每个命令执行后打印空行分隔
    print()
    return True
