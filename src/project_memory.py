"""
项目长久记忆管理模块
用于存储和管理项目特定的AI工作记忆，支持跨会话的上下文延续
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ProjectMemoryManager:
    """项目长久记忆管理器"""
    
    def __init__(self, project_root: str):
        """
        初始化项目记忆管理器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)
        self.memory_dir = self.project_root / ".byteiq_memory"
        self.memory_file = self.memory_dir / "project_memory.json"
        self.project_id = self._generate_project_id()
        
        # 确保记忆目录存在
        self.memory_dir.mkdir(exist_ok=True)
        
        # 初始化记忆数据
        self.memory_data = self._load_memory()
    
    def _generate_project_id(self) -> str:
        """根据项目路径生成唯一项目ID"""
        project_path_str = str(self.project_root.absolute())
        return hashlib.md5(project_path_str.encode()).hexdigest()[:12]
    
    def _load_memory(self) -> Dict[str, Any]:
        """加载项目记忆数据"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 确保数据结构完整
                    if 'project_id' not in data:
                        data['project_id'] = self.project_id
                    if 'sessions' not in data:
                        data['sessions'] = []
                    if 'summary' not in data:
                        data['summary'] = ""
                    if 'key_learnings' not in data:
                        data['key_learnings'] = []
                    return data
            except (json.JSONDecodeError, Exception):
                # 文件损坏，重新初始化
                pass
        
        # 返回默认结构
        return {
            'project_id': self.project_id,
            'project_path': str(self.project_root),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'sessions': [],
            'summary': "",
            'key_learnings': [],
            'total_sessions': 0
        }
    
    def _save_memory(self):
        """保存记忆数据到文件"""
        self.memory_data['updated_at'] = datetime.now().isoformat()
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存项目记忆失败: {e}")
    
    def add_session_summary(self, summary: str, completed_tasks: List[str] = None, 
                          key_insights: List[str] = None) -> bool:
        """
        添加会话总结到项目记忆
        
        Args:
            summary: AI工作总结
            completed_tasks: 完成的任务列表
            key_insights: 关键洞察和学习
            
        Returns:
            bool: 是否成功添加
        """
        try:
            session_data = {
                'session_id': len(self.memory_data['sessions']) + 1,
                'timestamp': datetime.now().isoformat(),
                'summary': summary.strip(),
                'completed_tasks': completed_tasks or [],
                'key_insights': key_insights or [],
                'word_count': len(summary.split())
            }
            
            self.memory_data['sessions'].append(session_data)
            self.memory_data['total_sessions'] += 1
            
            # 更新关键学习点
            if key_insights:
                for insight in key_insights:
                    if insight not in self.memory_data['key_learnings']:
                        self.memory_data['key_learnings'].append(insight)
            
            # 限制会话记录数量，保持最近50个会话
            if len(self.memory_data['sessions']) > 50:
                self.memory_data['sessions'] = self.memory_data['sessions'][-50:]
            
            # 更新项目总结
            self._update_project_summary()
            
            self._save_memory()
            return True
            
        except Exception as e:
            print(f"添加会话记忆失败: {e}")
            return False
    
    def _update_project_summary(self):
        """基于会话历史更新项目总结"""
        if not self.memory_data['sessions']:
            return
            
        recent_sessions = self.memory_data['sessions'][-10:]  # 最近10个会话
        
        # 提取关键信息
        all_tasks = []
        all_insights = []
        
        for session in recent_sessions:
            all_tasks.extend(session.get('completed_tasks', []))
            all_insights.extend(session.get('key_insights', []))
        
        # 生成简化的项目总结
        summary_parts = []
        
        if all_tasks:
            unique_tasks = list(set(all_tasks))
            summary_parts.append(f"主要完成任务: {', '.join(unique_tasks[:5])}")
        
        if all_insights:
            unique_insights = list(set(all_insights))
            summary_parts.append(f"关键技术要点: {', '.join(unique_insights[:3])}")
        
        summary_parts.append(f"总会话数: {self.memory_data['total_sessions']}")
        
        self.memory_data['summary'] = " | ".join(summary_parts)
    
    def get_context_for_ai(self, max_words: int = 500) -> str:
        """
        获取用于AI上下文的项目记忆摘要
        
        Args:
            max_words: 最大词数限制
            
        Returns:
            str: 格式化的上下文字符串
        """
        if not self.memory_data['sessions']:
            return ""
        
        context_parts = []
        
        # 添加项目基本信息
        context_parts.append(f"项目路径: {self.memory_data['project_path']}")
        context_parts.append(f"项目ID: {self.memory_data['project_id']}")
        
        # 添加项目总结
        if self.memory_data['summary']:
            context_parts.append(f"项目概况: {self.memory_data['summary']}")
        
        # 添加关键学习点
        if self.memory_data['key_learnings']:
            key_learnings = self.memory_data['key_learnings'][-5:]  # 最近5个
            context_parts.append(f"关键技术要点: {', '.join(key_learnings)}")
        
        # 添加最近会话摘要
        recent_sessions = self.memory_data['sessions'][-3:]  # 最近3个会话
        if recent_sessions:
            context_parts.append("最近工作记录:")
            for i, session in enumerate(recent_sessions, 1):
                session_summary = session['summary'][:100] + "..." if len(session['summary']) > 100 else session['summary']
                context_parts.append(f"  {i}. {session_summary}")
        
        # 组合上下文并控制长度
        full_context = "\n".join(context_parts)
        words = full_context.split()
        
        if len(words) > max_words:
            # 截断到指定词数
            truncated_words = words[:max_words]
            full_context = " ".join(truncated_words) + "..."
        
        return full_context
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        return {
            'project_id': self.memory_data['project_id'],
            'total_sessions': self.memory_data['total_sessions'],
            'memory_file_size': self.memory_file.stat().st_size if self.memory_file.exists() else 0,
            'last_updated': self.memory_data.get('updated_at', ''),
            'key_learnings_count': len(self.memory_data['key_learnings']),
            'recent_sessions_count': len(self.memory_data['sessions'])
        }
    
    def clear_memory(self) -> bool:
        """清空项目记忆（慎用）"""
        try:
            self.memory_data = {
                'project_id': self.project_id,
                'project_path': str(self.project_root),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'sessions': [],
                'summary': "",
                'key_learnings': [],
                'total_sessions': 0
            }
            self._save_memory()
            return True
        except Exception as e:
            print(f"清空项目记忆失败: {e}")
            return False


def get_project_memory_manager(project_root: str = None) -> ProjectMemoryManager:
    """
    获取项目记忆管理器实例
    
    Args:
        project_root: 项目根目录，如果为None则使用当前工作目录
        
    Returns:
        ProjectMemoryManager: 记忆管理器实例
    """
    if project_root is None:
        project_root = os.getcwd()
    
    return ProjectMemoryManager(project_root)


# 全局实例缓存
_memory_managers = {}

def get_cached_memory_manager(project_root: str = None) -> ProjectMemoryManager:
    """获取缓存的记忆管理器实例"""
    if project_root is None:
        project_root = os.getcwd()
    
    project_root = str(Path(project_root).absolute())
    
    if project_root not in _memory_managers:
        _memory_managers[project_root] = ProjectMemoryManager(project_root)
    
    return _memory_managers[project_root]
