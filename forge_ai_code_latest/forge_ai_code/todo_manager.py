#!/usr/bin/env python3
"""
TODO任务管理器
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from colorama import Fore, Style

class TodoItem:
    """TODO项目类"""
    
    def __init__(self, title: str, description: str = "", priority: str = "medium", 
                 parent_id: Optional[str] = None, task_id: Optional[str] = None):
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = "pending"  # pending, in_progress, completed, cancelled
        self.priority = priority  # low, medium, high, urgent
        self.parent_id = parent_id
        self.subtasks: List[str] = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.progress = 0  # 0-100
        
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'parent_id': self.parent_id,
            'subtasks': self.subtasks,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'progress': self.progress
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TodoItem':
        """从字典创建"""
        item = cls(data['title'], data.get('description', ''), 
                  data.get('priority', 'medium'), data.get('parent_id'))
        item.id = data['id']
        item.status = data.get('status', 'pending')
        item.subtasks = data.get('subtasks', [])
        item.created_at = data.get('created_at', datetime.now().isoformat())
        item.updated_at = data.get('updated_at', datetime.now().isoformat())
        item.progress = data.get('progress', 0)
        return item

class TodoManager:
    """TODO管理器"""
    
    def __init__(self, data_file: str = "todo_data.json"):
        self.data_file = data_file
        self.todos: Dict[str, TodoItem] = {}
        self.load_todos()
    
    def load_todos(self):
        """加载TODO数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for todo_data in data:
                        todo = TodoItem.from_dict(todo_data)
                        self.todos[todo.id] = todo
            except Exception as e:
                print(f"加载TODO数据失败: {e}")
    
    def save_todos(self):
        """保存TODO数据"""
        try:
            data = [todo.to_dict() for todo in self.todos.values()]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存TODO数据失败: {e}")
    
    def add_todo(self, title: str, description: str = "", priority: str = "medium", 
                 parent_id: Optional[str] = None) -> str:
        """添加TODO项目"""
        todo = TodoItem(title, description, priority, parent_id)
        self.todos[todo.id] = todo
        
        # 如果有父任务，添加到父任务的子任务列表
        if parent_id and parent_id in self.todos:
            self.todos[parent_id].subtasks.append(todo.id)
            self.todos[parent_id].updated_at = datetime.now().isoformat()
        
        self.save_todos()
        return todo.id
    
    def update_todo(self, todo_id: str, **kwargs) -> bool:
        """更新TODO项目"""
        if todo_id not in self.todos:
            return False
        
        todo = self.todos[todo_id]
        for key, value in kwargs.items():
            if hasattr(todo, key):
                setattr(todo, key, value)
        
        todo.updated_at = datetime.now().isoformat()
        self.save_todos()
        return True
    
    def delete_todo(self, todo_id: str) -> bool:
        """删除TODO项目"""
        if todo_id not in self.todos:
            return False
        
        todo = self.todos[todo_id]
        
        # 删除所有子任务
        for subtask_id in todo.subtasks:
            self.delete_todo(subtask_id)
        
        # 从父任务中移除
        if todo.parent_id and todo.parent_id in self.todos:
            parent = self.todos[todo.parent_id]
            if todo_id in parent.subtasks:
                parent.subtasks.remove(todo_id)
                parent.updated_at = datetime.now().isoformat()
        
        del self.todos[todo_id]
        self.save_todos()
        return True
    
    def get_todo(self, todo_id: str) -> Optional[TodoItem]:
        """获取TODO项目"""
        return self.todos.get(todo_id)
    
    def get_root_todos(self) -> List[TodoItem]:
        """获取根级TODO项目"""
        return [todo for todo in self.todos.values() if todo.parent_id is None]
    
    def get_subtodos(self, parent_id: str) -> List[TodoItem]:
        """获取子TODO项目"""
        if parent_id not in self.todos:
            return []
        
        parent = self.todos[parent_id]
        return [self.todos[subtask_id] for subtask_id in parent.subtasks 
                if subtask_id in self.todos]
    
    def clear_completed(self):
        """清除已完成的任务"""
        completed_ids = [todo_id for todo_id, todo in self.todos.items() 
                        if todo.status == "completed"]
        
        for todo_id in completed_ids:
            self.delete_todo(todo_id)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = len(self.todos)
        pending = len([t for t in self.todos.values() if t.status == "pending"])
        in_progress = len([t for t in self.todos.values() if t.status == "in_progress"])
        completed = len([t for t in self.todos.values() if t.status == "completed"])
        cancelled = len([t for t in self.todos.values() if t.status == "cancelled"])
        
        return {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'cancelled': cancelled
        }

# 全局TODO管理器实例
todo_manager = TodoManager()
