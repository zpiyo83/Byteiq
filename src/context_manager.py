"""
智能上下文管理系统 - 充分利用Claude的200K token上下文窗口
"""

import json
import time
import tiktoken
from typing import List, Dict, Any, Optional
from pathlib import Path
from colorama import Fore, Style

class ContextManager:
    """智能上下文管理器"""
    
    def __init__(self, max_tokens=None):  # 用户可配置的上下文限制
        # 从配置文件加载max_tokens设置
        if max_tokens is None:
            from .config import load_config
            config = load_config()
            max_tokens = config.get('max_tokens', 12800)
        self.max_tokens = max_tokens
        self.conversation_history = []
        self.project_context = {}
        self.code_context = {}
        self.session_summary = ""
        self.encoding = tiktoken.get_encoding("cl100k_base")  # Claude使用的编码
        
    def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        try:
            return len(self.encoding.encode(text))
        except:
            # 如果编码失败，使用近似计算
            return len(text) // 3
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """添加消息到上下文"""
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "tokens": self.count_tokens(content),
            "metadata": metadata or {}
        }
        
        # 如果是用户的原始需求，标记为高优先级
        if role == "user" and not self.conversation_history:
            self.add_project_context("original_request", content, "critical")
        
        self.conversation_history.append(message)
        self._optimize_context()
    
    def _optimize_context(self):
        """优化上下文，确保不超过token限制"""
        total_tokens = self._calculate_total_tokens()
        
        if total_tokens <= self.max_tokens:
            return
        
        # 执行上下文压缩策略
        self._compress_context()
        
        # 清理过期的代码上下文
        self._cleanup_code_context()
    
    def _calculate_total_tokens(self) -> int:
        """计算当前总token数"""
        total = 0
        
        # 计算对话历史
        for msg in self.conversation_history:
            total += msg.get("tokens", 0)
        
        # 计算项目上下文
        for context in self.project_context.values():
            total += self.count_tokens(str(context))
        
        # 计算代码上下文
        for context in self.code_context.values():
            total += self.count_tokens(str(context))
        
        # 计算会话摘要
        if self.session_summary:
            total += self.count_tokens(self.session_summary)
        
        return total
    
    def _compress_context(self):
        """压缩上下文"""
        print(f"{Fore.YELLOW}🔄 上下文接近限制，正在智能压缩...{Style.RESET_ALL}")
        
        # 1. 保留最近的重要消息
        important_messages = self._extract_important_messages()
        
        # 2. 生成会话摘要
        old_messages = [msg for msg in self.conversation_history if msg not in important_messages]
        if old_messages:
            self.session_summary = self._generate_session_summary(old_messages)
        
        # 3. 更新对话历史
        self.conversation_history = important_messages
        
        # 4. 清理过期的代码上下文
        self._cleanup_code_context()
        
        print(f"{Fore.GREEN}✓ 上下文压缩完成{Style.RESET_ALL}")
    
    def _extract_important_messages(self) -> List[Dict]:
        """提取重要消息"""
        important = []
        
        # 保留最近的20条消息
        recent_messages = self.conversation_history[-20:]
        
        # 保留包含工具调用的消息
        tool_messages = [msg for msg in self.conversation_history 
                        if any(tag in msg["content"] for tag in ["<", ">", "工具", "执行"])]
        
        # 保留错误和重要信息
        error_messages = [msg for msg in self.conversation_history 
                         if any(keyword in msg["content"].lower() 
                               for keyword in ["错误", "error", "失败", "成功", "完成"])]
        
        # 合并并去重
        all_important = recent_messages + tool_messages[-10:] + error_messages[-5:]
        seen = set()
        for msg in all_important:
            msg_id = (msg["role"], msg["content"][:100], msg["timestamp"])
            if msg_id not in seen:
                important.append(msg)
                seen.add(msg_id)
        
        # 按时间排序
        important.sort(key=lambda x: x["timestamp"])
        
        return important
    
    def _generate_session_summary(self, messages: List[Dict]) -> str:
        """生成会话摘要"""
        if not messages:
            return self.session_summary
        
        # 提取关键信息
        user_requests = [msg["content"] for msg in messages if msg["role"] == "user"]
        ai_actions = [msg["content"] for msg in messages if msg["role"] == "assistant"]
        
        summary_parts = []
        
        if self.session_summary:
            summary_parts.append(f"之前的会话摘要: {self.session_summary}")
        
        if user_requests:
            summary_parts.append(f"用户请求: {'; '.join(user_requests[-5:])}")
        
        if ai_actions:
            # 提取工具调用和重要操作
            actions = []
            for action in ai_actions[-10:]:
                if any(tag in action for tag in ["创建", "修改", "执行", "完成"]):
                    actions.append(action[:100])
            if actions:
                summary_parts.append(f"执行的操作: {'; '.join(actions)}")
        
        return " | ".join(summary_parts)
    
    def _cleanup_code_context(self):
        """清理过期的代码上下文"""
        current_time = time.time()
        
        # 移除超过1小时的代码上下文
        expired_keys = []
        for key, context in self.code_context.items():
            if current_time - context.get("timestamp", 0) > 3600:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.code_context[key]
    
    def add_project_context(self, key: str, content: str, priority: str = "normal"):
        """添加项目上下文"""
        self.project_context[key] = {
            "content": content,
            "priority": priority,  # critical > high > normal
            "timestamp": time.time(),
            "tokens": self.count_tokens(content)
        }
    
    def _get_todo_context(self) -> str:
        """获取当前TODO任务上下文"""
        try:
            import os
            todo_file = "todo_data.json"
            if os.path.exists(todo_file):
                import json
                with open(todo_file, 'r', encoding='utf-8') as f:
                    todos = json.load(f)
                
                active_todos = []
                for todo in todos:
                    if todo.get('status') in ['pending', 'in_progress']:
                        priority_mark = "🔥" if todo.get('priority') == 'high' else "📋"
                        status_mark = "⏳" if todo.get('status') == 'in_progress' else "📝"
                        active_todos.append(f"{priority_mark}{status_mark} {todo.get('content', '')}")
                
                if active_todos:
                    return "; ".join(active_todos[:3])  # 最多显示3个任务
        except:
            pass
        return ""
    
    def add_code_context(self, file_path: str, content: str, context_type: str = "file"):
        """添加代码上下文"""
        self.code_context[file_path] = {
            "content": content,
            "type": context_type,
            "timestamp": time.time(),
            "tokens": self.count_tokens(content)
        }
    
    def update_todo_context(self):
        """更新TODO上下文到项目上下文中"""
        todo_context = self._get_todo_context()
        if todo_context:
            self.add_project_context("current_todos", todo_context, "high")
    
    def get_context_for_ai(self) -> Dict[str, Any]:
        """获取用于AI的上下文信息"""
        context = {
            "conversation_history": [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in self.conversation_history
            ],
            "session_summary": self.session_summary,
            "project_context": {},
            "code_context": {},
            "stats": {
                "total_tokens": self._calculate_total_tokens(),
                "max_tokens": self.max_tokens,
                "utilization": f"{(self._calculate_total_tokens() / self.max_tokens * 100):.1f}%"
            }
        }
        
        # 添加高优先级项目上下文
        for key, ctx in self.project_context.items():
            if ctx["priority"] == "high" or len(context["project_context"]) < 5:
                context["project_context"][key] = ctx["content"]
        
        # 添加最近的代码上下文
        recent_code = sorted(
            self.code_context.items(),
            key=lambda x: x[1]["timestamp"],
            reverse=True
        )[:10]
        
        for file_path, ctx in recent_code:
            context["code_context"][file_path] = {
                "type": ctx["type"],
                "content": ctx["content"][:2000]  # 限制长度
            }
        
        return context
    
    def get_enhanced_messages(self) -> List[Dict[str, str]]:
        """获取增强的消息列表，按重要性排序，不包含系统提示词"""
        messages = []
        
        # 1. 最高优先级：原始需求和关键计划
        critical_contexts = []
        high_contexts = []
        normal_contexts = []
        
        for key, ctx in self.project_context.items():
            if ctx["priority"] == "critical":
                critical_contexts.append(f"{key}: {ctx['content']}")
            elif ctx["priority"] == "high":
                high_contexts.append(f"{key}: {ctx['content']}")
            else:
                normal_contexts.append(f"{key}: {ctx['content']}")
        
        # 按优先级添加上下文
        if critical_contexts:
            messages.append({
                "role": "system",
                "content": f"[关键信息] {'; '.join(critical_contexts)}"
            })
        
        if high_contexts:
            messages.append({
                "role": "system", 
                "content": f"[重要上下文] {'; '.join(high_contexts)}"
            })
        
        # 2. 添加TODO任务上下文
        todo_context = self._get_todo_context()
        if todo_context:
            messages.append({
                "role": "system",
                "content": f"[当前任务] {todo_context}"
            })
        
        # 3. 添加会话摘要
        if self.session_summary:
            messages.append({
                "role": "system",
                "content": f"[会话摘要] {self.session_summary}"
            })
        
        # 4. 添加对话历史，但跳过系统消息避免重复
        for msg in self.conversation_history:
            if msg["role"] != "system":
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return messages
    
    def save_context(self, file_path: str = ".byteiq_context.json"):
        """保存上下文到文件"""
        try:
            context_data = {
                "conversation_history": self.conversation_history,
                "project_context": self.project_context,
                "session_summary": self.session_summary,
                "timestamp": time.time()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"{Fore.YELLOW}保存上下文失败: {e}{Style.RESET_ALL}")
    
    def load_context(self, file_path: str = ".byteiq_context.json"):
        """从文件加载上下文"""
        try:
            if not Path(file_path).exists():
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
            
            self.conversation_history = context_data.get("conversation_history", [])
            self.project_context = context_data.get("project_context", {})
            self.session_summary = context_data.get("session_summary", "")
            
            # 重新计算token数
            for msg in self.conversation_history:
                if "tokens" not in msg:
                    msg["tokens"] = self.count_tokens(msg["content"])
            
            print(f"{Fore.GREEN}✓ 已加载上下文历史{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.YELLOW}加载上下文失败: {e}{Style.RESET_ALL}")
            return False
    
    def clear_context(self):
        """清除所有上下文"""
        self.conversation_history = []
        self.project_context = {}
        self.code_context = {}
        self.session_summary = ""
        print(f"{Fore.GREEN}✓ 已清除所有上下文{Style.RESET_ALL}")
    
    def get_context_stats(self) -> Dict[str, Any]:
        """获取上下文统计信息"""
        total_tokens = self._calculate_total_tokens()
        
        return {
            "total_tokens": total_tokens,
            "max_tokens": self.max_tokens,
            "utilization_percent": round((total_tokens / self.max_tokens) * 100, 1),
            "conversation_messages": len(self.conversation_history),
            "project_contexts": len(self.project_context),
            "code_contexts": len(self.code_context),
            "has_summary": bool(self.session_summary)
        }
    
    def set_max_tokens(self, max_tokens: int):
        """设置最大token数"""
        if max_tokens < 1000:
            raise ValueError("最大token数不能少于1000")
        if max_tokens > 200000:
            raise ValueError("最大token数不能超过200000")
        
        self.max_tokens = max_tokens
        
        # 保存到配置文件
        from .config import load_config, save_config
        config = load_config()
        config['max_tokens'] = max_tokens
        save_config(config)
        
        print(f"{Fore.GREEN}✓ 上下文限制已设置为 {max_tokens:,} tokens{Style.RESET_ALL}")
        
        # 如果当前上下文超出限制，触发压缩
        if self._calculate_total_tokens() > max_tokens:
            self._optimize_context()

# 全局上下文管理器实例
context_manager = ContextManager()
