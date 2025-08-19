"""
AI客户端模块 - 处理与AI API的交互
"""

import os
import json
import requests
import threading
import time
from colorama import Fore, Style
from .config import load_config, DEFAULT_API_URL

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

4. **执行命令**（Windows系统）
格式：<execute_command><command>命令内容</command></execute_command>
注意：使用Windows命令，如 dir、type、cd 等，不要使用 ls、cat 等Linux命令

5. **添加TODO任务**
格式：<add_todo><title>任务标题</title><description>任务描述</description><priority>优先级(low/medium/high/urgent)</priority></add_todo>

6. **更新TODO任务**
格式：<update_todo><id>任务ID</id><status>状态(pending/in_progress/completed/cancelled)</status><progress>进度(0-100)</progress></update_todo>

7. **显示TODO列表**
格式：<show_todos></show_todos>

8. **结束任务**
格式：<task_complete><summary>任务总结</summary></task_complete>

**重要规则：**
1. 当你需要使用工具时，必须使用XML格式
2. 每次只能使用一个工具
3. 使用工具后等待结果，然后继续
4. 完成任务后使用task_complete结束
5. 分析用户需求，制定步骤计划
6. 优先查看项目结构，理解现有代码
7. 创建文件时考虑项目结构的合理性
8. **重要**：不要使用系统命令操作TODO，必须使用内置XML工具
9. **重要**：当前运行在Windows系统，使用Windows命令（dir、type、cd），不要使用Linux命令（ls、cat、pwd）

**TODO操作示例：**
- 显示任务：<show_todos></show_todos>
- 添加任务：<add_todo><title>任务标题</title><description>描述</description><priority>high</priority></add_todo>
- 更新任务：<update_todo><id>任务ID</id><status>completed</status><progress>100</progress></update_todo>

**Windows命令示例：**
- 列出文件：<execute_command><command>dir</command></execute_command>
- 递归列出：<execute_command><command>dir /s</command></execute_command>
- 查看文件：<execute_command><command>type filename.txt</command></execute_command>
- 切换目录：<execute_command><command>cd dirname</command></execute_command>

**工作流程示例：**
用户："我要做贪吃蛇"
1. 分析需求，查看项目结构
2. 创建必要的文件（如snake.py, game.py等）
3. 逐步写入代码内容
4. 测试运行
5. 完成后总结

请始终保持专业、高效，提供高质量的代码和建议。"""

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
