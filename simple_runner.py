# simple_runner.py

import sys
import os
from colorama import Fore, Style, init

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def run_app():
    """动态导入并运行应用程序"""
    # 现在我们可以使用绝对导入
    from src.command_processor import process_command
    from src.ui import print_welcome_screen
    from src.config import load_config

    # 初始化colorama
    init(autoreset=True)

    # 检查API密钥
    try:
        config = load_config()
        if not config.get('api_key'):
            print(f"{Fore.RED}警告：未找到API密钥。请运行 forgeai.py 并使用 /s 命令进行设置。{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}加载配置时出错: {e}{Style.RESET_ALL}")

    print_welcome_screen()
    print(f"\n{Fore.YELLOW}--- 简化测试运行器 ---{Style.RESET_ALL}")
    print(f"{Fore.CYAN}输入命令或与AI对话。输入 '/exit' 退出。{Style.RESET_ALL}\n")

    while True:
        try:
            user_input = input(f"{Fore.GREEN}>>> {Style.RESET_ALL}")
            if not user_input:
                continue

            should_continue = process_command(user_input)
            if not should_continue:
                break

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.YELLOW}再见！{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}发生错误: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    run_app()

