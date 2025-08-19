"""
AI工具系统 - 处理AI的工具调用
"""

import os
import re
import subprocess
from colorama import Fore, Style
from .todo_manager import todo_manager
from .todo_renderer import get_todo_renderer

class AIToolProcessor:
    """AI工具处理器"""
    
    def __init__(self):
        self.tools = {
            'read_file': self.read_file,
            'write_file': self.write_file,
            'create_file': self.create_file,
            'execute_command': self.execute_command,
            'add_todo': self.add_todo,
            'update_todo': self.update_todo,
            'show_todos': self.show_todos,
            'task_complete': self.task_complete
        }
        self.todo_renderer = get_todo_renderer(todo_manager)
    
    def process_response(self, ai_response):
        """处理AI响应，提取和执行工具调用"""
        # 查找XML工具调用
        tool_patterns = {
            'read_file': r'<read_file><path>(.*?)</path></read_file>',
            'write_file': r'<write_file><path>(.*?)</path><content>(.*?)</content></write_file>',
            'create_file': r'<create_file><path>(.*?)</path><content>(.*?)</content></create_file>',
            'execute_command': r'<execute_command><command>(.*?)</command></execute_command>',
            'add_todo': r'<add_todo><title>(.*?)</title><description>(.*?)</description><priority>(.*?)</priority></add_todo>',
            'update_todo': r'<update_todo><id>(.*?)</id><status>(.*?)</status><progress>(.*?)</progress></update_todo>',
            'show_todos': r'<show_todos></show_todos>',
            'task_complete': r'<task_complete><summary>(.*?)</summary></task_complete>'
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
                elif tool_name == 'add_todo':
                    title, description, priority = matches[0]
                    tool_result = self.tools[tool_name](title.strip(), description.strip(), priority.strip())
                    display_text = f"添加任务: {title.strip()}"
                elif tool_name == 'update_todo':
                    todo_id, status, progress = matches[0]
                    tool_result = self.tools[tool_name](todo_id.strip(), status.strip(), int(progress.strip()) if progress.strip().isdigit() else 0)
                    display_text = f"更新任务: {todo_id.strip()}"
                elif tool_name == 'show_todos':
                    tool_result = self.tools[tool_name]()
                    display_text = "显示任务列表"
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
                timeout=30,
                encoding='utf-8',
                errors='ignore'
            )
            
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            output = stdout + stderr
            return_code = result.returncode

            if return_code == 0:
                return f"命令执行成功:\n{output}" if output.strip() else "命令执行成功"
            else:
                return f"命令执行失败 (返回码: {return_code}):\n{output}"
                
        except subprocess.TimeoutExpired:
            return "命令执行超时"
        except Exception as e:
            return f"执行命令失败: {str(e)}"

    def add_todo(self, title: str, description: str = "", priority: str = "medium"):
        """添加TODO任务工具"""
        try:
            todo_id = todo_manager.add_todo(title, description, priority)
            return f"成功添加任务: {title} (ID: {todo_id[:8]})"
        except Exception as e:
            return f"添加任务失败: {str(e)}"

    def update_todo(self, todo_id: str, status: str, progress: int = 0):
        """更新TODO任务工具"""
        try:
            # 如果是短ID，尝试匹配完整ID
            if len(todo_id) == 8:
                full_id = None
                for tid in todo_manager.todos.keys():
                    if tid.startswith(todo_id):
                        full_id = tid
                        break
                if full_id:
                    todo_id = full_id
                else:
                    return f"未找到ID为 {todo_id} 的任务"

            success = todo_manager.update_todo(todo_id, status=status, progress=progress)
            if success:
                todo = todo_manager.get_todo(todo_id)
                return f"成功更新任务: {todo.title} -> {status} ({progress}%)"
            else:
                return f"更新任务失败: 任务不存在"
        except Exception as e:
            return f"更新任务失败: {str(e)}"

    def show_todos(self):
        """显示TODO列表工具"""
        try:
            return self.todo_renderer.render_todo_list()
        except Exception as e:
            return f"显示任务列表失败: {str(e)}"

    def task_complete(self, summary):
        """任务完成工具"""
        return f"任务已完成: {summary}"

# 全局工具处理器实例
ai_tool_processor = AIToolProcessor()
