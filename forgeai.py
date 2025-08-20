#!/usr/bin/env python3
"""
Forge AI Code - 主程序（清理版）
"""

import os
import sys
import json
import requests
import threading
import time
import re
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
from src.thinking_animation import start_thinking, stop_thinking
from src.keyboard_handler import (
    start_task_monitoring, stop_task_monitoring, 
    show_esc_hint, is_task_interrupted, reset_interrupt_flag
)

def process_ai_conversation(user_input):
    """处理AI对话"""
    # 检查是否配置了API密钥
    config = load_config()
    if not config.get('api_key'):
        print(f"{Fore.RED}错误：请先设置API密钥。使用 /s 命令进入设置。{Style.RESET_ALL}")
        return

    # 重置中断标志
    reset_interrupt_flag()
    
    # 发送消息给AI（已集成思考动画和ESC监控）
    ai_response = ai_client.send_message(user_input)
    
    # 检查是否在发送阶段被中断
    if is_task_interrupted():
        print(f"\n{Fore.YELLOW}任务已被用户中断{Style.RESET_ALL}")
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

    # 退出命令
    if user_input.lower() in ['/exit', '/quit', '/q']:
        print(f"{Fore.CYAN}再见！感谢使用 Forge AI Code{Style.RESET_ALL}")
        return "exit"

    return False

# ========== UI界面 ==========
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

def print_input_box():
    """打印输入框"""
    # 输入框
    print(f"{Fore.LIGHTBLACK_EX}╭{'─' * 78}╮{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}│{' ' * 78}│{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}╰{'─' * 78}╯{Style.RESET_ALL}")

    # 当前模式提示文字（灰色）
    from src.modes import mode_manager
    current_mode = mode_manager.get_current_mode()
    print(f"{Fore.LIGHTBLACK_EX}? {current_mode}{Style.RESET_ALL}")

# ========== 主程序 ==========
def main():
    """主程序入口"""
    try:
        # 打印头部
        print_header()
        print()

        # 显示初始状态
        print_status()
        print()

        # 主循环
        while True:
            try:
                # 显示输入框
                print_input_box()

                # 获取用户输入（安全版本）
                try:
                    user_input = input(f"{Fore.WHITE}> {Style.RESET_ALL}").strip()
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
            stop_thinking()
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
