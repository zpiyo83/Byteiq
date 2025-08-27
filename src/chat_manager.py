"""
聊天上下文管理器 - 提供交互式上下文保存和加载功能
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from colorama import Fore, Style

class ChatManager:
    """聊天上下文管理器"""
    
    def __init__(self):
        # 软件目录下的上下文存储目录
        self.contexts_dir = Path(__file__).parent.parent / "contexts"
        self.contexts_dir.mkdir(exist_ok=True)
        
    def save_context_interactive(self, context_manager) -> bool:
        """交互式保存上下文"""
        try:
            print(f"\n{theme_manager.format_tool_header('Save', '上下文')}")
            
            # 获取用户输入的名称
            name = input(f"请输入上下文名称: ").strip()
            if not name:
                print(f"{Fore.YELLOW}❌ 名称不能为空{Style.RESET_ALL}")
                return False
            
            # 清理文件名
            safe_name = self._sanitize_filename(name)
            filename = f"{safe_name}_{int(time.time())}.json"
            filepath = self.contexts_dir / filename
            
            # 保存上下文数据
            context_data = {
                "name": name,
                "created_time": time.time(),
                "created_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "conversation_history": context_manager.conversation_history,
                "project_context": context_manager.project_context,
                "session_summary": context_manager.session_summary,
                "stats": context_manager.get_context_stats()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, ensure_ascii=False, indent=2)
            
            print(f"  • 上下文已保存: {name}")
            print(f"  • 保存位置: {filepath}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ 保存失败: {e}{Style.RESET_ALL}")
            return False
    
    def export_context_to_current_dir(self, context_manager) -> bool:
        """导出上下文到当前目录"""
        try:
            print(f"\n{Fore.CYAN}📤 导出上下文到当前目录{Style.RESET_ALL}")
            
            # 获取用户输入的名称
            name = input(f"请输入导出文件名称: ").strip()
            if not name:
                print(f"{Fore.YELLOW}❌ 名称不能为空{Style.RESET_ALL}")
                return False
            
            # 清理文件名并添加扩展名
            safe_name = self._sanitize_filename(name)
            if not safe_name.endswith('.json'):
                safe_name += '.json'
            
            filepath = Path.cwd() / safe_name
            
            # 导出上下文数据
            context_data = {
                "name": name,
                "exported_time": time.time(),
                "exported_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "conversation_history": context_manager.conversation_history,
                "project_context": context_manager.project_context,
                "session_summary": context_manager.session_summary,
                "stats": context_manager.get_context_stats()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, ensure_ascii=False, indent=2)
            
            print(f"  • 上下文已导出: {name}")
            print(f"  • 导出位置: {filepath}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ 导出失败: {e}{Style.RESET_ALL}")
            return False
    
    def load_context_interactive(self, context_manager) -> bool:
        """交互式加载上下文"""
        try:
            print(f"\n{Fore.CYAN}📂 加载上下文{Style.RESET_ALL}")
            
            # 获取所有保存的上下文
            contexts = self._get_saved_contexts()
            
            if not contexts:
                print(f"{Fore.YELLOW}📭 没有找到已保存的上下文{Style.RESET_ALL}")
                return False
            
            # 显示上下文列表
            print(f"\n{Fore.CYAN}可用的上下文:{Style.RESET_ALL}")
            print("=" * 60)
            
            for i, context_info in enumerate(contexts, 1):
                name = context_info['name']
                date = context_info['date']
                messages = context_info['message_count']
                tokens = context_info['tokens']
                
                print(f"{Fore.WHITE}{i:2d}.{Style.RESET_ALL} {Fore.YELLOW}{name}{Style.RESET_ALL}")
                print(f"     📅 {date}  💬 {messages}条消息  🔢 {tokens:,} tokens")
                print()
            
            # 用户选择
            while True:
                try:
                    choice = input(f"{Fore.CYAN}请选择要加载的上下文 (1-{len(contexts)}, 0=取消): {Style.RESET_ALL}").strip()
                    
                    if choice == '0':
                        print(f"{Fore.YELLOW}❌ 已取消加载{Style.RESET_ALL}")
                        return False
                    
                    index = int(choice) - 1
                    if 0 <= index < len(contexts):
                        selected_context = contexts[index]
                        break
                    else:
                        print(f"{Fore.RED}❌ 无效选择，请输入 1-{len(contexts)}{Style.RESET_ALL}")
                        
                except ValueError:
                    print(f"{Fore.RED}❌ 请输入有效数字{Style.RESET_ALL}")
            
            # 加载选中的上下文
            return self._load_context_file(selected_context['filepath'], context_manager)
            
        except Exception as e:
            print(f"{Fore.RED}❌ 加载失败: {e}{Style.RESET_ALL}")
            return False
    
    def _get_saved_contexts(self) -> List[Dict[str, Any]]:
        """获取所有保存的上下文信息"""
        contexts = []
        
        try:
            for filepath in self.contexts_dir.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 提取上下文信息
                    context_info = {
                        'filepath': filepath,
                        'name': data.get('name', filepath.stem),
                        'date': data.get('created_date', '未知时间'),
                        'message_count': len(data.get('conversation_history', [])),
                        'tokens': data.get('stats', {}).get('total_tokens', 0),
                        'created_time': data.get('created_time', 0)
                    }
                    
                    contexts.append(context_info)
                    
                except Exception as e:
                    print(f"  • 跳过损坏的上下文文件: {filepath.name} - {e}")
                    continue
            
            # 按创建时间倒序排列
            contexts.sort(key=lambda x: x['created_time'], reverse=True)
            
        except Exception as e:
            print(f"{Fore.RED}❌ 读取上下文目录失败: {e}{Style.RESET_ALL}")
        
        return contexts
    
    def _load_context_file(self, filepath: Path, context_manager) -> bool:
        """加载指定的上下文文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 恢复上下文数据
            context_manager.conversation_history = data.get('conversation_history', [])
            context_manager.project_context = data.get('project_context', {})
            context_manager.session_summary = data.get('session_summary', '')
            
            # 重新计算token数（如果缺失）
            for msg in context_manager.conversation_history:
                if 'tokens' not in msg:
                    msg['tokens'] = context_manager.count_tokens(msg['content'])
            
            context_name = data.get('name', filepath.stem)
            print(f"\n{theme_manager.format_tool_header('Load', context_name)}")
            print(f"  • 上下文已加载")
            
            # 显示加载的统计信息
            stats = context_manager.get_context_stats()
            print(f"{Fore.CYAN}📊 加载统计: {stats['conversation_messages']}条消息, {stats['total_tokens']:,} tokens{Style.RESET_ALL}")
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ 加载上下文文件失败: {e}{Style.RESET_ALL}")
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符"""
        import re
        # 移除或替换非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 限制长度
        if len(filename) > 50:
            filename = filename[:50]
        return filename.strip()

# 全局聊天管理器实例
chat_manager = ChatManager()
