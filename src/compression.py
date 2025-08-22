"""
上下文压缩模块
"""

import sys
import re
from colorama import Fore, Style

# 这是一个简化的键盘监听器，后续会完善
# 在Windows上，可以使用msvcrt
# try:
#     import msvcrt
# except ImportError:
#     msvcrt = None

def show_compression_menu():
    """显示一个交互式菜单，支持箭头、数字和回车键。"""
    try:
        import msvcrt
    except ImportError:
        # 如果不是Windows系统，则回退到简单的数字输入模式
        return _fallback_menu()

    options = [
        ("Intelligent context compression", "intelligent"),
        ("AI context compression", "ai")
    ]
    selected_index = 0

    # ANSI转义码，用于控制光标
    CURSOR_UP = '\x1b[A'
    CLEAR_LINE = '\x1b[K'

    def print_menu():
        # 第一次打印时不需要上移光标
        if not hasattr(print_menu, "first_run"):
            print_menu.first_run = True
        else:
            # 上移光标以覆盖旧菜单
            sys.stdout.write(CURSOR_UP * (len(options) + 2))

        sys.stdout.write(f"\n{Fore.CYAN}请选择上下文压缩模式:{Style.RESET_ALL}\n")
        for i, (text, _) in enumerate(options):
            line = f"  {text}"
            if i == selected_index:
                sys.stdout.write(f"{Fore.GREEN}> {line}{Style.RESET_ALL}{CLEAR_LINE}\n")
            else:
                sys.stdout.write(f"  {line}{CLEAR_LINE}\n")
        sys.stdout.flush()

    print_menu()

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()

            # 检查是否是特殊键（如箭头）
            if key == b'\xe0':
                arrow = msvcrt.getch()
                if arrow == b'H':  # 上箭头
                    selected_index = (selected_index - 1 + len(options)) % len(options)
                    print_menu()
                elif arrow == b'P':  # 下箭头
                    selected_index = (selected_index + 1) % len(options)
                    print_menu()

            # 回车键
            elif key == b'\r':
                # 清理菜单并返回结果
                sys.stdout.write(CURSOR_UP * (len(options) + 2))
                sys.stdout.write("\x1b[J") # 清除从光标到屏幕末尾的内容
                return options[selected_index][1]

            # 数字键
            elif key in [b'1', b'2']:
                sys.stdout.write(CURSOR_UP * (len(options) + 2))
                sys.stdout.write("\x1b[J")
                choice = int(key.decode()) - 1
                if 0 <= choice < len(options):
                    return options[choice][1]

            # Q键或ESC键退出
            elif key in [b'q', b'Q', b'\x1b']:
                sys.stdout.write(CURSOR_UP * (len(options) + 2))
                sys.stdout.write("\x1b[J")
                print(f"{Fore.YELLOW}操作已取消。{Style.RESET_ALL}")
                return None

def _fallback_menu():
    """为非Windows系统提供的简化版菜单。"""
    options = {
        "1": ("Intelligent context compression", "intelligent"),
        "2": ("AI context compression", "ai")
    }
    print(f"\n{Fore.CYAN}请选择上下文压缩模式:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}1. {options['1'][0]}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}2. {options['2'][0]}{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}q. 取消{Style.RESET_ALL}")

    while True:
        choice = input(f"\n{Fore.WHITE}请输入选项 > {Style.RESET_ALL}").strip().lower()
        if choice in options:
            return options[choice][1]
        elif choice in ['q', 'quit', 'exit']:
            print(f"{Fore.YELLOW}操作已取消。{Style.RESET_ALL}")
            return None
        else:
            print(f"{Fore.RED}无效的输入，请重新选择。{Style.RESET_ALL}")


def compress_context(compression_type):
    """根据所选类型执行上下文压缩"""
    from .ai_client import ai_client

    print(f"\n{Fore.CYAN}正在执行 {compression_type} 压缩...{Style.RESET_ALL}")

    history = ai_client.get_history()
    original_length = len(history)
    new_history = []

    if compression_type == "intelligent":
        new_history = _intelligent_compression(history)
    elif compression_type == "ai":
        new_history = _ai_compression(history)
    else:
        return

    ai_client.set_history(new_history)

    if len(new_history) < original_length:
        print(f"{Fore.GREEN}✓ 上下文压缩完成! (从 {original_length} 条消息压缩至 {len(new_history)} 条){Style.RESET_ALL}")
    else:
        # 如果长度没变（例如历史太短），也给用户一个反馈
        print(f"{Fore.YELLOW}上下文无需压缩。{Style.RESET_ALL}")

def _intelligent_compression(history):
    """智能压缩算法：保留最近3轮对话，简化更早的AI工具调用。"""
    # 每轮对话包含user和assistant两条消息，所以是6条
    if len(history) <= 6:
        return history

    recent_history = history[-6:]
    old_history = history[:-6]

    compressed_old_history = []

    # 正则表达式，用于匹配整个工具调用XML块
    tool_call_pattern = re.compile(r'<(\w+)>[\s\S]*?</\1>', re.DOTALL)
    # 正则表达式，用于从工具内容中提取路径
    path_pattern = re.compile(r'"path"\s*:\s*"(.*?)"')

    for message in old_history:
        if message['role'] == 'user':
            compressed_old_history.append(message)
            continue

        if message['role'] == 'assistant':
            content = message.get('content', '')
            if not content:
                compressed_old_history.append(message)
                continue

            tool_calls = tool_call_pattern.findall(content)
            text_content = tool_call_pattern.sub('', content).strip()

            summaries = []
            if text_content:
                summaries.append(text_content)

            if tool_calls:
                # 提取工具调用的摘要
                for tool_xml in tool_call_pattern.finditer(content):
                    tool_name = tool_xml.group(1)
                    tool_content = tool_xml.group(0)

                    path_match = path_pattern.search(tool_content)
                    if path_match:
                        file_path = path_match.group(1)
                        summaries.append(f"[AI 使用了工具: {tool_name}, 操作了文件: {file_path}]")
                    else:
                        summaries.append(f"[AI 使用了工具: {tool_name}]")

            if summaries:
                compressed_content = "\n".join(summaries)
                compressed_old_history.append({'role': 'assistant', 'content': compressed_content})
            else:
                # 如果没有文本也没有工具，保留原样
                compressed_old_history.append(message)

    return compressed_old_history + recent_history

def _ai_compression(history):
    """使用AI来压缩历史记录"""
    from .ai_client import ai_client

    if len(history) < 3:
        # 如果历史太短，不进行压缩
        return history

    # 将历史记录格式化为纯文本
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

    # 构建压缩提示
    prompt = f"""
请将以下对话历史压缩成一段简洁的摘要，保留关键信息、代码片段和文件修改。摘要应清晰地反映对话的进展和最终结果。

原始对话历史:
---
{history_text}
---

请输出压缩后的摘要:
"""

    print(f"{Fore.CYAN}正在请求AI进行上下文摘要...{Style.RESET_ALL}")

    # 调用AI进行压缩
    # 我们创建一个新的临时的ai_client实例，或者添加一个特殊方法来处理这种一次性请求
    # 这里为了简单，我们假设ai_client可以处理这种请求
    # 注意：这可能会污染当前会话的历史，需要小心处理
    # 一个更好的方法是有一个独立的函数来调用AI API
    from .ai_client import AIClient
    temp_client = AIClient()

    # 确保临时客户端有API密钥
    from .config import load_config
    config = load_config()
    if not config.get('api_key'):
        print(f"{Fore.RED}错误：无法执行AI压缩，因为缺少API密钥。{Style.RESET_ALL}")
        return history # 返回原始历史
    temp_client.api_key = config.get('api_key')
    temp_client.model = config.get('model', 'gpt-3.5-turbo')

    summary_response = temp_client.send_message(prompt, include_structure=False) # 不包含项目结构，也不包含历史（因为是临时客户端）

    if summary_response and 'content' in summary_response:
        summary_text = summary_response['content']
        # 创建一个新的历史记录，包含系统消息和AI生成的摘要
        new_history = [
            {'role': 'system', 'content': '这是先前对话的摘要。'},
            {'role': 'assistant', 'content': summary_text}
        ]
        return new_history
    else:
        print(f"{Fore.RED}AI摘要失败，返回原始历史记录。{Style.RESET_ALL}")
        return history

