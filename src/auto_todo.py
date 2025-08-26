#!/usr/bin/env python3
"""
自动TODO管理器 - 在用户提出需求时自动创建和更新TODO任务
"""

from typing import List, Dict
from .todo_manager import todo_manager
from .ai_tools import ai_tool_processor
import re

class AutoTodoManager:
    """自动TODO管理器"""
    
    def __init__(self):
        self.active_tasks = {}  # 跟踪当前活跃任务
    
    def extract_task_from_request(self, user_request: str) -> List[Dict]:
        """从用户请求中提取任务信息"""
        tasks = []
        
        # 检查是否是明确的任务请求
        task_patterns = [
            r'(?:实现|开发|创建|添加).*?(?:功能|模块|组件|特性|feature|module|component)',
            r'(?:修复|解决|处理).*?(?:bug|问题|错误|issue)',
            r'(?:优化|改进|重构|refactor|optimize).*?(?:性能|代码|结构)',
            r'(?:写|创建|生成).*?(?:文档|说明|guide|documentation)',
        ]
        
        for pattern in task_patterns:
            matches = re.finditer(pattern, user_request, re.IGNORECASE)
            for match in matches:
                task_title = match.group(0)
                task_type = self._classify_task(task_title)
                tasks.append({
                    'title': task_title,
                    'type': task_type,
                    'description': f"根据用户请求自动创建的任务: {user_request}"
                })
        
        # 如果没有匹配到特定模式，创建一个通用任务
        if not tasks and len(user_request) > 10:  # 长度大于10才认为是有效请求
            tasks.append({
                'title': f"处理用户请求: {user_request[:30]}...",
                'type': 'general',
                'description': user_request
            })
        
        return tasks
    
    def _classify_task(self, task_title: str) -> str:
        """分类任务类型"""
        title_lower = task_title.lower()
        
        if any(word in title_lower for word in ['bug', '修复', '解决', '错误']):
            return 'bug_fix'
        elif any(word in title_lower for word in ['优化', '改进', '重构', 'refactor', 'optimize']):
            return 'optimization'
        elif any(word in title_lower for word in ['文档', '说明', 'guide', 'documentation']):
            return 'documentation'
        elif any(word in title_lower for word in ['测试', 'test']):
            return 'testing'
        else:
            return 'feature'
    
    def create_todo_from_request(self, user_request: str) -> str:
        """根据用户请求自动创建TODO任务"""
        tasks = self.extract_task_from_request(user_request)
        
        if not tasks:
            return ""
        
        # 创建主任务
        main_task = tasks[0]
        task_id = todo_manager.add_todo(
            title=main_task['title'],
            description=main_task['description'],
            priority=self._determine_priority(user_request)
        )
        
        # 跟踪任务
        self.active_tasks[task_id] = {
            'request': user_request,
            'title': main_task['title'],
            'subtasks': []
        }
        
        # 如果有子任务，创建子任务
        for i, subtask in enumerate(tasks[1:], 1):
            subtask_id = todo_manager.add_todo(
                title=subtask['title'],
                description=subtask['description'],
                priority='medium',
                parent_id=task_id
            )
            self.active_tasks[task_id]['subtasks'].append(subtask_id)
        
        return task_id
    
    def _determine_priority(self, user_request: str) -> str:
        """根据用户请求确定任务优先级"""
        request_lower = user_request.lower()
        
        # 紧急关键词
        urgent_keywords = ['紧急', 'urgent', '马上', '立即', 'asap', 'critical', '重要']
        if any(keyword in request_lower for keyword in urgent_keywords):
            return 'urgent'
        
        # 高优先级关键词
        high_keywords = ['重要', '重要性', '关键', '核心', '主要', 'high', 'important']
        if any(keyword in request_lower for keyword in high_keywords):
            return 'high'
        
        # 低优先级关键词
        low_keywords = ['简单', '小', 'minor', '低', '琐碎']
        if any(keyword in request_lower for keyword in low_keywords):
            return 'low'
        
        # 默认中等优先级
        return 'medium'
    
    def update_todo_progress(self, task_id: str, progress: int, status: str = None):
        """更新任务进度"""
        if task_id in self.active_tasks:
            updates = {'progress': progress}
            if status:
                updates['status'] = status
            
            todo_manager.update_todo(task_id, **updates)
    
    def mark_task_completed(self, task_id: str):
        """标记任务完成"""
        if task_id in self.active_tasks:
            todo_manager.update_todo(task_id, status='completed', progress=100)
            # 同时完成所有子任务
            for subtask_id in self.active_tasks[task_id]['subtasks']:
                todo_manager.update_todo(subtask_id, status='completed', progress=100)
    
    def get_active_tasks(self) -> Dict:
        """获取当前活跃任务"""
        return self.active_tasks

# 全局实例
auto_todo_manager = AutoTodoManager()