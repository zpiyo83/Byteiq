
#!/usr/bin/env python3
"""
ByteIQ - 主程序（清理版）
"""

import os
import sys
import json

from colorama import Fore, Style, init

# 初始化colorama以支持Windows终端颜色
init(autoreset=True)

# ========== 模式管理 ==========
# 模式管理已移至 src/modes.py，使用统一的模式管理器

def handle_mode_switch_command(user_input):
    """处理模式切换命令（使用统一的模式管理器）"""
    # 检查是否是模式切换命令
    if user_input.lower() in ['/mode', '/m', 'alt+l']:
        from src.modes import mode_manager
        mode_manager.show_mode_switch_notification()
        return True
    return False

# ========== 配置管理 ==========
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".byteiq_config.json")

def load_config():
    """加载配置文件"""
    if not os.path.exists(CONFIG_PATH):
        return {}

    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_config(config):
    """保存配置文件"""
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

# ========== 设置功能 ==========
def set_language_interactive():
    """交互式设置语言"""
    print(f"\n{Fore.LIGHTCYAN_EX}选择语言 / Choose Language{Style.RESET_ALL}")
    print(f"  1 - 中文 (zh-CN)")
    print(f"  2 - English (en-US)")
    print(f"  回车 - 保持不变")

    choice = input(f"\n{Fore.WHITE}请选择语言 > {Style.RESET_ALL}").strip()

    lang_map = {
        "1": "zh-CN",
        "2": "en-US"
    }

    if choice in lang_map:
        cfg = load_config()
        cfg["language"] = lang_map[choice]
        if save_config(cfg):
            print(f"  • 语言设置已保存: {lang_map[choice]}")
        else:
            print(f"  • 保存失败")

def set_api_key_interactive():
    """交互式设置API密钥"""
    print(f"\n{Fore.LIGHTCYAN_EX}设置API密钥{Style.RESET_ALL}")
    print(f"请输入您的API密钥（输入为空则保持不变）:")

    api_key = input(f"{Fore.WHITE}API Key > {Style.RESET_ALL}").strip()

    if api_key:
        cfg = load_config()
        cfg["api_key"] = api_key
        if save_config(cfg):
            print(f"  • API密钥已保存")
        else:
            print(f"  • 保存失败")

def set_model_interactive():
    """交互式设置模型"""
    print(f"\n{Fore.LIGHTCYAN_EX}设置AI模型{Style.RESET_ALL}")
    print(f"常用模型:")
    print(f"  gpt-3.5-turbo, gpt-4, gpt-4-turbo")
    print(f"  claude-3-haiku, claude-3-sonnet, claude-3-opus")
    print(f"  gemini-pro, llama2-70b, 等...")
    print(f"  • 提示: 直接输入模型名称，回车保持不变")

    new_model = input(f"\n{Fore.WHITE}请输入模型名称 > {Style.RESET_ALL}").strip()

    if new_model:
        cfg = load_config()
        cfg["model"] = new_model
        if save_config(cfg):
            print(f"  • AI模型设置已保存: {new_model}")
        else:
            print(f"  • 保存失败")

def show_settings():
    """显示设置菜单"""
    # 使用统一的配置管理系统
    from src.config import show_settings as config_show_settings
    config_show_settings()

# ========== AI功能 ==========
# AI模块延迟导入，提升启动速度
# 移除全局AI客户端导入，改为延迟加载

def process_ai_conversation(user_input):
    """处理AI对话"""
    # 导入theme_manager
    from src.theme import theme_manager
    
    # 检查是否配置了API密钥
    config = load_config()
    if not config.get('api_key'):
        print("错误：请先设置API密钥。使用 /s 命令进入设置。")
        return
    
    try:
        # 自动创建TODO任务 - 已禁用
        # try:
        #     from src.auto_todo import auto_todo_manager
        #     task_id = auto_todo_manager.create_todo_from_request(user_input)
        #     if task_id:
        #         print(f"📝 已自动创建任务: {auto_todo_manager.active_tasks[task_id]['title']}")
        # except Exception as e:
        #     # 忽略自动TODO创建过程中的任何错误，不显示错误信息
        #     pass
        
        # 使用延迟加载器获取AI客户端
        from src.lazy_loader import lazy_loader
        ai_client = lazy_loader.get_ai_client()
        if ai_client:
            ai_response = ai_client.send_message(user_input)
        else:
            # 回退到直接导入
            from src.ai_client import ai_client
            ai_response = ai_client.send_message(user_input)

        # 检查是否处于HACPP模式
        from src.modes import hacpp_mode
        from src.hacpp_client import hacpp_client

        if hacpp_mode.is_hacpp_active():
            print(f"\n{theme_manager.format_tool_header('HACPP', '模式激活 - 双AI协作处理')}")
            hacpp_client.process_hacpp_request(user_input)
            return

        # 使用延迟加载器获取AI工具处理器
        ai_tool_processor = lazy_loader.get_ai_tools()
        if not ai_tool_processor:
            # 回退到直接导入
            from src.ai_tools import ai_tool_processor
        
        # 使用延迟加载器获取token动画器
        token_animator = lazy_loader.get_token_animator()
        if not token_animator:
            # 回退到直接导入
            from src.token_animator import token_animator
        
        # 重置中断标志并启动ESC监控
        from src.keyboard_handler import reset_interrupt_flag, is_task_interrupted, start_task_monitoring, stop_task_monitoring, interrupt_current_task, show_esc_hint
        reset_interrupt_flag()
        
        # 启动ESC键监控
        start_task_monitoring(interrupt_current_task)
        show_esc_hint()

        # 开始上传动画
        token_animator.start_upload_animation(user_input)
        
        # 等待上传动画完成后再显示检查状态
        token_animator.wait_upload_complete()
        print(f"{Fore.YELLOW}● 检查中...{Style.RESET_ALL}")
        
        # 发送消息给AI（已集成思考动画和ESC监控）
        ai_response = ai_client.send_message(user_input)

        # 检查是否在发送阶段被中断
        if is_task_interrupted():
            print(f"\n  • 任务已被用户中断")
            token_animator.cleanup()
            return

        # 开始下载动画
        if ai_response:
            token_animator.start_download_animation(ai_response)
            token_animator.wait_download_complete()

        # 检查是否启用了原始输出模式
        from src.debug_config import is_raw_output_enabled
        if is_raw_output_enabled():
            print(f"\n{ai_response}")
            token_animator.cleanup()
            return

        # 处理AI响应和工具调用（添加循环计数器和重复检测）
        max_iterations = 100  # 🚨 最大迭代次数提升到100次
        iteration_count = 0
        recent_operations = []  # 记录最近的操作，用于检测重复

        while True:
            # 检查是否被中断
            if is_task_interrupted():
                print(f"\n  • 任务处理已被用户中断")
                break

            iteration_count += 1
            if iteration_count >= max_iterations:
                print(f"\n{Fore.YELLOW}⚠️ 现在已经迭代{max_iterations}次，请确认后继续{Style.RESET_ALL}")
                print(f"{Fore.CYAN}输入 'y' 继续处理，或按 Enter 停止:{Style.RESET_ALL} ", end="", flush=True)
                
                try:
                    user_choice = input().strip().lower()
                    if user_choice == 'y':
                        print(f"{Fore.GREEN}继续处理...{Style.RESET_ALL}")
                        max_iterations += 50  # 每次确认后再增加50次
                    else:
                        print(f"\n  • 用户选择停止处理")
                        break
                except (EOFError, KeyboardInterrupt):
                    print(f"\n  • 用户中断，停止处理")
                    break

            result = ai_tool_processor.process_response(ai_response)

            # 检测重复操作
            current_operation = result['display_text'].strip()
            if current_operation:
                recent_operations.append(current_operation)
                # 只保留最近5次操作
                if len(recent_operations) > 5:
                    recent_operations.pop(0)

                # 检查是否有重复操作（最近3次都是相同操作）
                if len(recent_operations) >= 3 and len(set(recent_operations[-3:])) == 1:
                    print(f"\n  • 检测到重复操作，停止处理避免无限循环")
                    break

            # 显示AI的意图（过滤XML）
            if result['display_text'].strip():
                print(f"\n{theme_manager.format_tool_header('AI', result['display_text'])}")

            # 工具调用结果已在工具输出中显示，这里不再重复显示

            # 简化停止条件检查 - 只有should_continue=False才能停止
            if not result['should_continue']:
                print(f"\n  • 任务处理完成")
                break

            # 如果需要继续，继续对话（包括工具执行失败的情况）
            if result['has_tool']:
                # 检查是否被中断
                if is_task_interrupted():
                    print(f"\n  • 任务处理已被用户中断")
                    break
                    
                # 将工具执行结果发送回AI，包括错误信息
                ai_response = ai_client.send_message(f"工具执行结果: {result['tool_result']}", include_structure=False)
                
                # 为继续的AI响应显示下载动画
                if ai_response:
                    token_animator.start_download_animation(ai_response)
                    token_animator.wait_download_complete()

                # 检查继续处理时是否被中断
                if is_task_interrupted():
                    print(f"\n  • 任务处理已被用户中断")
                    break
            else:
                # 没有工具调用的情况，也要检查是否应该继续
                if result['should_continue']:
                    # 检查是否被中断
                    if is_task_interrupted():
                        print(f"\n  • 任务处理已被用户中断")
                        break
                        
                    # 发送一个继续的提示
                    ai_response = ai_client.send_message("请继续完成任务。", include_structure=False)
                    
                    # 为继续的AI响应显示下载动画
                    if ai_response:
                        token_animator.start_download_animation(ai_response)
                        token_animator.wait_download_complete()
                    
                    # 检查继续处理时是否被中断
                    if is_task_interrupted():
                        print(f"\n  • 任务处理已被用户中断")
                        break
                else:
                    break

        # 清理token动画器
        try:
            token_animator.cleanup()
        except:
            pass
    
    except Exception as e:
        print(f"处理AI对话时出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保停止ESC监控
        try:
            from src.keyboard_handler import stop_task_monitoring
            stop_task_monitoring()
        except:
            pass
    
    print()  # 空行分隔

# ========== 命令处理 ==========
def handle_special_commands(user_input):
    """处理特殊命令"""
    user_input = user_input.strip()


    # 调试命令
    if user_input.lower().startswith('/debug'):
        parts = user_input.split()
        if len(parts) > 1 and parts[1].lower() == 'raw':
            from src.debug_config import toggle_raw_output, is_raw_output_enabled
            toggle_raw_output()
            new_state = "启用" if is_raw_output_enabled() else "禁用"
            print(f"  • 原始输出模式已{new_state}")
        else:
            print(f"  • 未知调试命令。可用命令: /debug raw")
        return True

    # 压缩命令
    if user_input.lower() in ['/compact']:
        from src.compression import show_compression_menu, compress_context
        compression_type = show_compression_menu()
        if compression_type:
            compress_context(compression_type)
        return True


    # 设置命令
    if user_input.lower() in ['/s', '/setting', '/settings']:
        show_settings()
        return True

    # 模式切换命令
    if handle_mode_switch_command(user_input):
        return True

    # 帮助命令
    if user_input.lower() in ['/h', '/help', '/?']:
        from src.commands import show_help
        show_help()
        return True

    # TODO命令
    if user_input.lower() in ['/t', '/todo', '/todos']:
        from src.commands import show_todos_command
        show_todos_command()
        return True

    # MCP命令
    if user_input.lower() in ['/mcp', '/m', '/model-context-protocol']:
        handle_mcp_command()
        return True

    # HACPP模式命令
    if user_input.lower().startswith('/hacpp'):
        from src.command_processor import handle_hacpp_command
        command_parts = user_input.split()
        handle_hacpp_command(command_parts)
        return True

    # AI辅助调试命令
    if user_input.lower().startswith('/fix'):
        from src.command_processor import handle_fix_command
        command_parts = user_input.split()
        handle_fix_command(command_parts)
        return True

    # 上下文管理命令
    if user_input.lower().startswith('/context') or user_input.lower().startswith('/ctx'):
        handle_context_command(user_input)
        return True

    # 代理增强命令
    if user_input.lower().startswith('/agent'):
        handle_agent_command(user_input)
        return True

    # 项目分析命令
    if user_input.lower() in ['/analyze']:
        handle_analyze_command()
        return True

    # 聊天上下文管理命令
    if user_input.lower().startswith('/chat'):
        handle_chat_command(user_input)
        return True

    # 导出上下文命令
    if user_input.lower() in ['/export']:
        handle_export_command()
        return True

    # 超大型项目分析命令
    if user_input.lower().startswith('/init'):
        from src.command_processor import handle_init_command
        command_parts = user_input.split()
        handle_init_command(command_parts)
        return True

    return False

def handle_analyze_command():
    """处理项目分析命令"""
    try:
        from src.theme import theme_manager
        print(f"\n{theme_manager.format_tool_header('Analyze', '开始分析项目')}")
        
        # 使用延迟加载器获取项目分析器
        from src.lazy_loader import lazy_loader
        project_analyzer_module = lazy_loader.get_module('src.project_analyzer')
        
        if project_analyzer_module:
            analyzer = project_analyzer_module.project_analyzer
        else:
            # 回退到直接导入
            from src.project_analyzer import project_analyzer as analyzer
        
        # 分析项目
        analysis_result = analyzer.analyze_project()
        
        if analysis_result:
            # 获取AI客户端用于增强内容
            from src.lazy_loader import lazy_loader
            ai_client = lazy_loader.get_ai_client()
            if not ai_client:
                from src.ai_client import ai_client
            
            # 生成BYTEIQ.md文件，让AI参与优化
            output_path = analyzer.generate_byteiq_md(ai_client=ai_client)
            print(f"  • 项目分析完成，AI增强配置文件已生成")
        else:
            print(f"  • 项目分析失败")
        
        # 显示分析摘要
        print(f"\n{theme_manager.format_tool_header('Analyze', '项目摘要')}")
        print(f"  项目类型: {analysis_result['project_type']}")
        print(f"  技术栈: {', '.join(analysis_result['tech_stack'])}")
        print(f"  文件总数: {analysis_result['file_structure']['total_files']}")
        print(f"  项目大小: {analysis_result['project_info']['size']['size_mb']} MB")
        
        if analysis_result['code_features']['languages']:
            print(f"  编程语言: {', '.join(analysis_result['code_features']['languages'])}")
        
        if analysis_result['code_features']['frameworks']:
            print(f"  使用框架: {', '.join(analysis_result['code_features']['frameworks'])}")
        
        print(f"  • BYTEIQ.md 文件包含了项目的详细配置，AI助手将根据此配置提供更精准的帮助")
        
    except Exception as e:
        print(f"处理AI对话时出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保停止ESC监控
        try:
            from src.keyboard_handler import stop_task_monitoring
            stop_task_monitoring()
        except:
            pass

def handle_chat_command(user_input):
    """处理聊天上下文管理命令"""
    try:
        from src.theme import theme_manager
        from src.lazy_loader import lazy_loader
        ai_client = lazy_loader.get_ai_client()
        if not ai_client:
            from src.ai_client import ai_client
        
        from src.chat_manager import chat_manager
        
        parts = user_input.split()
        if len(parts) == 1:
            # 显示帮助信息
            print(f"\n{theme_manager.format_tool_header('Chat', '上下文管理命令')}")
            print(f"  /chat save    - 保存当前上下文到软件目录")
            print(f"  /chat load    - 交互式加载已保存的上下文")
            print(f"  /chat delete  - 交互式删除已保存的上下文")
            print(f"  /export       - 导出上下文到当前目录")
            return
        
        subcommand = parts[1].lower()
        
        if subcommand == 'save':
            chat_manager.save_context_interactive(ai_client.context_manager)
        elif subcommand == 'load':
            chat_manager.load_context_interactive(ai_client.context_manager)
        elif subcommand == 'delete':
            chat_manager.delete_context_interactive()
        else:
            print(f"  • 未知子命令: {subcommand}")
            print(f"  • 可用命令: save, load, delete")
            
    except Exception as e:
        print(f"  • 聊天命令处理失败: {e}")

def handle_export_command():
    """处理导出上下文命令"""
    try:
        from src.lazy_loader import lazy_loader
        ai_client = lazy_loader.get_ai_client()
        if not ai_client:
            from src.ai_client import ai_client
        
        from src.chat_manager import chat_manager
        chat_manager.export_context_to_current_dir(ai_client.context_manager)
        
    except Exception as e:
        print(f"  • 导出命令处理失败: {e}")

def handle_context_command(user_input):
    """处理上下文管理命令"""
    try:
        from src.theme import theme_manager
        from src.ai_client import ai_client
        
        parts = user_input.split()
        if len(parts) == 1:
            # 显示上下文状态
            stats = ai_client.context_manager.get_context_stats()
            print(f"\n{theme_manager.format_tool_header('Context', '状态')}")
            print("=" * 50)
            print(f"总Token数: {stats['total_tokens']:,} / {stats['max_tokens']:,}")
            print(f"利用率: {stats['utilization_percent']}%")
            print(f"对话消息: {stats['conversation_messages']}")
            print(f"项目上下文: {stats['project_contexts']}")
            print(f"代码上下文: {stats['code_contexts']}")
            print(f"会话摘要: {'是' if stats['has_summary'] else '否'}")
            
            # 显示进度条
            bar_length = 30
            filled_length = int(bar_length * stats['utilization_percent'] / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            print(f"进度: [{bar}] {stats['utilization_percent']}%")
            
        elif parts[1].lower() == 'clear':
            ai_client.context_manager.clear_context()
            
        elif parts[1].lower() == 'save':
            filename = parts[2] if len(parts) > 2 else ".byteiq_context.json"
            ai_client.context_manager.save_context(filename)
            print(f"  • 上下文已保存到 {filename}")
            
        elif parts[1].lower() == 'load':
            filename = parts[2] if len(parts) > 2 else ".byteiq_context.json"
            success = ai_client.context_manager.load_context(filename)
            if success:
                print(f"  • 已从 {filename} 加载上下文")
            else:
                print(f"  • 无法加载 {filename}")
        
        elif parts[1].lower() == 'set':
            if len(parts) < 3:
                print(f"  • 用法: /context set <token数量>")
                return
            
            try:
                max_tokens = int(parts[2])
                ai_client.context_manager.set_max_tokens(max_tokens)
            except ValueError:
                print(f"  • 无效的token数量: {parts[2]}")
            except Exception as e:
                print(f"  • 设置失败: {e}")
                
        else:
            print(f"\n{theme_manager.format_tool_header('Context', '管理命令')}")
            print(f"  /context          - 显示上下文状态")
            print(f"  /context clear    - 清除所有上下文")
            print(f"  /context save [文件名] - 保存上下文到文件")
            print(f"  /context load [文件名] - 从文件加载上下文")
            print(f"  /context set <tokens>  - 设置上下文token限制")
            print(f"\n  • 示例:")
            print(f"  /context set 12800    - 设置上下文限制为12800 tokens")
            print(f"  /context set 25600    - 设置上下文限制为25600 tokens")
            print(f"  /context set 180000   - 设置上下文限制为180000 tokens")
            
    except Exception as e:
        print(f"  • 上下文命令处理失败: {e}")

def handle_agent_command(user_input):
    """处理代理增强命令"""
    try:
        from src.theme import theme_manager
        from src.ai_client import ai_client
        
        parts = user_input.split()
        if len(parts) == 1:
            # 显示代理状态
            status = ai_client.agent_enhancer.get_execution_status()
            print(f"\n{theme_manager.format_tool_header('Agent', '执行状态')}")
            print("=" * 50)
            print(f"总任务数: {status['total_tasks']}")
            print(f"已完成: {status['completed_tasks']}")
            print(f"待执行: {status['pending_tasks']}")
            print(f"失败任务: {status['failed_tasks']}")
            print(f"完成率: {status['progress_percent']}%")
            
            if status['current_task']:
                print(f"当前任务: {status['current_task']}")
                
        elif parts[1].lower() == 'clear':
            ai_client.agent_enhancer.clear_plans()
            
        elif parts[1].lower() == 'next':
            next_task = ai_client.agent_enhancer.get_next_task()
            if next_task:
                print(f"  • 下一个任务: {next_task.description}")
                print(f"优先级: {next_task.priority}")
                print(f"状态: {next_task.status}")
            else:
                print(f"  • 没有待执行的任务")
                
        else:
            print(f"\n{theme_manager.format_tool_header('Agent', '增强命令')}")
            print("  /agent              - 显示代理执行状态")
            print("  /agent clear        - 清除所有执行计划")
            print("  /agent next         - 显示下一个任务")
            
    except Exception as e:
        print(f"  • 代理命令处理失败: {e}")

def handle_clear_command():
    """处理清除上下文命令"""
    try:
        from src.lazy_loader import lazy_loader
        ai_client = lazy_loader.get_ai_client()
        if not ai_client:
            from src.ai_client import ai_client
        
        # 直接清除上下文
        ai_client.context_manager.clear_context()
        print(f"  • 上下文已清除")
            
    except Exception as e:
        print(f"  • 清除命令处理失败: {e}")

def handle_mcp_command(user_input):
    """处理MCP命令"""
    try:
        from src.theme import theme_manager
        from src.mcp_config import mcp_config

        print(f"\n{theme_manager.format_tool_header('MCP', 'Model Context Protocol 管理')}")
        print("=" * 60)

        # 显示当前状态
        mcp_config.show_config_summary()

        print(f"\n  • MCP管理选项:")
        print("  1 - 启用/禁用MCP")
        print("  2 - 配置服务器")
        print("  3 - 启动服务器")
        print("  4 - 停止服务器")
        print("  5 - 查看服务器状态")
        print("  6 - 列出可用工具")
        print("  7 - 列出可用资源")
        print("  8 - 交互式设置")
        print("  q - 返回")

        while True:
            choice = input(f"\n{Fore.WHITE}请选择操作 > {Style.RESET_ALL}").strip().lower()

            if choice == '1':
                current_status = "启用" if mcp_config.is_enabled() else "禁用"
                print(f"当前状态: {current_status}")

                enable_choice = input(f"是否启用MCP? (y/n): ").strip().lower()
                if enable_choice in ['y', 'yes']:
                    mcp_config.enable_mcp(True)
                    print(f"  • MCP已启用")
                elif enable_choice in ['n', 'no']:
                    mcp_config.enable_mcp(False)
                    print(f"  • MCP已禁用")

            elif choice == '2':
                _configure_mcp_servers()

            elif choice == '3':
                auto_start_mcp_servers()

            elif choice == '4':
                auto_stop_mcp_servers()

            elif choice == '5':
                _show_mcp_server_status()

            elif choice == '6':
                _list_mcp_tools()

            elif choice == '7':
                _list_mcp_resources()

            elif choice == '8':
                mcp_config.interactive_setup()

            elif choice == 'q':
                break

            else:
                print(f"  • 无效选择")

    except ImportError as e:
        print(f"  • MCP模块导入失败: {e}")
    except Exception as e:
        print(f"  • MCP命令处理失败: {e}")

def auto_start_mcp_servers():
    """自动启动MCP服务器（延迟加载版本）"""
    try:
        from src.lazy_loader import lazy_loader
        
        # 使用延迟加载器获取MCP组件
        mcp_config = lazy_loader.get_mcp_config()
        mcp_client = lazy_loader.get_mcp_client()
        
        if not mcp_config or not mcp_client:
            # 回退到直接导入
            from src.mcp_config import mcp_config
            from src.mcp_client import mcp_client
        
        # 获取配置的服务器列表
        servers = mcp_config.get_configured_servers()
        
        if not servers:
            print(f"  • 没有配置MCP服务器")
            return
        
        print(f"\n{theme_manager.format_tool_header('MCP', '启动服务器')}")
        
        # 启动所有配置的服务器
        for server_name in servers:
            try:
                mcp_client.start_server(server_name)
                print(f"  • {server_name} 服务器已启动")
            except Exception as e:
                print(f"  • {server_name} 启动失败: {e}")
                
    except Exception as e:
        print(f"  • MCP服务器启动失败: {e}")

def auto_stop_mcp_servers():
    """自动停止MCP服务器（延迟加载版本）"""
    try:
        from src.lazy_loader import lazy_loader
        
        # 使用延迟加载器获取MCP组件
        mcp_config = lazy_loader.get_mcp_config()
        mcp_client = lazy_loader.get_mcp_client()
        
        if not mcp_config or not mcp_client:
            # 回退到直接导入
            from src.mcp_config import mcp_config
            from src.mcp_client import mcp_client
        
        # 获取配置的服务器列表
        servers = mcp_config.get_configured_servers()
        
        if not servers:
            print(f"  • 没有配置MCP服务器")
            return
        
        print(f"\n{theme_manager.format_tool_header('MCP', '停止服务器')}")
        
        # 停止所有配置的服务器
        for server_name in servers:
            try:
                mcp_client.stop_server(server_name)
                print(f"  • {server_name} 服务器已停止")
            except Exception as e:
                print(f"  • {server_name} 停止失败: {e}")
                
    except Exception as e:
        print(f"  • MCP服务器停止失败: {e}")

def _configure_mcp_servers():
    """配置MCP服务器"""
    from src.mcp_config import mcp_config

    print(f"\n{Fore.CYAN}配置MCP服务器{Style.RESET_ALL}")
    servers = mcp_config.config.get("servers", {})

    print("可用服务器:")
    for i, (name, config) in enumerate(servers.items(), 1):
        status = "启用" if config.get("enabled", False) else "禁用"
        print(f"  {i}. {name} - {config.get('description', '')} ({status})")

    try:
        choice = int(input("\n请选择要配置的服务器编号: ")) - 1
        server_names = list(servers.keys())

        if 0 <= choice < len(server_names):
            server_name = server_names[choice]
            server_config = servers[server_name]

            print(f"\n配置服务器: {server_name}")
            print(f"描述: {server_config.get('description', '')}")

            # 启用/禁用
            current_enabled = server_config.get("enabled", False)
            enable_choice = input(f"启用服务器? (y/n, 当前: {'y' if current_enabled else 'n'}): ").strip().lower()

            if enable_choice in ['y', 'yes']:
                mcp_config.enable_server(server_name, True)
                print(f"  • {server_name} 已启用")

                # 配置环境变量
                env_vars = server_config.get("env", {})
                if env_vars:
                    print(f"\n环境变量配置:")
                    for env_key in env_vars.keys():
                        current_value = env_vars.get(env_key, "")
                        display_value = "***" if current_value and ("key" in env_key.lower() or "token" in env_key.lower()) else current_value
                        print(f"  {env_key}: {display_value}")

                        new_value = input(f"请输入 {env_key} 的值 (留空保持不变): ").strip()
                        if new_value:
                            mcp_config.set_server_env(server_name, env_key, new_value)
                            print(f"  • {env_key} 已更新")

            elif enable_choice in ['n', 'no']:
                mcp_config.enable_server(server_name, False)
                print(f"  • {server_name} 已禁用")
        else:
            print(f"  • 无效的服务器编号")

    except ValueError:
        print(f"  • 请输入有效的数字")

def _start_mcp_servers():
    """启动MCP服务器"""
    from src.mcp_config import mcp_config
    from src.mcp_client import mcp_client
    import asyncio

    if not mcp_config.is_enabled():
        print(f"  • MCP功能未启用")
        return

    enabled_servers = mcp_config.get_enabled_servers()
    if not enabled_servers:
        print(f"  • 没有启用的服务器")
        return

    print(f"\n{theme_manager.format_tool_header('MCP', '启动服务器')}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        for server_name in enabled_servers:
            server_config = mcp_config.get_server_config(server_name)
            if server_config:
                print(f"启动服务器: {server_name}")

                # 添加服务器到MCP客户端
                mcp_client.add_server(
                    server_name,
                    server_config.get("command", []),
                    server_config.get("args", []),
                    server_config.get("env", {}),
                    server_config.get("type", "process"),
                    server_config.get("url")
                )

                # 启动服务器
                success = loop.run_until_complete(mcp_client.start_server(server_name))

                if success:
                    print(f"  • {server_name} 启动成功")
                else:
                    print(f"  • {server_name} 启动失败")
    finally:
        loop.close()

def _stop_mcp_servers():
    """停止MCP服务器"""
    from src.mcp_client import mcp_client
    import asyncio

    print(f"\n{Fore.CYAN}停止MCP服务器{Style.RESET_ALL}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(mcp_client.stop_all_servers())
        print(f"  • 所有MCP服务器已停止")
    finally:
        loop.close()

def _show_mcp_server_status():
    """显示MCP服务器状态"""
    from src.mcp_client import mcp_client

    print(f"\n{Fore.CYAN}MCP服务器状态{Style.RESET_ALL}")
    print("=" * 40)

    status = mcp_client.get_server_status()

    if not status:
        print(f"  • 没有配置的服务器")
        return

    for server_name, server_status in status.items():
        status_color = Fore.GREEN if server_status == "运行中" else Fore.YELLOW
        print(f"{status_color}{server_name}: {server_status}{Style.RESET_ALL}")

    # 显示统计信息
    tools_count = len(mcp_client.get_available_tools())
    resources_count = len(mcp_client.get_available_resources())

    print(f"\n统计信息:")
    print(f"  可用工具: {tools_count}")
    print(f"  可用资源: {resources_count}")

def _list_mcp_tools():
    """列出MCP工具"""
    from src.mcp_client import mcp_client

    print(f"\n{Fore.CYAN}可用的MCP工具{Style.RESET_ALL}")
    print("=" * 40)

    tools = mcp_client.get_available_tools()

    if not tools:
        print(f"  • 没有可用的工具")
        return

    for tool in tools:
        print(f"{Fore.GREEN}工具: {tool.name}{Style.RESET_ALL}")
        print(f"  服务器: {tool.server_name}")
        print(f"  描述: {tool.description}")
        print()

def _list_mcp_resources():
    """列出MCP资源"""
    from src.mcp_client import mcp_client

    print(f"\n{Fore.CYAN}可用的MCP资源{Style.RESET_ALL}")
    print("=" * 40)

    resources = mcp_client.get_available_resources()

    if not resources:
        print(f"  • 没有可用的资源")
        return

    for resource in resources:
        print(f"{Fore.GREEN}资源: {resource.name}{Style.RESET_ALL}")
        print(f"  服务器: {resource.server_name}")
        print(f"  URI: {resource.uri}")
        print(f"  描述: {resource.description}")
        print()

# ========== UI界面 ==========
# UI模块在main函数内按需导入

def print_header():
    """打印程序头部"""
    print(f"{Fore.LIGHTCYAN_EX}╭{'─' * 58}╮{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}│{' ' * 22}ByteIQ{' ' * 32}│{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}│{' ' * 15}智能编程助手 v2.0{' ' * 23}│{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}╰{'─' * 58}╯{Style.RESET_ALL}")

def show_prompt():
    """显示输入提示符"""
    from src.modes import mode_manager
    from src.theme import theme_manager
    
    # 当前模式行
    mode_text = f"Mode: {mode_manager.get_current_mode()} (Alt+L to switch)"
    mode_color = theme_manager.get_tool_color('success') if mode_manager.get_current_mode() == "sprint" else theme_manager.get_tool_color('warning')

    # 权限信息
    permissions = mode_manager.get_mode_permissions()
    perm_text = ""
    if "allowed" in permissions and permissions["allowed"]:
        perm_text += f" | 允许: {', '.join(permissions['allowed'][:2])}"
    if "confirm" in permissions and permissions["confirm"]:
        perm_text += f" | 需确认: {', '.join(permissions['confirm'][:2])}"

    print(f"{mode_color}{mode_text}{perm_text}{Style.RESET_ALL}")

def auto_start_mcp_servers():
    """自动启动MCP服务器（延迟执行，提升启动速度）"""
    try:
        # 延迟导入，避免启动时加载
        from src.mcp_config import mcp_config
        
        # 快速检查是否启用，避免不必要的导入
        if not mcp_config.is_enabled():
            return

        # 获取启用的服务器
        enabled_servers = mcp_config.get_enabled_servers()
        if not enabled_servers:
            return

        # 只有在确实需要时才导入重量级模块
        from src.mcp_client import mcp_client
        import asyncio

        print(f"\n{theme_manager.format_tool_header('MCP', '启动服务器')}")

        # 创建异步事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            success_count = 0
            for server_name in enabled_servers:
                server_config = mcp_config.get_server_config(server_name)
                if server_config:
                    # 添加服务器到MCP客户端
                    mcp_client.add_server(
                        server_name,
                        server_config.get("command", []),
                        server_config.get("args", []),
                        server_config.get("env", {}),
                        server_config.get("type", "process"),
                        server_config.get("url")
                    )

                    # 启动服务器
                    success = loop.run_until_complete(mcp_client.start_server(server_name))
                    if success:
                        success_count += 1

            if success_count > 0:
                tools_count = len(mcp_client.get_available_tools())
                print(f"  • MCP服务器启动完成，可用工具: {tools_count} 个")

        finally:
            loop.close()

    except Exception as e:
        print(f"  • MCP服务器启动失败: {e}")

def initialize_theme():
    """初始化主题设置"""
    try:
        from src.theme import theme_manager
        from src.config import load_config, save_config

        # 获取主题设置
        cfg = load_config()
        theme = cfg.get("theme", "default")

        # 设置主题
        theme_manager.set_theme(theme)

    except Exception:
        # 如果主题初始化失败，使用默认主题
        pass

# ========== 主程序 ==========
def main():
    """主程序入口"""
    try:
        # 性能优化：启动时优化
        from src.performance_optimizer import get_performance_optimizer
        optimizer = get_performance_optimizer()
        optimizer.optimize_startup()
        
        # 初始化主题设置
        initialize_theme()

        # 打印欢迎界面
        from src.ui import print_welcome_screen
        print_welcome_screen()
        print()

        # 延迟启动MCP服务器，避免阻塞启动
        # auto_start_mcp_servers()  # 移至首次使用时启动

        # 主循环
        while True:
            try:
                # 定期检查内存使用并优化
                if optimizer.should_run_gc():
                    optimizer.optimize_memory()
                
                # 输入提示符现在由 get_input_with_claude_style() 处理
                # print_input_box()

                # 获取用户输入（安全版本）
                try:
                    # 使用延迟加载器获取输入处理器
                    from src.lazy_loader import lazy_loader
                    get_input_func = lazy_loader.get_input_handler()
                    if get_input_func:
                        user_input = get_input_func()
                    else:
                        # 回退到直接导入
                        from src.input_handler import get_input_with_claude_style
                        user_input = get_input_with_claude_style()
                except EOFError:
                    # 处理EOF错误（比如Ctrl+Z或管道输入结束）
                    print(f"\n{Fore.CYAN}检测到输入结束，程序退出{Style.RESET_ALL}")
                    break
                except Exception as e:
                    print(f"\n{Fore.RED}输入处理错误: {e}{Style.RESET_ALL}")
                    continue
                    
                if not user_input:
                    continue
                
                # 处理特殊命令
                result = handle_special_commands(user_input)
                if result == "exit":
                    break
                elif result:
                    continue
                
                # 处理AI对话
                process_ai_conversation(user_input)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}程序被用户中断{Style.RESET_ALL}")
                break
            except EOFError:
                print(f"\n{Fore.YELLOW}输入结束，退出程序{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}程序发生错误: {e}{Style.RESET_ALL}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"{Fore.RED}程序启动失败: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        try:
            print(f"  • 程序发生错误: {e}")
        except Exception:
            # 如果colorama出错，使用基本输出
            import sys
            sys.__stdout__.write(f"程序发生错误: {e}\n")
            sys.__stdout__.flush()
    finally:
        # 清理资源
        try:
            from src.lazy_loader import lazy_loader
            keyboard_funcs = lazy_loader.get_keyboard_handler()
            if keyboard_funcs.get('stop_task_monitoring'):
                keyboard_funcs['stop_task_monitoring']()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 最后的异常处理
        try:
            print(f"程序启动失败: {e}")
        except Exception:
            import sys
            sys.__stdout__.write(f"程序启动失败: {e}\n")
            sys.__stdout__.flush()
