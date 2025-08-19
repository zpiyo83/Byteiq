#!/usr/bin/env python3
"""
Forge AI Code - AI编程助手命令行工具
"""

import os
import sys
import json
import getpass
import requests
import threading
import time
import re
import subprocess
from colorama import Fore, Style, init

# 尝试导入实时输入相关的库
try:
    import msvcrt  # Windows
    WINDOWS = True
except ImportError:
    try:
        import termios
        import tty
        import select
        WINDOWS = False
    except ImportError:
        WINDOWS = None  # 不支持实时输入

# 初始化colorama以支持Windows终端颜色
init(autoreset=True)

# ========== 模式管理 ==========
AVAILABLE_MODES = ["Ask", "mostly accepted", "sprint"]
current_mode = "Ask"  # 默认模式

def get_current_mode():
    """获取当前模式"""
    return current_mode

def switch_mode():
    """切换到下一个模式"""
    global current_mode
    current_index = AVAILABLE_MODES.index(current_mode)
    next_index = (current_index + 1) % len(AVAILABLE_MODES)
    current_mode = AVAILABLE_MODES[next_index]
    return current_mode

def get_mode_description(mode):
    """获取模式描述"""
    descriptions = {
        "Ask": "询问模式 - 标准问答交互",
        "mostly accepted": "大部分接受模式 - 快速确认建议",
        "sprint": "冲刺模式 - 快速开发迭代"
    }
    return descriptions.get(mode, "未知模式")

def handle_mode_switch_command(user_input):
    """处理模式切换命令（简化实现）"""
    # 检查是否是模式切换命令
    if user_input.lower() in ['/mode', '/m', 'alt+l']:
        show_mode_switch_notification()
        return True
    return False

def show_mode_switch_notification():
    """显示模式切换通知"""
    new_mode = switch_mode()
    description = get_mode_description(new_mode)
    print(f"\n{Fore.LIGHTCYAN_EX}🔄 模式已切换: {new_mode}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   {description}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   按 Alt+L 继续切换模式{Style.RESET_ALL}\n")

# ========== 配置管理 ==========
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".forgeai_config.json")

def load_config():
    """加载配置文件"""
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(cfg: dict):
    """保存配置文件"""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"{Fore.RED}保存配置失败: {e}{Style.RESET_ALL}")
        return False

def set_api_key_interactive():
    """交互式设置 API 密钥"""
    cfg = load_config()
    print(f"\n{Fore.CYAN}API 密钥设置{Style.RESET_ALL}")
    print(f"配置文件位置: {CONFIG_PATH}")

    existing = cfg.get("api_key")
    if existing:
        print(f"{Fore.YELLOW}当前已设置 API Key (已隐藏显示){Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}尚未设置 API Key{Style.RESET_ALL}")

    # 使用 getpass 隐藏输入
    try:
        new_key = getpass.getpass("请输入新的 API Key (输入将被隐藏，回车跳过): ")
    except Exception:
        new_key = input("请输入新的 API Key (回车跳过): ")

    if new_key.strip():
        cfg["api_key"] = new_key.strip()
        if save_config(cfg):
            print(f"{Fore.GREEN}✓ API Key 已保存成功！{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ API Key 保存失败{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}未修改 API Key{Style.RESET_ALL}")

def set_language_interactive():
    """交互式设置语言"""
    cfg = load_config()
    current_lang = cfg.get("language", "zh-CN")

    print(f"\n{Fore.CYAN}语言设置{Style.RESET_ALL}")
    print(f"当前语言: {current_lang}")
    print(f"\n{Fore.CYAN}可选语言:{Style.RESET_ALL}")
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
        cfg["language"] = lang_map[choice]
        if save_config(cfg):
            print(f"{Fore.GREEN}✓ 语言设置已保存！{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ 语言设置保存失败{Style.RESET_ALL}")
    elif choice == "":
        print(f"{Fore.CYAN}语言设置未修改{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}无效选择{Style.RESET_ALL}")

def set_model_interactive():
    """交互式设置AI模型"""
    cfg = load_config()
    current_model = cfg.get("model", "gpt-3.5-turbo")

    print(f"\n{Fore.CYAN}AI模型设置{Style.RESET_ALL}")
    print(f"当前模型: {current_model}")
    print(f"\n{Fore.CYAN}常用模型示例:{Style.RESET_ALL}")
    print(f"  gpt-3.5-turbo, gpt-4, gpt-4-turbo")
    print(f"  claude-3-haiku, claude-3-sonnet, claude-3-opus")
    print(f"  gemini-pro, llama2-70b, 等...")
    print(f"\n{Fore.YELLOW}提示: 直接输入模型名称，回车保持不变{Style.RESET_ALL}")

    new_model = input(f"\n{Fore.WHITE}请输入模型名称 > {Style.RESET_ALL}").strip()

    if new_model:
        cfg["model"] = new_model
        if save_config(cfg):
            print(f"{Fore.GREEN}✓ AI模型设置已保存: {new_model}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ AI模型设置保存失败{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}AI模型设置未修改{Style.RESET_ALL}")

def show_settings():
    """显示设置菜单"""
    while True:
        cfg = load_config()
        api_key_status = "已设置 ********" if cfg.get("api_key") else "未设置"
        language_status = cfg.get("language", "zh-CN")
        model_status = cfg.get("model", "gpt-3.5-turbo")

        print(f"\n{Fore.LIGHTCYAN_EX}⚙️  Forge AI Code 设置{Style.RESET_ALL}")
        print(f"{'='*50}")
        print(f"API Key: {api_key_status}")
        print(f"语言: {language_status}")
        print(f"AI模型: {model_status}")
        print(f"配置文件: {CONFIG_PATH}")
        print(f"{'='*50}")
        print(f"\n{Fore.CYAN}请选择操作:{Style.RESET_ALL}")
        print(f"  1 - 设置语言")
        print(f"  2 - 设置API密钥")
        print(f"  3 - 设置模型")
        print(f"  4 - 退出设置")

        choice = input(f"\n{Fore.WHITE}请输入选项 (1-4) > {Style.RESET_ALL}").strip()

        if choice == "1":
            set_language_interactive()
        elif choice == "2":
            set_api_key_interactive()
        elif choice == "3":
            set_model_interactive()
        elif choice == "4":
            print(f"{Fore.CYAN}退出设置{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.YELLOW}无效选择，请输入 1-4{Style.RESET_ALL}")
            input(f"{Fore.CYAN}按回车继续...{Style.RESET_ALL}")

# ========== AI功能 ==========
DEFAULT_API_URL = "https://www.lumjf.com/v1/chat/completions"

class AIClient:
    """AI客户端类"""

    def __init__(self):
        self.config = load_config()
        self.api_url = DEFAULT_API_URL
        self.conversation_history = []
        self.is_loading = False
        self.loading_thread = None

    def get_system_prompt(self):
        """获取系统提示词"""
        return """你是Forge AI Code，一个专业的CLI AI编程助手。你可以帮助用户进行编程开发。

你有以下工具可以使用：

1. **读取文件**
格式：<read_file><path>文件路径</path></read_file>

2. **写入文件**（覆盖写入）
格式：<write_file><path>文件路径</path><content>文件内容</content></write_file>

3. **创建文件**
格式：<create_file><path>文件路径</path><content>文件内容</content></create_file>

4. **执行命令**
格式：<execute_command><command>命令内容</command></execute_command>

5. **结束任务**
格式：<task_complete><summary>任务总结</summary></task_complete>

**重要规则：**
1. 当你需要使用工具时，必须严格使用XML格式，不要有任何其他文本
2. 每次只能使用一个工具，等待执行结果后再继续
3. 不要在XML标签外添加额外的解释文本
4. 创建文件时会自动创建必要的目录结构
5. 完成所有操作后使用task_complete结束任务

**示例：**
正确：<create_file><path>app.py</path><content>print("hello")</content></create_file>
错误：我要创建文件 <create_file>...

请始终保持专业、高效，严格遵循XML格式。"""

    def get_project_structure(self, path=".", max_depth=3, current_depth=0):
        """获取项目结构"""
        if current_depth >= max_depth:
            return ""

        structure = ""
        try:
            items = sorted(os.listdir(path))
            for item in items:
                if item.startswith('.'):
                    continue

                item_path = os.path.join(path, item)
                indent = "  " * current_depth

                if os.path.isdir(item_path):
                    structure += f"{indent}{item}/\n"
                    structure += self.get_project_structure(item_path, max_depth, current_depth + 1)
                else:
                    structure += f"{indent}{item}\n"
        except PermissionError:
            pass

        return structure

    def start_loading_animation(self):
        """启动加载动画"""
        self.is_loading = True
        self.loading_thread = threading.Thread(target=self._loading_animation)
        self.loading_thread.daemon = True
        self.loading_thread.start()

    def stop_loading_animation(self):
        """停止加载动画"""
        self.is_loading = False
        if self.loading_thread:
            self.loading_thread.join(timeout=1)
        print("\r" + " " * 50 + "\r", end="", flush=True)  # 清除动画

    def _loading_animation(self):
        """加载动画实现"""
        frames = [
            "● ●●   ",
            "●● ●  ",
            "● ● ● ",
            "●●●   ",
            "● ●● "
        ]
        frame_index = 0

        while self.is_loading:
            print(f"\r{Fore.CYAN}AI思考中... {frames[frame_index]}{Style.RESET_ALL}", end="", flush=True)
            frame_index = (frame_index + 1) % len(frames)
            time.sleep(0.5)

    def send_message(self, user_input, include_structure=True):
        """发送消息给AI"""
        try:
            # 构建消息
            messages = [{"role": "system", "content": self.get_system_prompt()}]

            # 添加历史对话
            messages.extend(self.conversation_history)

            # 构建用户消息
            user_message = user_input
            if include_structure:
                structure = self.get_project_structure()
                if structure.strip():
                    user_message += f"\n\n当前项目结构：\n```\n{structure}```"
                else:
                    user_message += "\n\n当前项目结构：空"

            messages.append({"role": "user", "content": user_message})

            # 准备请求数据
            data = {
                "model": self.config.get("model", "gpt-3.5-turbo"),
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.get('api_key', '')}"
            }

            # 启动加载动画
            self.start_loading_animation()

            # 发送请求
            response = requests.post(self.api_url, json=data, headers=headers, timeout=30)

            # 停止加载动画
            self.stop_loading_animation()

            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']

                # 保存对话历史
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": ai_response})

                # 限制历史长度
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]

                return ai_response
            else:
                return f"API请求失败: {response.status_code} - {response.text}"

        except requests.exceptions.Timeout:
            self.stop_loading_animation()
            return "请求超时，请检查网络连接"
        except requests.exceptions.RequestException as e:
            self.stop_loading_animation()
            return f"网络错误: {str(e)}"
        except Exception as e:
            self.stop_loading_animation()
            return f"发生错误: {str(e)}"

    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []

# 全局AI客户端实例
ai_client = AIClient()

class AIToolProcessor:
    """AI工具处理器"""

    def __init__(self):
        self.tools = {
            'read_file': self.read_file,
            'write_file': self.write_file,
            'create_file': self.create_file,
            'execute_command': self.execute_command,
            'task_complete': self.task_complete
        }

    def process_response(self, ai_response):
        """处理AI响应，提取和执行工具调用"""
        # 查找XML工具调用
        tool_patterns = {
            'read_file': r'<read_file><path>(.*?)</path></read_file>',
            'write_file': r'<write_file><path>(.*?)</path><content>(.*?)</content></write_file>',
            'create_file': r'<create_file><path>(.*?)</path><content>(.*?)</content></create_file>',
            'execute_command': r'<execute_command><command>(.*?)</command></execute_command>',
            'task_complete': r'<task_complete><summary>(.*?)</summary></task_complete>'
        }

        # 检查是否有不完整的XML标签
        incomplete_patterns = [
            r'<create_file><path>([^<]*?)$',
            r'<write_file><path>([^<]*?)$',
            r'<read_file><path>([^<]*?)$'
        ]

        for pattern in incomplete_patterns:
            if re.search(pattern, ai_response, re.DOTALL):
                return {
                    'has_tool': False,
                    'tool_result': "检测到不完整的XML标签，请AI重新发送完整的工具调用",
                    'display_text': "XML格式不完整，等待AI重新发送...",
                    'should_continue': False
                }

        tool_found = False
        tool_result = ""
        display_text = ai_response

        for tool_name, pattern in tool_patterns.items():
            matches = re.findall(pattern, ai_response, re.DOTALL)
            if matches:
                tool_found = True
                if tool_name in ['write_file', 'create_file']:
                    path, content = matches[0]
                    tool_result = self.tools[tool_name](path.strip(), content.strip())
                    # 显示操作信息
                    action = "创建文件" if tool_name == 'create_file' else "写入文件"
                    content_preview = self._get_content_preview(content.strip())
                    display_text = f"{action} {path.strip()}:\n{content_preview}"
                elif tool_name == 'read_file':
                    path = matches[0].strip()
                    tool_result = self.tools[tool_name](path)
                    display_text = f"读取文件 {path}"
                elif tool_name == 'execute_command':
                    command = matches[0].strip()
                    tool_result = self.tools[tool_name](command)
                    display_text = f"执行命令: {command}"
                elif tool_name == 'task_complete':
                    summary = matches[0].strip()
                    tool_result = self.tools[tool_name](summary)
                    display_text = f"任务完成: {summary}"
                break

        # 如果没有工具调用，移除XML标签显示纯文本
        if not tool_found:
            display_text = self._remove_xml_tags(ai_response)

        return {
            'has_tool': tool_found,
            'tool_result': tool_result,
            'display_text': display_text,
            'should_continue': tool_found and not 'task_complete' in ai_response
        }

    def _get_content_preview(self, content, max_lines=5):
        """获取内容预览（前5行）"""
        lines = content.split('\n')
        if len(lines) <= max_lines:
            return content
        else:
            preview_lines = lines[:max_lines]
            return '\n'.join(preview_lines) + f"\n... (还有 {len(lines) - max_lines} 行)"

    def _remove_xml_tags(self, text):
        """移除XML标签"""
        # 移除所有XML标签
        clean_text = re.sub(r'<[^>]+>', '', text)
        return clean_text.strip()

    def read_file(self, path):
        """读取文件工具"""
        try:
            if not os.path.exists(path):
                return f"错误：文件 {path} 不存在"

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            return f"成功读取文件 {path}，内容长度: {len(content)} 字符"
        except Exception as e:
            return f"读取文件失败: {str(e)}"

    def write_file(self, path, content):
        """写入文件工具"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"成功写入文件 {path}"
        except Exception as e:
            return f"写入文件失败: {str(e)}"

    def create_file(self, path, content):
        """创建文件工具"""
        try:
            if os.path.exists(path):
                return f"警告：文件 {path} 已存在，将覆盖"

            # 确保目录存在
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"成功创建文件 {path}"
        except Exception as e:
            return f"创建文件失败: {str(e)}"

    def execute_command(self, command):
        """执行命令工具"""
        try:
            # 安全检查 - 禁止危险命令
            dangerous_commands = ['rm -rf', 'del /f', 'format', 'fdisk', 'mkfs']
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                return "错误：禁止执行危险命令"

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout + result.stderr
            return_code = result.returncode

            if return_code == 0:
                return f"命令执行成功:\n{output}" if output else "命令执行成功"
            else:
                return f"命令执行失败 (返回码: {return_code}):\n{output}"

        except subprocess.TimeoutExpired:
            return "命令执行超时"
        except Exception as e:
            return f"执行命令失败: {str(e)}"

    def task_complete(self, summary):
        """任务完成工具"""
        return f"任务已完成: {summary}"

# 全局工具处理器实例
ai_tool_processor = AIToolProcessor()

def process_ai_conversation(user_input):
    """处理AI对话"""
    # 检查是否配置了API密钥
    config = load_config()
    if not config.get('api_key'):
        print(f"{Fore.RED}错误：请先设置API密钥。使用 /s 命令进入设置。{Style.RESET_ALL}")
        return

    print(f"{Fore.CYAN}🤖 AI助手正在处理您的请求...{Style.RESET_ALL}")

    # 发送消息给AI
    ai_response = ai_client.send_message(user_input)

    # 处理AI响应和工具调用
    while True:
        result = ai_tool_processor.process_response(ai_response)

        # 显示AI的意图（过滤XML）
        if result['display_text'].strip():
            print(f"\n{Fore.GREEN}🤖 AI: {result['display_text']}{Style.RESET_ALL}")

        # 如果有工具调用，显示结果
        if result['has_tool'] and result['tool_result']:
            print(f"{Fore.YELLOW}📋 执行结果: {result['tool_result']}{Style.RESET_ALL}")

        # 如果需要继续（有工具调用且未完成），继续对话
        if result['should_continue']:
            print(f"\n{Fore.CYAN}🤖 AI继续处理...{Style.RESET_ALL}")
            # 将工具执行结果发送回AI
            ai_response = ai_client.send_message(f"工具执行结果: {result['tool_result']}", include_structure=False)
        else:
            break

    print()  # 空行分隔

def get_wave_icon():
    """生成音符条样式的图标 - 3个点横向排列"""
    # 横向排列的3个圆点
    icon = [
        "●●●"
    ]
    return icon

def get_forge_ai_ascii():
    """生成FORGE AI CODE的ASCII艺术字"""
    ascii_art = [
        "███████╗ ██████╗ ██████╗  ██████╗ ███████╗",
        "██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝",
        "█████╗  ██║   ██║██████╔╝██║  ███╗█████╗  ",
        "██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  ",
        "██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗",
        "╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝",
        "",
        " █████╗ ██╗     ██████╗  ██████╗ ██████╗ ███████╗",
        "██╔══██╗██║    ██╔════╝ ██╔═══██╗██╔══██╗██╔════╝",
        "███████║██║    ██║      ██║   ██║██║  ██║█████╗  ",
        "██╔══██║██║    ██║      ██║   ██║██║  ██║██╔══╝  ",
        "██║  ██║██║    ╚██████╗ ╚██████╔╝██████╔╝███████╗",
        "╚═╝  ╚═╝╚═╝     ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝"
    ]
    return ascii_art

def print_welcome_screen():
    """打印欢迎界面"""
    # 清屏
    os.system('cls' if os.name == 'nt' else 'clear')

    # 获取当前工作目录
    current_dir = os.getcwd()

    # 淡蓝色主题颜色
    light_blue = Fore.LIGHTCYAN_EX
    blue = Fore.CYAN
    white = Fore.WHITE

    # 先打印ASCII艺术字标题
    ascii_art = get_forge_ai_ascii()
    for line in ascii_art:
        print(f"{light_blue}{line}{Style.RESET_ALL}")

    print()

    # 打印带边框的欢迎信息框
    box_width = 50

    # 获取图标
    icon = get_wave_icon()

    # 顶部边框（圆角）
    print(f"{light_blue}╭{'─' * (box_width - 2)}╮{Style.RESET_ALL}")

    # 图标和欢迎信息行
    print(f"{light_blue}│{Style.RESET_ALL}{light_blue}{icon[0]}{Style.RESET_ALL} {white}Welcome to Forge AI Code!{' ' * (box_width - len(icon[0]) - 26)}{light_blue}│{Style.RESET_ALL}")

    # 其余图标行
    for i in range(1, len(icon)):
        print(f"{light_blue}│{Style.RESET_ALL}{light_blue}{icon[i]}{' ' * (box_width - len(icon[i]) - 2)}{Style.RESET_ALL}{light_blue}│{Style.RESET_ALL}")

    # 空行
    print(f"{light_blue}│{' ' * (box_width - 2)}│{Style.RESET_ALL}")

    # 帮助信息行
    help_text = "/help for help, /status for your current setup"
    print(f"{light_blue}│{Style.RESET_ALL} {blue}{help_text}{' ' * (box_width - len(help_text) - 3)}{Style.RESET_ALL}{light_blue}│{Style.RESET_ALL}")

    # 空行
    print(f"{light_blue}│{' ' * (box_width - 2)}│{Style.RESET_ALL}")

    # 当前目录行
    cwd_text = f"cwd: {current_dir}"
    if len(cwd_text) > box_width - 3:
        cwd_text = f"cwd: ...{current_dir[-(box_width - 10):]}"
    print(f"{light_blue}│{Style.RESET_ALL} {white}{cwd_text}{' ' * (box_width - len(cwd_text) - 3)}{Style.RESET_ALL}{light_blue}│{Style.RESET_ALL}")

    # 空行
    print(f"{light_blue}│{' ' * (box_width - 2)}│{Style.RESET_ALL}")

    # 当前模式行
    mode_text = f"Mode: {get_current_mode()} (Alt+L to switch)"
    print(f"{light_blue}│{Style.RESET_ALL} {Fore.YELLOW}{mode_text}{' ' * (box_width - len(mode_text) - 3)}{Style.RESET_ALL}{light_blue}│{Style.RESET_ALL}")

    # 底部边框（圆角）
    print(f"{light_blue}╰{'─' * (box_width - 2)}╯{Style.RESET_ALL}")
    print()

    # 显示输入框
    print_input_box()

def print_input_box():
    """打印输入框，并保存起始光标位置以便后续精确定位"""
    gray = Fore.LIGHTBLACK_EX  # 灰色

    # 保存当前光标位置（作为输入框左上角参考点）
    print('\033[s', end='', flush=True)

    # 输入框宽度 - 增加长度以匹配图片要求
    input_box_width = 110

    # 输入框顶部边框（圆角，灰色）
    print(f"{gray}╭{'─' * (input_box_width - 2)}╮{Style.RESET_ALL}")

    # 输入框内容行 - 空的，没有占位符
    print(f"{gray}│{' ' * (input_box_width - 2)}│{Style.RESET_ALL}")

    # 输入框底部边框（圆角，灰色）
    print(f"{gray}╰{'─' * (input_box_width - 2)}╯{Style.RESET_ALL}")

    # Ask 提示文字（灰色）
    print(f"{gray}? Ask{Style.RESET_ALL}")

def get_available_commands():
    """获取所有可用命令"""
    return [
        "/help", "/status", "/clear", "/pwd", "/ls", "/cd", "/exit",
        "/s", "/mode", "/clear-history"
    ]

def get_command_descriptions():
    """获取命令描述"""
    return {
        "/help": "显示帮助信息",
        "/status": "显示当前状态",
        "/clear": "清屏",
        "/pwd": "显示当前目录",
        "/ls": "列出当前目录文件",
        "/cd": "切换目录",
        "/exit": "退出程序",
        "/chat": "与AI助手对话",
        "/code": "AI代码生成",
        "/review": "代码审查",
        "/debug": "调试帮助",
        "/s": "设置API密钥",
        "/mode": "切换工作模式"
    }

def filter_commands(partial_input):
    """根据输入过滤命令"""
    if not partial_input.startswith('/'):
        return []

    commands = get_available_commands()

    # 如果只输入了 "/"，显示所有命令
    if partial_input == '/':
        return commands

    # 否则过滤匹配的命令
    filtered = [cmd for cmd in commands if cmd.startswith(partial_input.lower())]
    return filtered

def show_command_suggestions(suggestions, highlight_index=0):
    """显示命令建议"""
    if not suggestions:
        return

    gray = Fore.LIGHTBLACK_EX
    white = Fore.WHITE
    light_blue = Fore.LIGHTCYAN_EX

    print()
    for i, cmd in enumerate(suggestions[:5]):  # 最多显示5个建议
        if i == highlight_index:
            # 高亮显示第一个建议
            print(f"{light_blue}{cmd}{Style.RESET_ALL}")
        else:
            print(f"{gray}{cmd}{Style.RESET_ALL}")

def get_char():
    """跨平台获取单个字符输入"""
    if WINDOWS:
        return msvcrt.getch().decode('utf-8', errors='ignore')
    elif WINDOWS is False:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    else:
        # 回退到普通输入
        return input()

def clear_line():
    """清除当前行"""
    print('\r' + ' ' * 120 + '\r', end='', flush=True)

def move_cursor_up(lines):
    """向上移动光标"""
    print(f'\033[{lines}A', end='', flush=True)

def move_cursor_down(lines):
    """向下移动光标"""
    print(f'\033[{lines}B', end='', flush=True)

def position_cursor_for_input():
    """恢复到输入框起点，再相对移动到内容行内的提示符位置"""
    # 恢复到 print_input_box 保存的位置（输入框左上角）
    print('\033[u', end='', flush=True)
    # 下移1行到内容行，右移2列到竖线内侧
    print('\033[1B\033[2C', end='', flush=True)

def clear_suggestions():
    """清除建议显示区域"""
    # 清除下方3行
    for _ in range(3):
        print('\033[1B\033[2K', end='', flush=True)
    # 回到原位置
    print('\033[3A', end='', flush=True)

def show_inline_suggestion(current_input):
    """在输入行显示内联建议"""
    if not current_input.startswith('/'):
        return ""

    suggestions = filter_commands(current_input)
    if not suggestions or current_input in get_available_commands():
        return ""

    # 返回第一个建议的剩余部分
    first_suggestion = suggestions[0]
    if first_suggestion.startswith(current_input):
        return first_suggestion[len(current_input):]
    return ""

def show_suggestion_popup(current_input):
    """在下方显示建议弹窗"""
    if not current_input.startswith('/'):
        return

    suggestions = filter_commands(current_input)
    if not suggestions or current_input in get_available_commands():
        return

    gray = Fore.LIGHTBLACK_EX
    descriptions = get_command_descriptions()

    # 保存当前光标位置
    print('\033[s', end='', flush=True)

    # 移动到下一行显示建议
    print('\n', end='', flush=True)

    # 显示第一个建议
    first_suggestion = suggestions[0]
    desc = descriptions.get(first_suggestion, "")
    print(f"{gray}💡 {first_suggestion} - {desc}{Style.RESET_ALL}")

    # 恢复光标位置
    print('\033[u', end='', flush=True)

def show_command_preview(partial_input):
    """显示命令预览（灰色提示）"""
    if not partial_input.startswith('/') or len(partial_input) <= 1:
        return ""

    suggestions = filter_commands(partial_input)
    if not suggestions:
        return ""

    # 返回第一个匹配的命令作为预览
    best_match = suggestions[0]
    if best_match.startswith(partial_input):
        # 返回剩余部分作为灰色提示
        return best_match[len(partial_input):]
    return ""

def get_input_with_live_suggestions():
    """带实时命令建议的输入（类似Claude Code）"""
    white = Fore.WHITE
    gray = Fore.LIGHTBLACK_EX

    # 移动光标到输入框内
    position_cursor_for_input()

    # 显示提示符
    print(f"{white}> {Style.RESET_ALL}", end="", flush=True)

    # 获取用户输入
    user_input = input()

    # 显示命令建议
    if user_input.startswith('/') and len(user_input) > 1:
        suggestions = filter_commands(user_input)
        if suggestions and user_input not in get_available_commands():
            print(f"\n{gray}建议命令:{Style.RESET_ALL}")
            descriptions = get_command_descriptions()

            # 显示前3个建议
            for i, cmd in enumerate(suggestions[:3]):
                desc = descriptions.get(cmd, "")
                if i == 0:
                    # 第一个建议高亮显示
                    print(f"  {Fore.LIGHTCYAN_EX}{cmd}{Style.RESET_ALL} {gray}- {desc}{Style.RESET_ALL}")
                else:
                    print(f"  {gray}{cmd} - {desc}{Style.RESET_ALL}")

            # 如果有精确匹配，询问是否使用第一个建议
            if suggestions[0].startswith(user_input):
                print(f"\n{gray}按Tab或Enter使用 {Fore.LIGHTCYAN_EX}{suggestions[0]}{Style.RESET_ALL}{gray}，或继续输入:{Style.RESET_ALL}")

                # 简单的选择机制
                try:
                    choice = input(f"{white}> {Style.RESET_ALL}")
                    if choice.strip() == "" or choice.strip().lower() == "tab":
                        user_input = suggestions[0]
                    elif choice.strip():
                        user_input = choice.strip()
                except:
                    pass

    return user_input.strip()

def get_input_with_suggestions():
    """带命令建议的简化输入（备用方案）"""
    gray = Fore.LIGHTBLACK_EX
    white = Fore.WHITE
    light_blue = Fore.LIGHTCYAN_EX

    # 移动光标到输入框内
    position_cursor_for_input()
    print(f"{white}> {Style.RESET_ALL}", end="", flush=True)

    # 获取用户输入
    user_input = input()

    # 如果输入以/开头但不完整，显示建议
    if user_input.startswith('/') and user_input not in get_available_commands():
        suggestions = filter_commands(user_input)
        if suggestions:
            print(f"\n{gray}建议命令:{Style.RESET_ALL}")
            for i, cmd in enumerate(suggestions[:3]):  # 显示前3个建议
                if i == 0:
                    print(f"  {light_blue}{cmd}{Style.RESET_ALL} {gray}(按Tab补全){Style.RESET_ALL}")
                else:
                    print(f"  {gray}{cmd}{Style.RESET_ALL}")

            # 询问是否使用第一个建议
            print(f"\n{gray}按Enter使用 {light_blue}{suggestions[0]}{Style.RESET_ALL}{gray}，或重新输入:{Style.RESET_ALL}")
            choice = input(f"{white}> {Style.RESET_ALL}")

            if choice.strip() == "":
                user_input = suggestions[0]
            elif choice.strip():
                user_input = choice.strip()

    return user_input.strip()

def get_input_with_simple_suggestions():
    """简化的建议输入 - 修复光标定位"""
    white = Fore.WHITE
    gray = Fore.LIGHTBLACK_EX

    # 正确移动光标到输入框内
    position_cursor_for_input()
    print(f"{white}> {Style.RESET_ALL}", end="", flush=True)

    # 使用简单的input()
    user_input = input()

    # 如果输入以/开头且不完整，显示建议
    if user_input.startswith('/') and user_input not in get_available_commands():
        suggestions = filter_commands(user_input)
        if suggestions:
            # 在下方显示建议
            print(f"\n{gray}💡 建议: {suggestions[0]} - {get_command_descriptions().get(suggestions[0], '')}{Style.RESET_ALL}")
            if len(suggestions) > 1:
                print(f"{gray}   其他选项: {', '.join(suggestions[1:3])}{Style.RESET_ALL}")
            print(f"{gray}   按Enter使用建议，或重新输入:{Style.RESET_ALL}")

            # 询问用户选择
            choice = input(f"{white}> {Style.RESET_ALL}")
            if choice.strip() == "":
                user_input = suggestions[0]
            elif choice.strip():
                user_input = choice.strip()

    return user_input.strip()

def get_input_with_real_time_suggestions():
    """真正的实时建议输入 - 类似Claude Code"""
    white = Fore.WHITE
    gray = Fore.LIGHTBLACK_EX

    # 正确移动光标到输入框内并显示提示符
    position_cursor_for_input()
    print(f"{white}> {Style.RESET_ALL}", end="", flush=True)

    current_input = ""
    last_suggestion_length = 0

    if WINDOWS is None:
        # 回退到简单建议
        return get_input_with_simple_suggestions()

    while True:
        try:
            char = get_char()

            # 处理特殊按键
            if char == '\r' or char == '\n':  # Enter键
                # 清除建议显示
                if last_suggestion_length > 0:
                    print('\033[K', end='', flush=True)  # 清除到行尾
                print()  # 换行
                break
            elif char == '\x08' or char == '\x7f':  # Backspace
                if current_input:
                    current_input = current_input[:-1]
                    # 清除整行并重新显示
                    print('\033[K', end='', flush=True)  # 清除到行尾
                    print(f"\r", end="", flush=True)
                    position_cursor_for_input()
                    print(f"{white}> {current_input}{Style.RESET_ALL}", end="", flush=True)
                    last_suggestion_length = 0

                    # 重新显示建议
                    if current_input.startswith('/') and current_input not in get_available_commands():
                        suggestions = filter_commands(current_input)
                        if suggestions:
                            suggestion_text = suggestions[0]
                            if suggestion_text.startswith(current_input):
                                remaining = suggestion_text[len(current_input):]
                                print(f"{gray}{remaining}{Style.RESET_ALL}", end="", flush=True)
                                last_suggestion_length = len(remaining)
            elif char == '\t':  # Tab键 - 补全第一个建议
                if current_input.startswith('/'):
                    suggestions = filter_commands(current_input)
                    if suggestions and current_input not in get_available_commands():
                        # 补全为第一个建议
                        current_input = suggestions[0]
                        print('\033[K', end='', flush=True)  # 清除到行尾
                        print(f"\r", end="", flush=True)
                        position_cursor_for_input()
                        print(f"{white}> {current_input}{Style.RESET_ALL}", end="", flush=True)
                        last_suggestion_length = 0
            elif char == '\x1b':  # Escape序列，忽略
                continue
            elif ord(char) >= 32 and ord(char) <= 126:  # 可打印字符
                current_input += char
                # 清除之前的建议
                if last_suggestion_length > 0:
                    print('\033[K', end='', flush=True)  # 清除到行尾

                # 更新显示
                print(f"\r", end="", flush=True)
                position_cursor_for_input()
                print(f"{white}> {current_input}{Style.RESET_ALL}", end="", flush=True)
                last_suggestion_length = 0

                # 显示新建议
                if current_input.startswith('/') and current_input not in get_available_commands():
                    suggestions = filter_commands(current_input)
                    if suggestions:
                        suggestion_text = suggestions[0]
                        if suggestion_text.startswith(current_input):
                            remaining = suggestion_text[len(current_input):]
                            print(f"{gray}{remaining}{Style.RESET_ALL}", end="", flush=True)
                            last_suggestion_length = len(remaining)

        except KeyboardInterrupt:
            return "/exit"
        except:
            continue

    return current_input.strip()

def get_input_with_claude_style():
    """Claude Code风格的输入 - 简化但可靠的版本"""
    white = Fore.WHITE
    gray = Fore.LIGHTBLACK_EX

    # 简单直接的光标定位到输入框
    position_cursor_for_input()
    print(f"{white}> {Style.RESET_ALL}", end="", flush=True)

    # 获取用户输入
    user_input = input()

    # 如果输入以/开头且不完整，显示建议
    if user_input.startswith('/') and user_input not in get_available_commands():
        suggestions = filter_commands(user_input)
        if suggestions:
            print(f"\n{gray}💡 建议: {suggestions[0]} - {get_command_descriptions().get(suggestions[0], '')}{Style.RESET_ALL}")
            if len(suggestions) > 1:
                print(f"{gray}   其他选项: {', '.join(suggestions[1:3])}{Style.RESET_ALL}")
            print(f"\n{gray}按Enter使用建议，或输入其他命令:{Style.RESET_ALL}")

            choice = input(f"{white}> {Style.RESET_ALL}")
            if choice.strip() == "":
                user_input = suggestions[0]
            elif choice.strip():
                user_input = choice.strip()

    return user_input.strip()

def get_input_in_box():
    """输入框输入 - 使用Claude风格建议输入"""
    try:
        # 尝试使用Claude风格建议功能
        return get_input_with_claude_style()
    except:
        # 如果失败，回退到简单建议
        return get_input_with_suggestions()

def show_help():
    """显示帮助信息"""
    help_text = f"""
{Fore.LIGHTCYAN_EX}Forge AI Code - 命令帮助{Style.RESET_ALL}

{Fore.CYAN}基础命令:{Style.RESET_ALL}
  {Fore.WHITE}/help{Style.RESET_ALL}     - 显示此帮助信息
  {Fore.WHITE}/status{Style.RESET_ALL}   - 显示当前状态
  {Fore.WHITE}/clear{Style.RESET_ALL}    - 清屏
  {Fore.WHITE}/pwd{Style.RESET_ALL}      - 显示当前目录
  {Fore.WHITE}/ls{Style.RESET_ALL}       - 列出当前目录文件
  {Fore.WHITE}/cd <dir>{Style.RESET_ALL} - 切换目录
  {Fore.WHITE}/exit{Style.RESET_ALL}     - 退出程序

{Fore.CYAN}AI功能:{Style.RESET_ALL}
  {Fore.GREEN}直接输入{Style.RESET_ALL}        - 与AI助手对话（无需命令前缀）
  {Fore.WHITE}/s{Style.RESET_ALL}        - 设置（API密钥、语言、模型）
  {Fore.WHITE}/mode{Style.RESET_ALL}     - 切换工作模式
  {Fore.WHITE}/clear-history{Style.RESET_ALL} - 清除AI对话历史

{Fore.CYAN}AI工具能力:{Style.RESET_ALL}
  {Fore.YELLOW}📖 读取文件{Style.RESET_ALL}     - AI可以读取项目文件
  {Fore.YELLOW}✏️  写入文件{Style.RESET_ALL}     - AI可以创建和修改文件
  {Fore.YELLOW}⚡ 执行命令{Style.RESET_ALL}     - AI可以执行系统命令
  {Fore.YELLOW}🎯 项目感知{Style.RESET_ALL}     - AI自动了解项目结构

{Fore.GREEN}💡 使用提示: 直接输入您的需求，AI会自动帮您完成编程任务！{Style.RESET_ALL}
"""
    print(help_text)

def show_status():
    """显示当前状态"""
    current_dir = os.getcwd()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    status_text = f"""
{Fore.LIGHTCYAN_EX}Forge AI Code - 当前状态{Style.RESET_ALL}

{Fore.CYAN}系统信息:{Style.RESET_ALL}
  {Fore.WHITE}当前目录:{Style.RESET_ALL} {Fore.CYAN}{current_dir}{Style.RESET_ALL}
  {Fore.WHITE}Python版本:{Style.RESET_ALL} {Fore.CYAN}{python_version}{Style.RESET_ALL}
  {Fore.WHITE}操作系统:{Style.RESET_ALL} {Fore.CYAN}{os.name}{Style.RESET_ALL}

{Fore.CYAN}AI功能状态:{Style.RESET_ALL}
  {Fore.YELLOW}所有AI功能正在开发中...{Style.RESET_ALL}
"""
    print(status_text)

def main():
    """主程序入口"""
    print_welcome_screen()

    while True:
        try:
            # 使用输入框内输入
            user_input = get_input_in_box()
            
            if not user_input or user_input.strip() == "":
                continue

            # 过滤掉特殊字符
            user_input = user_input.replace('\n', '').replace('\r', '').strip()
            if not user_input:
                continue

            # 检查是否是命令（以/开头）
            if not user_input.startswith('/'):
                # 不是命令，发送给AI处理
                process_ai_conversation(user_input)
                print_input_box()
                continue

            # 检查模式切换命令
            if handle_mode_switch_command(user_input):
                # 重新显示输入框
                print_input_box()
                continue

            command_parts = user_input.split()
            command = command_parts[0].lower()

            if command in ['/exit', '/quit']:
                print(f"{Fore.LIGHTCYAN_EX}再见！感谢使用 Forge AI Code!{Style.RESET_ALL}")
                break
            elif command == '/help':
                show_help()
            elif command == '/status':
                show_status()
            elif command == '/s':
                show_settings()
            elif command == '/clear-history':
                ai_client.clear_history()
                print(f"{Fore.GREEN}✓ AI对话历史已清除{Style.RESET_ALL}")
            elif command == '/clear':
                print_welcome_screen()
                continue  # 跳过重新显示输入框，因为print_welcome_screen已经包含了
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
            else:
                print(f"{Fore.RED}未知命令: {command}. 输入 '/help' 查看可用命令{Style.RESET_ALL}")

            # 在每个命令执行后重新显示输入框
            print()
            print_input_box()

        except KeyboardInterrupt:
            print(f"\n{Fore.LIGHTCYAN_EX}再见！感谢使用 Forge AI Code!{Style.RESET_ALL}")
            break
        except EOFError:
            print(f"\n{Fore.LIGHTCYAN_EX}再见！感谢使用 Forge AI Code!{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    main()
