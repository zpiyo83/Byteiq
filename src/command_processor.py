"""
命令处理模块
"""

import os
from colorama import Fore, Style
from .commands import show_help, show_status, handle_todo_command, show_todos
from .config import show_settings, load_config
from .modes import mode_manager, hacpp_mode
from .hacpp_client import hacpp_client
from .ui import print_welcome_screen
from .ai_client import ai_client
from .ai_tools import ai_tool_processor
from .output_monitor import start_output_monitoring, stop_output_monitoring, enable_print_monitoring
from .debug_session import debug_session

def process_ai_conversation(user_input):
    """处理AI对话，包含继承计划逻辑"""
    import re
    original_user_input = user_input
    config = load_config()
    if not config.get('api_key'):
        print(f"{Fore.RED}错误：请先设置API密钥。使用 /s 命令进入设置。{Style.RESET_ALL}")
        return

    if hacpp_mode.is_hacpp_active() and hacpp_mode.phase == "researching":
        print(f"{Fore.MAGENTA}🚀 HACPP模式启动 - 研究员分析阶段...{Style.RESET_ALL}")
        project_info = hacpp_client._get_project_structure()
        user_input = f"""
用户需求: {user_input}
当前项目结构:
{project_info}
请分析此需求并制定详细计划。使用 `read_file` 和 `code_search` 收集信息。完成后，**必须调用 `<task_complete>` 工具**来移交计划。
"""

    print(f"{Fore.CYAN}AI助手正在处理您的请求...{Style.RESET_ALL}")
    enable_print_monitoring()

    max_iterations = 50
    iteration_count = 0
    next_message_to_ai = user_input
    inherited_plan = None
    original_request_reminder = f"[原始用户需求提醒] {user_input}" if user_input else ""

    try:
        start_output_monitoring(timeout_seconds=15)

        while iteration_count < max_iterations:
            iteration_count += 1

            # 在每次迭代中提醒AI原始需求
            if iteration_count > 1 and original_request_reminder:
                print(f"{Fore.BLUE}📋 原始需求提醒: {user_input[:50]}...{Style.RESET_ALL}")

            if inherited_plan:
                print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}🧬 继承计划 (第 {iteration_count} 步){Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}先前完成: {inherited_plan['completed']}{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}下一步计划: {inherited_plan['next']}{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
                
                message_with_plan = f"""
[Inherited Plan - STEP {iteration_count}]
My previous action was: {inherited_plan['completed']}
My mandatory next step is: {inherited_plan['next']}

[Your New Task]
{next_message_to_ai}

[Original User Request Reminder - DO NOT FORGET]
{original_request_reminder}

[IMPORTANT INSTRUCTIONS]
1. Execute the inherited plan as your top priority
2. Do not forget the original user request
3. After completing this step, use the <plan> tool to define your next step
4. Only use <task_complete> when the entire original task is finished
"""
                next_message_to_ai = message_with_plan
                inherited_plan = None

            model_to_use = hacpp_mode.cheap_model if hacpp_mode.is_hacpp_active() and hacpp_mode.phase == "researching" else None
            ai_response_text = ai_client.send_message_streaming(next_message_to_ai, model_override=model_to_use)

            if not ai_response_text or any(keyword in ai_response_text.lower() for keyword in ['error', 'timeout', '任务已被用户中断']):
                print(f"\n{Fore.RED}⚠️ AI 错误: {ai_response_text}{Style.RESET_ALL}")
                break

            result = ai_tool_processor.process_response(ai_response_text)

            if result.get('has_tool') and result.get('tool_result'):
                tool_output = result.get('tool_result')
                if tool_output and "PLAN::COMPLETED:" in tool_output:
                    plan_part_list = [res for res in tool_output.split('\n') if res.startswith("PLAN::")]
                    if plan_part_list:
                        plan_part = plan_part_list[0]
                        # 更新正则表达式以适应新的计划格式（包含时间戳）
                        completed_match = re.search(r"COMPLETED:(.*?)::NEXT:", plan_part)
                        next_match = re.search(r"::NEXT:(.*)", plan_part)
                        if completed_match and next_match:
                            inherited_plan = {"completed": completed_match.group(1).strip(), "next": next_match.group(1).strip()}
                            clean_tool_result = "\n".join([res for res in tool_output.split('\n') if not res.startswith("PLAN::")])
                            result['tool_result'] = clean_tool_result.strip()

            if hacpp_mode.is_hacpp_active() and result.get('is_handover'):
                print(f"\n{Fore.MAGENTA}HACPP 交接：研究员分析完成，执行者接管...{Style.RESET_ALL}")
                hacpp_mode.phase = "executing"
                summary = result.get('summary', '没有提供总结。')
                next_message_to_ai = f"[HACPP模式交接]\n研究员的计划: {summary}\n原始用户需求: {original_user_input}\n作为执行者AI，请开始执行此计划。"
                ai_client.clear_history()
                continue

            if result.get('display_text') and result['display_text'].strip():
                print(f"\n{Fore.GREEN}AI: {result['display_text']}{Style.RESET_ALL}")
                
                # 显示原始需求提醒（如果有的话）
                if iteration_count > 1 and original_request_reminder:
                    print(f"{Fore.BLUE}📋 原始需求提醒: {user_input[:80]}...{Style.RESET_ALL}")
            
            if result.get('has_tool') and result.get('tool_result'):
                if not (hacpp_mode.is_hacpp_active() and hacpp_mode.phase == "researching"):
                    tool_result_text = result.get('tool_result', '')
                    executed_tools = result.get('executed_tools', [])

                    # 仅当不是成功的execute_command时才打印结果，以避免重复
                    is_successful_command = 'execute_command' in executed_tools and "命令执行成功" in tool_result_text
                    if not is_successful_command:
                        print(f"{Fore.YELLOW}📋 结果: {tool_result_text}{Style.RESET_ALL}")
                        
                        # 显示原始需求提醒（如果有的话）
                        if iteration_count > 1 and original_request_reminder:
                            print(f"{Fore.BLUE}📋 原始需求提醒: {user_input[:80]}...{Style.RESET_ALL}")

            if result.get('should_continue'):
                print(f"\n{Fore.CYAN}AI 继续处理... (步骤 {iteration_count}/{max_iterations}){Style.RESET_ALL}")
                next_message_to_ai = f"工具执行结果: {result['tool_result']}"
            else:
                break

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ 用户中断了处理流程{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}⚠️ 处理过程中出现异常: {str(e)}{Style.RESET_ALL}")
    finally:
        try:
            stop_output_monitoring()
        except:
            pass

    if iteration_count >= max_iterations:
        print(f"\n{Fore.YELLOW}⚠️ 已达到最大处理步骤数 ({max_iterations})，任务可能需要手动干预。{Style.RESET_ALL}")

def handle_fix_command(command_parts):
    """处理/fix命令 - AI辅助调试"""
    if len(command_parts) == 1:
        # 只输入了 /fix，显示帮助
        print(f"{Fore.CYAN}AI辅助调试命令帮助:{Style.RESET_ALL}")
        print(f"  /fix bug <描述>     - 开始AI辅助调试会话")
        print(f"  /fix status         - 查看当前调试会话状态")
        print(f"  /fix end           - 结束当前调试会话")
        print(f"\n{Fore.YELLOW}示例:{Style.RESET_ALL}")
        print(f"  /fix bug 程序启动时出现模块导入错误")
        return

    subcommand = command_parts[1].lower()
    
    if subcommand == 'bug':
        # /fix bug 命令 - 开始调试会话
        if len(command_parts) < 3:
            print(f"{Fore.RED}错误：请提供bug描述{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}用法: /fix bug <bug描述>{Style.RESET_ALL}")
            return
        
        # 检查是否已有活动会话
        if debug_session.is_active:
            print(f"{Fore.YELLOW}⚠️ 已有活动的调试会话，请先结束当前会话{Style.RESET_ALL}")
            print(debug_session.get_session_status())
            return
        
        # 获取bug描述
        bug_description = ' '.join(command_parts[2:])
        
        # 询问引导者AI模型
        print(f"{Fore.CYAN}请输入引导者AI模型名称:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}建议使用: gpt-4, claude-3-sonnet, gpt-3.5-turbo 等{Style.RESET_ALL}")
        guide_model = input(f"{Fore.YELLOW}引导者AI模型: {Style.RESET_ALL}").strip()
        
        if not guide_model:
            print(f"{Fore.RED}错误：引导者AI模型名称不能为空{Style.RESET_ALL}")
            return
        
        # 开始调试会话
        print(f"\n{Fore.CYAN}正在启动AI辅助调试会话...{Style.RESET_ALL}")
        success = debug_session.start_session(bug_description, guide_model)
        
        if not success:
            print(f"{Fore.RED}❌ 调试会话启动失败{Style.RESET_ALL}")
    
    elif subcommand == 'status':
        # /fix status 命令 - 显示调试会话状态
        status = debug_session.get_session_status()
        print(f"{Fore.CYAN}调试会话状态:{Style.RESET_ALL}")
        print(status)
    
    elif subcommand == 'end':
        # /fix end 命令 - 结束调试会话
        if debug_session.is_active:
            debug_session.end_session()
            print(f"{Fore.GREEN}✓ 调试会话已结束{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}没有活动的调试会话{Style.RESET_ALL}")
    
    else:
        print(f"{Fore.RED}未知的fix子命令: {subcommand}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}可用命令: bug, status, end{Style.RESET_ALL}")

def handle_hacpp_command(command_parts):
    """处理HACPP模式命令"""
    if len(command_parts) == 1:
        # 只输入了 /HACPP，要求输入测试码
        test_code = input(f"{Fore.YELLOW}请输入测试码: {Style.RESET_ALL}").strip()

        if hacpp_mode.activate(test_code):
            print(f"{Fore.GREEN}✓ HACPP模式已激活{Style.RESET_ALL}")
            print(f"{Fore.CYAN}现在可以使用 /HACPP model 设置便宜模型{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ 测试码错误{Style.RESET_ALL}")

    elif len(command_parts) == 2 and command_parts[1].lower() == 'model':
        # /HACPP model 命令
        if not hacpp_mode.is_active:
            print(f"{Fore.RED}错误：请先激活HACPP模式{Style.RESET_ALL}")
            return

        model_name = input(f"{Fore.YELLOW}请输入便宜模型名称: {Style.RESET_ALL}").strip()

        if model_name:
            hacpp_mode.set_cheap_model(model_name)
            print(f"{Fore.GREEN}✓ 便宜模型已设置: {model_name}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}HACPP模式已完全激活，可以开始双AI协作{Style.RESET_ALL}")

            # 显示当前配置
            config = load_config()
            expensive_model = config.get('model', '未设置')
            print(f"{Fore.WHITE}当前配置:{Style.RESET_ALL}")
            print(f"  便宜AI模型: {Fore.YELLOW}{model_name}{Style.RESET_ALL}")
            print(f"  贵AI模型: {Fore.MAGENTA}{expensive_model}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}模型名称不能为空{Style.RESET_ALL}")

    elif len(command_parts) == 2 and command_parts[1].lower() == 'off':
        # /HACPP off 命令 - 关闭HACPP模式
        hacpp_mode.deactivate()
        print(f"{Fore.YELLOW}HACPP模式已关闭{Style.RESET_ALL}")

    elif len(command_parts) == 2 and command_parts[1].lower() == 'status':
        # /HACPP status 命令 - 显示状态
        if hacpp_mode.is_hacpp_active():
            config = load_config()
            expensive_model = config.get('model', '未设置')
            print(f"{Fore.GREEN}HACPP模式状态: 激活{Style.RESET_ALL}")
            print(f"  便宜AI模型: {Fore.YELLOW}{hacpp_mode.cheap_model}{Style.RESET_ALL}")
            print(f"  贵AI模型: {Fore.MAGENTA}{expensive_model}{Style.RESET_ALL}")
        elif hacpp_mode.is_active:
            print(f"{Fore.YELLOW}HACPP模式状态: 已认证，但未设置便宜模型{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}HACPP模式状态: 未激活{Style.RESET_ALL}")

    else:
        # 显示帮助信息
        print(f"{Fore.CYAN}HACPP模式命令帮助:{Style.RESET_ALL}")
        print(f"  /HACPP        - 激活HACPP模式（需要测试码）")
        print(f"  /HACPP model  - 设置便宜模型")
        print(f"  /HACPP status - 显示HACPP模式状态")
        print(f"  /HACPP off    - 关闭HACPP模式")
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
        print(f"{Fore.LIGHTCYAN_EX}再见！感谢使用 ByteIQ!{Style.RESET_ALL}")
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

    # HACPP模式命令
    elif command == '/hacpp':
        handle_hacpp_command(command_parts)

    # AI辅助调试命令
    elif command == '/fix':
        handle_fix_command(command_parts)

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
