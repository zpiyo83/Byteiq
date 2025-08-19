#!/usr/bin/env python3
"""
Forge AI Code - AI编程助手命令行工具
主程序入口
"""

from colorama import init
from src.ui import print_welcome_screen
from src.input_handler import get_input_in_box
from src.command_processor import process_command
from src.output_monitor import enable_print_monitoring

# 初始化colorama以支持Windows终端颜色
init(autoreset=True)

# 启用全局输出监控
enable_print_monitoring()

def main():
    """主程序入口"""
    try:
        print_welcome_screen()
    except Exception as e:
        # 如果欢迎界面出错，使用基本输出
        import sys
        sys.__stdout__.write("Forge AI Code - AI编程助手\n")
        sys.__stdout__.write("欢迎界面加载失败，但程序可以正常使用\n")
        sys.__stdout__.flush()

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
            try:
                print(f"\n再见！感谢使用 Forge AI Code!")
            except Exception:
                # 如果colorama出错，使用基本输出
                import sys
                sys.__stdout__.write("\n再见！感谢使用 Forge AI Code!\n")
                sys.__stdout__.flush()
            break
        except EOFError:
            try:
                print(f"\n再见！感谢使用 Forge AI Code!")
            except Exception:
                # 如果colorama出错，使用基本输出
                import sys
                sys.__stdout__.write("\n再见！感谢使用 Forge AI Code!\n")
                sys.__stdout__.flush()
            break
        except Exception as e:
            try:
                print(f"\n程序出现异常: {e}")
                print("正在安全退出...")
            except Exception:
                # 如果colorama出错，使用基本输出
                import sys
                sys.__stdout__.write(f"\n程序出现异常: {e}\n")
                sys.__stdout__.write("正在安全退出...\n")
                sys.__stdout__.flush()
            break

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
    finally:
        # 清理资源
        try:
            from src.output_monitor import disable_print_monitoring, stop_output_monitoring
            stop_output_monitoring()
            disable_print_monitoring()
        except Exception:
            pass
