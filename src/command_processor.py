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
from .project_doc_analyzer import project_doc_analyzer
from .context_manager import context_manager

# 在主AI系统提示词中添加项目分析文档提示
def get_project_analysis_context():
    """获取项目分析文档上下文提示"""
    import os
    
    current_dir = os.getcwd()
    project_name = os.path.basename(current_dir)
    docs_folder = os.path.join(current_dir, f"{project_name}_analysis_docs")
    
    if os.path.exists(docs_folder) and os.path.isdir(docs_folder):
        md_files = [f for f in os.listdir(docs_folder) if f.endswith('.md')]
        if md_files:
            return f"""

# 📁 项目分析文档可用
当前项目已有分析文档（{len(md_files)}个文件）位于: {docs_folder}
当用户咨询项目结构、函数、类或变量时，优先建议查看这些分析文档。
每个文件都有对应的.md文档，包含详细的函数、类、变量分析。
"""
    return ""

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

    # 检查是否有项目分析文档可用
    _check_and_suggest_analysis_docs()
    
    # 在AI系统提示词中添加项目分析上下文
    analysis_context = get_project_analysis_context()
    if analysis_context:
        user_input += analysis_context
    
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
            
            # 工具执行结果已在工具输出中显示，避免重复
            if result.get('has_tool') and result.get('tool_result'):
                if not (hacpp_mode.is_hacpp_active() and hacpp_mode.phase == "researching"):
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

def handle_init_command(command_parts):
    """处理/init命令 - 超大型项目分析模式"""
    if len(command_parts) == 1:
        # 只输入了 /init，显示帮助和启动选项
        print(f"{Fore.CYAN}超大型项目分析模式{Style.RESET_ALL}")
        print(f"{Fore.WHITE}功能: 分析项目中所有文件，生成完整的接口文档和变量文档{Style.RESET_ALL}")
        print()
        print(f"{Fore.CYAN}可用命令:{Style.RESET_ALL}")
        print(f"  /init start [路径]   - 开始分析项目（默认当前目录）")
        print(f"  /init status        - 查看分析状态")
        print(f"  /init stop          - 停止分析")
        print()
        
        # 检查当前状态
        status = project_doc_analyzer.get_status()
        if status['is_active']:
            print(f"{Fore.YELLOW}⚠️ 分析模式正在运行中{Style.RESET_ALL}")
            print(f"  项目路径: {status['project_path']}")
            print(f"  分析进度: {status['progress']}")
        else:
            print(f"{Fore.GREEN}💡 提示: 使用 '/init start' 开始分析当前目录{Style.RESET_ALL}")
        return

    subcommand = command_parts[1].lower()
    
    if subcommand == 'start':
        # /init start 命令 - 开始项目分析
        if project_doc_analyzer.is_active:
            print(f"{Fore.YELLOW}⚠️ 项目分析模式已在运行中{Style.RESET_ALL}")
            status = project_doc_analyzer.get_status()
            print(f"  项目路径: {status['project_path']}")
            print(f"  分析进度: {status['progress']}")
            return
        
        # 获取项目路径
        project_path = None
        if len(command_parts) > 2:
            project_path = command_parts[2]
        
        # 确认开始分析
        if not project_path:
            project_path = os.getcwd()
            
        print(f"{Fore.CYAN}准备分析项目: {project_path}{Style.RESET_ALL}")
        confirm = input(f"{Fore.YELLOW}确认开始分析？这可能需要较长时间 (y/N): {Style.RESET_ALL}").strip().lower()
        
        if confirm == 'y':
            print(f"\n{Fore.CYAN}正在启动超大型项目分析模式...{Style.RESET_ALL}")
            success = project_doc_analyzer.start_analysis(project_path)
            
            if not success:
                print(f"{Fore.RED}❌ 项目分析启动失败{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}已取消分析{Style.RESET_ALL}")
    
    elif subcommand == 'status':
        # /init status 命令 - 显示分析状态
        status = project_doc_analyzer.get_status()
        print(f"{Fore.CYAN}项目分析状态:{Style.RESET_ALL}")
        
        if status['is_active']:
            print(f"  状态: {Fore.GREEN}运行中{Style.RESET_ALL}")
            print(f"  项目路径: {status['project_path']}")
            print(f"  分析进度: {status['progress']}")
            print(f"  总文件数: {status['total_files']}")
            print(f"  已处理: {status['processed_files']}")
        else:
            print(f"  状态: {Fore.YELLOW}未运行{Style.RESET_ALL}")
    
    elif subcommand == 'stop':
        # /init stop 命令 - 停止分析
        if project_doc_analyzer.is_active:
            project_doc_analyzer.stop_analysis()
            print(f"{Fore.GREEN}✓ 项目分析已停止{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}没有正在运行的分析任务{Style.RESET_ALL}")
    
    else:
        print(f"{Fore.RED}未知的init命令: {subcommand}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}可用命令: start, status, stop{Style.RESET_ALL}")

def handle_context_command(command_parts):
    """处理/context命令 - 上下文管理"""
    if len(command_parts) == 1:
        # 只输入了 /context，显示状态
        stats = context_manager.get_context_stats()
        print(f"{Fore.CYAN}上下文状态:{Style.RESET_ALL}")
        print(f"  Token使用: {stats['total_tokens']:,} / {stats['max_tokens']:,} ({stats['utilization_percent']}%)")
        print(f"  对话消息: {stats['conversation_messages']}")
        print(f"  项目上下文: {stats['project_contexts']}")
        print(f"  代码上下文: {stats['code_contexts']}")
        print(f"  会话摘要: {'是' if stats['has_summary'] else '否'}")
        print()
        print(f"{Fore.CYAN}可用命令:{Style.RESET_ALL}")
        print(f"  /context set <tokens>   - 设置最大token数")
        print(f"  /context status         - 显示详细状态")
        print(f"  /context clear          - 清除所有上下文")
        print(f"  /context save [文件]    - 保存上下文到文件")
        print(f"  /context load [文件]    - 从文件加载上下文")
        return

    subcommand = command_parts[1].lower()
    
    if subcommand == 'set':
        # /context set <tokens> 命令
        if len(command_parts) < 3:
            print(f"{Fore.RED}请指定token数量，例如: /context set 20000{Style.RESET_ALL}")
            return
        
        try:
            max_tokens = int(command_parts[2])
            context_manager.set_max_tokens(max_tokens)
        except ValueError:
            print(f"{Fore.RED}无效的token数量: {command_parts[2]}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}设置失败: {str(e)}{Style.RESET_ALL}")
    
    elif subcommand == 'status':
        # /context status 命令 - 显示详细状态
        stats = context_manager.get_context_stats()
        print(f"{Fore.CYAN}详细上下文状态:{Style.RESET_ALL}")
        print(f"  最大Token数: {stats['max_tokens']:,}")
        print(f"  当前使用: {stats['total_tokens']:,}")
        print(f"  使用率: {stats['utilization_percent']}%")
        print(f"  对话消息数: {stats['conversation_messages']}")
        print(f"  项目上下文数: {stats['project_contexts']}")
        print(f"  代码上下文数: {stats['code_contexts']}")
        print(f"  有会话摘要: {'是' if stats['has_summary'] else '否'}")
        
        # 显示进度条
        bar_width = 40
        used_width = int((stats['utilization_percent'] / 100) * bar_width)
        bar = "█" * used_width + "░" * (bar_width - used_width)
        color = Fore.GREEN if stats['utilization_percent'] < 70 else Fore.YELLOW if stats['utilization_percent'] < 90 else Fore.RED
        print(f"  使用情况: {color}[{bar}] {stats['utilization_percent']}%{Style.RESET_ALL}")
    
    elif subcommand == 'clear':
        # /context clear 命令
        confirm = input(f"{Fore.YELLOW}确认清除所有上下文？(y/N): {Style.RESET_ALL}").strip().lower()
        if confirm == 'y':
            context_manager.clear_context()
        else:
            print(f"{Fore.YELLOW}已取消{Style.RESET_ALL}")
    
    elif subcommand == 'save':
        # /context save [文件] 命令
        filename = command_parts[2] if len(command_parts) > 2 else ".byteiq_context.json"
        context_manager.save_context(filename)
        print(f"{Fore.GREEN}✓ 上下文已保存到 {filename}{Style.RESET_ALL}")
    
    elif subcommand == 'load':
        # /context load [文件] 命令
        filename = command_parts[2] if len(command_parts) > 2 else ".byteiq_context.json"
        if context_manager.load_context(filename):
            print(f"{Fore.GREEN}✓ 已从 {filename} 加载上下文{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ 加载失败或文件不存在: {filename}{Style.RESET_ALL}")
    
    else:
        print(f"{Fore.RED}未知的context命令: {subcommand}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}可用命令: set, status, clear, save, load{Style.RESET_ALL}")

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

    # 超大型项目分析命令
    elif command == '/init':
        handle_init_command(command_parts)

    # 上下文管理命令
    elif command == '/context':
        handle_context_command(command_parts)

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
    _check_and_suggest_analysis_docs()
    return True

def _check_and_suggest_analysis_docs():
    """检查是否有项目分析文档可用，并提示用户"""
    import os
    from pathlib import Path
    
    current_dir = os.getcwd()
    project_name = os.path.basename(current_dir)
    docs_folder = os.path.join(current_dir, f"{project_name}_analysis_docs")
    
    if os.path.exists(docs_folder) and os.path.isdir(docs_folder):
        # 检查文档数量
        md_files = [f for f in os.listdir(docs_folder) if f.endswith('.md')]
        if md_files:
            print(f"{Fore.LIGHTBLUE_EX}📁 提示：发现项目分析文档（{len(md_files)}个文件）{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📝 文档位置：{docs_folder}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 当您需要快速了解项目时，可以查看这些分析文档{Style.RESET_ALL}")
            print()
    print()
    return True
