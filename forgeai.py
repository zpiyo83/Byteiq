
#!/usr/bin/env python3
"""
Forge AI Code - 主程序（清理版）
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
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".forgeai_config.json")

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
    print(f"  3 - 日本語 (ja-JP)")
    print(f"  回车 - 保持不变")

    choice = input(f"\n{Fore.WHITE}请选择语言 > {Style.RESET_ALL}").strip()

    lang_map = {
        "1": "zh-CN",
        "2": "en-US",
        "3": "ja-JP"
    }

    if choice in lang_map:
        cfg = load_config()
        cfg["language"] = lang_map[choice]
        if save_config(cfg):
            print(f"{Fore.GREEN}✓ 语言设置已保存: {lang_map[choice]}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ 保存失败{Style.RESET_ALL}")

def set_api_key_interactive():
    """交互式设置API密钥"""
    print(f"\n{Fore.LIGHTCYAN_EX}设置API密钥{Style.RESET_ALL}")
    print(f"请输入您的API密钥（输入为空则保持不变）:")

    api_key = input(f"{Fore.WHITE}API Key > {Style.RESET_ALL}").strip()

    if api_key:
        cfg = load_config()
        cfg["api_key"] = api_key
        if save_config(cfg):
            print(f"{Fore.GREEN}✓ API密钥已保存{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ 保存失败{Style.RESET_ALL}")

def set_model_interactive():
    """交互式设置模型"""
    print(f"\n{Fore.LIGHTCYAN_EX}设置AI模型{Style.RESET_ALL}")
    print(f"常用模型:")
    print(f"  gpt-3.5-turbo, gpt-4, gpt-4-turbo")
    print(f"  claude-3-haiku, claude-3-sonnet, claude-3-opus")
    print(f"  gemini-pro, llama2-70b, 等...")
    print(f"\n{Fore.YELLOW}提示: 直接输入模型名称，回车保持不变{Style.RESET_ALL}")

    new_model = input(f"\n{Fore.WHITE}请输入模型名称 > {Style.RESET_ALL}").strip()

    if new_model:
        cfg = load_config()
        cfg["model"] = new_model
        if save_config(cfg):
            print(f"{Fore.GREEN}✓ AI模型设置已保存: {new_model}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ 保存失败{Style.RESET_ALL}")

def show_settings():
    """显示设置菜单"""
    # 使用统一的配置管理系统
    from src.config import show_settings as config_show_settings
    config_show_settings()

# ========== AI功能 ==========
# 使用统一的AI客户端（包含新功能：思考动画、ESC中断）
from src.ai_client import ai_client

# 使用统一的工具处理器（包含权限控制）
from src.ai_tools import ai_tool_processor
from src.input_handler import get_input_with_claude_style
from src.keyboard_handler import (
    stop_task_monitoring,
    is_task_interrupted, reset_interrupt_flag
)

def process_ai_conversation(user_input):
    """处理AI对话"""
    # 检查是否配置了API密钥
    config = load_config()
    if not config.get('api_key'):
        print(f"{Fore.RED}错误：请先设置API密钥。使用 /s 命令进入设置。{Style.RESET_ALL}")
        return

    # 检查是否处于HACPP模式
    from src.modes import hacpp_mode
    from src.hacpp_client import hacpp_client

    if hacpp_mode.is_hacpp_active():
        print(f"{Fore.MAGENTA}🚀 HACPP模式激活 - 双AI协作处理{Style.RESET_ALL}")
        hacpp_client.process_hacpp_request(user_input)
        return

    # 重置中断标志
    reset_interrupt_flag()

    # 发送消息给AI（已集成思考动画和ESC监控）
    ai_response = ai_client.send_message(user_input)

    # 检查是否在发送阶段被中断
    if is_task_interrupted():
        print(f"\n{Fore.YELLOW}任务已被用户中断{Style.RESET_ALL}")
        return

    # 检查是否启用了原始输出模式
    from src.debug_config import is_raw_output_enabled
    if is_raw_output_enabled():
        print(f"\n{ai_response}")
        return

    # 处理AI响应和工具调用（添加循环计数器和重复检测）
    max_iterations = 50  # 🚨 最大迭代次数提升到50次
    iteration_count = 0
    recent_operations = []  # 记录最近的操作，用于检测重复

    while True:
        # 检查是否被中断
        if is_task_interrupted():
            print(f"\n{Fore.YELLOW}任务处理已被用户中断{Style.RESET_ALL}")
            break

        iteration_count += 1
        if iteration_count > max_iterations:
            print(f"\n{Fore.RED}警告: AI处理超过最大迭代次数({max_iterations})，停止处理{Style.RESET_ALL}")
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
                print(f"\n{Fore.RED}检测到重复操作，停止处理避免无限循环{Style.RESET_ALL}")
                break

        # 显示AI的意图（过滤XML）
        if result['display_text'].strip():
            print(f"\n{Fore.GREEN}AI: {result['display_text']}{Style.RESET_ALL}")

        # 如果有工具调用，显示结果
        if result['has_tool'] and result['tool_result']:
            print(f"{Fore.YELLOW}执行结果: {result['tool_result']}{Style.RESET_ALL}")

        # 🚨 简化停止条件检查 - 只有should_continue=False才能停止
        if not result['should_continue']:
            print(f"\n{Fore.GREEN}任务处理完成{Style.RESET_ALL}")
            break

        # 🚨 如果需要继续，继续对话（包括工具执行失败的情况）
        if result['has_tool']:
            print(f"\n{Fore.CYAN}AI继续处理... (第{iteration_count}次){Style.RESET_ALL}")
            # 将工具执行结果发送回AI，包括错误信息
            ai_response = ai_client.send_message(f"工具执行结果: {result['tool_result']}", include_structure=False)

            # 检查继续处理时是否被中断
            if is_task_interrupted():
                print(f"\n{Fore.YELLOW}任务处理已被用户中断{Style.RESET_ALL}")
                break
        else:
            # 没有工具调用的情况，也要检查是否应该继续
            if result['should_continue']:
                print(f"\n{Fore.CYAN}AI继续处理... (第{iteration_count}次){Style.RESET_ALL}")
                # 发送一个继续的提示
                ai_response = ai_client.send_message("请继续完成任务。", include_structure=False)
            else:
                print(f"\n{Fore.GREEN}任务处理完成{Style.RESET_ALL}")
                break

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
            print(f"{Fore.YELLOW}✓ 原始输出模式已{new_state}。{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}未知调试命令。可用命令: /debug raw{Style.RESET_ALL}")
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

    # 退出命令
    if user_input.lower() in ['/exit', '/quit', '/q']:
        print(f"{Fore.CYAN}再见！感谢使用 Forge AI Code{Style.RESET_ALL}")
        return "exit"

    return False

def handle_mcp_command():
    """处理MCP命令"""
    try:
        from src.mcp_config import mcp_config


        print(f"\n{Fore.CYAN}🔧 MCP (Model Context Protocol) 管理{Style.RESET_ALL}")
        print("=" * 60)

        # 显示当前状态
        mcp_config.show_config_summary()

        print(f"\n{Fore.CYAN}MCP管理选项:{Style.RESET_ALL}")
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
                    print(f"{Fore.GREEN}✓ MCP已启用{Style.RESET_ALL}")
                elif enable_choice in ['n', 'no']:
                    mcp_config.enable_mcp(False)
                    print(f"{Fore.YELLOW}MCP已禁用{Style.RESET_ALL}")

            elif choice == '2':
                _configure_mcp_servers()

            elif choice == '3':
                _start_mcp_servers()

            elif choice == '4':
                _stop_mcp_servers()

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
                print(f"{Fore.YELLOW}无效选择{Style.RESET_ALL}")

    except ImportError as e:
        print(f"{Fore.RED}MCP模块导入失败: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}MCP命令处理失败: {e}{Style.RESET_ALL}")

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
                print(f"{Fore.GREEN}✓ {server_name} 已启用{Style.RESET_ALL}")

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
                            print(f"✓ {env_key} 已更新")

            elif enable_choice in ['n', 'no']:
                mcp_config.enable_server(server_name, False)
                print(f"{Fore.YELLOW}{server_name} 已禁用{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}无效的服务器编号{Style.RESET_ALL}")

    except ValueError:
        print(f"{Fore.YELLOW}请输入有效的数字{Style.RESET_ALL}")

def _start_mcp_servers():
    """启动MCP服务器"""
    from src.mcp_config import mcp_config
    from src.mcp_client import mcp_client
    import asyncio

    if not mcp_config.is_enabled():
        print(f"{Fore.YELLOW}MCP功能未启用{Style.RESET_ALL}")
        return

    enabled_servers = mcp_config.get_enabled_servers()
    if not enabled_servers:
        print(f"{Fore.YELLOW}没有启用的服务器{Style.RESET_ALL}")
        return

    print(f"\n{Fore.CYAN}启动MCP服务器{Style.RESET_ALL}")

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
                    print(f"{Fore.GREEN}✓ {server_name} 启动成功{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ {server_name} 启动失败{Style.RESET_ALL}")
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
        print(f"{Fore.GREEN}✓ 所有MCP服务器已停止{Style.RESET_ALL}")
    finally:
        loop.close()

def _show_mcp_server_status():
    """显示MCP服务器状态"""
    from src.mcp_client import mcp_client

    print(f"\n{Fore.CYAN}MCP服务器状态{Style.RESET_ALL}")
    print("=" * 40)

    status = mcp_client.get_server_status()

    if not status:
        print(f"{Fore.YELLOW}没有配置的服务器{Style.RESET_ALL}")
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
        print(f"{Fore.YELLOW}没有可用的工具{Style.RESET_ALL}")
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
        print(f"{Fore.YELLOW}没有可用的资源{Style.RESET_ALL}")
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
    print(f"{Fore.LIGHTCYAN_EX}│{' ' * 18}Forge AI Code{' ' * 28}│{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}│{' ' * 15}智能编程助手 v2.0{' ' * 23}│{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}╰{'─' * 58}╯{Style.RESET_ALL}")

def print_status():
    """打印状态信息"""
    from src.modes import mode_manager

    # 当前模式行
    mode_text = f"Mode: {mode_manager.get_current_mode()} (Alt+L to switch)"
    mode_color = Fore.GREEN if mode_manager.get_current_mode() == "sprint" else Fore.YELLOW

    # 权限信息
    permissions = mode_manager.get_mode_permissions()
    perm_text = ""
    if "allowed" in permissions and permissions["allowed"]:
        perm_text += f" | 允许: {', '.join(permissions['allowed'][:2])}"
    if "confirm" in permissions and permissions["confirm"]:
        perm_text += f" | 需确认: {', '.join(permissions['confirm'][:2])}"

    print(f"{mode_color}{mode_text}{perm_text}{Style.RESET_ALL}")

def auto_start_mcp_servers():
    """自动启动MCP服务器"""
    try:
        from src.mcp_config import mcp_config
        from src.mcp_client import mcp_client
        import asyncio

        # 检查MCP是否启用
        if not mcp_config.is_enabled():
            return

        # 获取启用的服务器
        enabled_servers = mcp_config.get_enabled_servers()
        if not enabled_servers:
            return

        print(f"{Fore.CYAN}🔧 启动MCP服务器...{Style.RESET_ALL}")

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
                print(f"{Fore.GREEN}✅ MCP服务器启动完成，可用工具: {tools_count} 个{Style.RESET_ALL}")

        finally:
            loop.close()

    except Exception as e:
        print(f"{Fore.YELLOW}⚠️ MCP服务器启动失败: {e}{Style.RESET_ALL}")

def initialize_theme():
    """初始化主题设置"""
    try:
        from src.theme import theme_manager
        from src.config import load_config

        # 加载配置
        cfg = load_config()

        # 获取主题设置
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
        # 初始化主题设置
        initialize_theme()

        # 打印欢迎界面
        from src.ui import print_welcome_screen
        print_welcome_screen()
        print()

        # 自动启动MCP服务器
        auto_start_mcp_servers()

        # 主循环
        while True:
            try:
                # 输入提示符现在由 get_input_with_claude_style() 处理
                # print_input_box()

                # 获取用户输入（安全版本）
                try:
                    user_input = get_input_with_claude_style()
                except EOFError:
                    # 处理EOF错误（比如Ctrl+Z或管道输入结束）
                    try:
                        print(f"\n{Fore.CYAN}检测到输入结束，程序退出{Style.RESET_ALL}")
                    except Exception:
                        import sys
                        sys.__stdout__.write("\n检测到输入结束，程序退出\n")
                        sys.__stdout__.flush()
                    break
                except KeyboardInterrupt:
                    # 处理Ctrl+C
                    try:
                        print(f"\n{Fore.YELLOW}使用 /exit 退出程序{Style.RESET_ALL}")
                    except Exception:
                        import sys
                        sys.__stdout__.write("\n使用 /exit 退出程序\n")
                        sys.__stdout__.flush()
                    continue

                # 检查空输入
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
                try:
                    print(f"\n{Fore.YELLOW}使用 /exit 退出程序{Style.RESET_ALL}")
                except Exception:
                    # 如果colorama出错，使用基本输出
                    import sys
                    sys.__stdout__.write("\n使用 /exit 退出程序\n")
                    sys.__stdout__.flush()
                continue
            except EOFError:
                try:
                    print(f"\n{Fore.CYAN}再见！{Style.RESET_ALL}")
                except Exception:
                    # 如果colorama出错，使用基本输出
                    import sys
                    sys.__stdout__.write("\n再见！\n")
                    sys.__stdout__.flush()
                break

    except Exception as e:
        try:
            print(f"{Fore.RED}程序发生错误: {e}{Style.RESET_ALL}")
        except Exception:
            # 如果colorama出错，使用基本输出
            import sys
            sys.__stdout__.write(f"程序发生错误: {e}\n")
            sys.__stdout__.flush()
    finally:
        # 清理资源
        try:
            stop_task_monitoring()
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
