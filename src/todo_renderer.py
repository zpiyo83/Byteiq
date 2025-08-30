#!/usr/bin/env python3
"""
TODO渲染器 - 负责美观地显示TODO列表
"""

from typing import List, Optional
from colorama import Fore, Style
from .todo_manager import TodoItem, TodoManager

class TodoRenderer:
    """TODO渲染器"""
    
    def __init__(self, todo_manager: TodoManager):
        self.todo_manager = todo_manager
        
        # 状态图标和颜色
        self.status_icons = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'cancelled': '❌'
        }
        
        self.status_colors = {
            'pending': Fore.YELLOW,
            'in_progress': Fore.CYAN,
            'completed': Fore.GREEN,
            'cancelled': Fore.RED
        }
        
        # 优先级图标和颜色
        self.priority_icons = {
            'low': '🔵',
            'medium': '🟡',
            'high': '🟠',
            'urgent': '🔴'
        }
        
        self.priority_colors = {
            'low': Fore.BLUE,
            'medium': Fore.YELLOW,
            'high': Fore.MAGENTA,
            'urgent': Fore.RED
        }
    
    def render_todo_list(self, show_completed: bool = True, filter_status: Optional[str] = None) -> str:
        """渲染完整的TODO列表"""
        output = []
        
        # 简洁标题
        output.append("[ show ] —— TODO ——")
        
        # 获取根级任务
        root_todos = self.todo_manager.get_root_todos()
        
        if not root_todos:
            output.append("  暂无任务")
            return '\n'.join(output)
        
        # 过滤任务
        if filter_status:
            root_todos = [todo for todo in root_todos if todo.status == filter_status]
        
        if not show_completed:
            root_todos = [todo for todo in root_todos if todo.status != 'completed']
        
        # 按优先级排序 (数字越大优先级越低)
        priority_order = {'urgent': 1, 'high': 2, 'medium': 3, 'low': 4}
        
        root_todos.sort(key=lambda x: priority_order.get(x.priority, 5))
        
        # 渲染每个根级任务
        for todo in root_todos:
            output.append(self._render_simple_todo_item(todo))
            
            # 渲染子任务
            subtodos = self.todo_manager.get_subtodos(todo.id)
            for subtodo in subtodos:
                output.append(self._render_simple_todo_item(subtodo, is_subtask=True))
        
        return '\n'.join(output)
    
    def _render_simple_todo_item(self, todo: TodoItem, is_subtask: bool = False) -> str:
        """渲染简洁格式的TODO项目"""
        # 完成状态：X表示完成，空格表示未完成
        status_mark = "X" if todo.status == 'completed' else " "
        
        # 优先级数字：数字越大优先级越低
        priority_num = {'urgent': 1, 'high': 2, 'medium': 3, 'low': 4}.get(todo.priority, 5)
        
        # 缩进处理
        indent = "    " if is_subtask else "  "
        
        # 构建输出
        return f"{indent}[{status_mark}]{todo.title} {priority_num}"
    
    def _render_todo_item(self, todo: TodoItem, level: int = 0, index: int = 1, is_subtask: bool = False) -> str:
        """渲染单个TODO项目"""
        indent = "  " * level
        
        # 状态图标和颜色
        status_icon = self.status_icons.get(todo.status, '❓')
        status_color = self.status_colors.get(todo.status, Fore.WHITE)
        
        # 优先级图标
        priority_icon = self.priority_icons.get(todo.priority, '⚪')
        
        # 进度条
        progress_bar = self._render_progress_bar(todo.progress)
        
        # 子任务前缀
        prefix = "└─" if is_subtask else f"{index}."
        
        # 构建输出
        output = f"{indent}{Fore.LIGHTBLACK_EX}{prefix}{Style.RESET_ALL} "
        output += f"{status_icon} {priority_icon} "
        output += f"{status_color}{todo.title}{Style.RESET_ALL}"
        
        # 添加进度条（如果有进度）
        if todo.progress > 0:
            output += f" {progress_bar}"
        
        # 添加描述（如果有）
        if todo.description:
            output += f"\n{indent}   {Fore.LIGHTBLACK_EX}{todo.description}{Style.RESET_ALL}"
        
        # 添加子任务数量
        if todo.subtasks:
            subtask_count = len(todo.subtasks)
            completed_subtasks = len([sid for sid in todo.subtasks 
                                    if sid in self.todo_manager.todos and 
                                    self.todo_manager.todos[sid].status == 'completed'])
            output += f"\n{indent}   {Fore.LIGHTBLACK_EX}子任务: {completed_subtasks}/{subtask_count}{Style.RESET_ALL}"
        
        return output
    
    def _render_progress_bar(self, progress: int, width: int = 10) -> str:
        """渲染进度条"""
        if progress <= 0:
            return ""
        
        filled = int(progress / 100 * width)
        empty = width - filled
        
        bar = "█" * filled + "░" * empty
        color = Fore.GREEN if progress >= 100 else Fore.CYAN if progress >= 50 else Fore.YELLOW
        
        return f"{color}[{bar}] {progress}%{Style.RESET_ALL}"
    
    def render_todo_summary(self) -> str:
        """渲染TODO摘要"""
        stats = self.todo_manager.get_stats()
        
        if stats['total'] == 0:
            return f"{Fore.LIGHTBLACK_EX}暂无任务{Style.RESET_ALL}"
        
        # 获取当前进行中的任务
        current_tasks = [todo for todo in self.todo_manager.todos.values() 
                        if todo.status == 'in_progress']
        
        output = []
        output.append(f"{Fore.CYAN}任务概览:{Style.RESET_ALL}")
        output.append(f"   {Fore.YELLOW}⏳ 待办: {stats['pending']}{Style.RESET_ALL} | "
                     f"{Fore.CYAN}🔄 进行中: {stats['in_progress']}{Style.RESET_ALL} | "
                     f"{Fore.GREEN}✅ 已完成: {stats['completed']}{Style.RESET_ALL}")
        
        if current_tasks:
            output.append(f"\n{Fore.CYAN}当前任务:{Style.RESET_ALL}")
            for task in current_tasks[:3]:  # 最多显示3个
                progress = f" ({task.progress}%)" if task.progress > 0 else ""
                output.append(f"   • {task.title}{progress}")
        
        return '\n'.join(output)
    
    def render_todo_item_detail(self, todo_id: str) -> str:
        """渲染TODO项目详情"""
        todo = self.todo_manager.get_todo(todo_id)
        if not todo:
            return f"{Fore.RED}任务不存在: {todo_id}{Style.RESET_ALL}"
        
        output = []
        output.append(f"\n{Fore.LIGHTCYAN_EX}{'='*50}{Style.RESET_ALL}")
        output.append(f"{Fore.LIGHTCYAN_EX}任务详情{Style.RESET_ALL}")
        output.append(f"{Fore.LIGHTCYAN_EX}{'='*50}{Style.RESET_ALL}")
        
        # 基本信息
        status_icon = self.status_icons.get(todo.status, '❓')
        status_color = self.status_colors.get(todo.status, Fore.WHITE)
        priority_icon = self.priority_icons.get(todo.priority, '⚪')
        
        output.append(f"\n{Fore.WHITE}标题:{Style.RESET_ALL} {status_icon} {todo.title}")
        output.append(f"{Fore.WHITE}状态:{Style.RESET_ALL} {status_color}{todo.status}{Style.RESET_ALL}")
        output.append(f"{Fore.WHITE}优先级:{Style.RESET_ALL} {priority_icon} {todo.priority}")
        
        if todo.description:
            output.append(f"{Fore.WHITE}描述:{Style.RESET_ALL} {todo.description}")
        
        if todo.progress > 0:
            progress_bar = self._render_progress_bar(todo.progress)
            output.append(f"{Fore.WHITE}进度:{Style.RESET_ALL} {progress_bar}")
        
        # 时间信息
        output.append(f"{Fore.WHITE}创建时间:{Style.RESET_ALL} {todo.created_at[:19]}")
        output.append(f"{Fore.WHITE}更新时间:{Style.RESET_ALL} {todo.updated_at[:19]}")
        
        # 子任务
        if todo.subtasks:
            output.append(f"\n{Fore.WHITE}子任务 ({len(todo.subtasks)}):{Style.RESET_ALL}")
            for subtask_id in todo.subtasks:
                subtask = self.todo_manager.get_todo(subtask_id)
                if subtask:
                    icon = self.status_icons.get(subtask.status, '❓')
                    color = self.status_colors.get(subtask.status, Fore.WHITE)
                    output.append(f"   • {icon} {color}{subtask.title}{Style.RESET_ALL}")
        
        output.append(f"\n{Fore.LIGHTCYAN_EX}{'='*50}{Style.RESET_ALL}")
        return '\n'.join(output)

# 全局渲染器实例
def get_todo_renderer(todo_manager) -> TodoRenderer:
    """获取TODO渲染器实例"""
    return TodoRenderer(todo_manager)
