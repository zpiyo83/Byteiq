#!/usr/bin/env python3
"""
Forge AI Code - AI编程助手命令行工具
主程序入口
"""

from colorama import init
from src.ui import print_welcome_screen
from src.input_handler import get_input_in_box
from src.command_processor import process_command

# 初始化colorama以支持Windows终端颜色
init(autoreset=True)

def main():
    """主程序入口"""
    print_welcome_screen()

    while True:
        try:
            # 使用输入框内输入
            user_input = get_input_in_box()
            
            if not user_input or user_input.strip() == "":
                continue

            # 处理命令
            should_continue = process_command(user_input)
            if not should_continue:
                break

        except KeyboardInterrupt:
            print(f"\n再见！感谢使用 Forge AI Code!")
            break
        except EOFError:
            print(f"\n再见！感谢使用 Forge AI Code!")
            break

if __name__ == "__main__":
    main()
