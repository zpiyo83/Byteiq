"""
延迟加载器 - 优化ByteIQ启动性能
"""

import importlib
from typing import Any, Dict, Optional

class LazyLoader:
    """延迟加载器，用于按需导入模块"""
    
    def __init__(self):
        self._modules: Dict[str, Any] = {}
        self._loading = set()
    
    def get_module(self, module_name: str, reload: bool = False) -> Optional[Any]:
        """获取模块，首次访问时才导入"""
        if module_name in self._loading:
            # 防止循环导入
            return None
            
        if module_name not in self._modules or reload:
            try:
                self._loading.add(module_name)
                self._modules[module_name] = importlib.import_module(module_name)
            except ImportError as e:
                print(f"延迟加载失败: {module_name} - {e}")
                return None
            finally:
                self._loading.discard(module_name)
        
        return self._modules[module_name]
    
    def get_ai_client(self):
        """获取AI客户端"""
        module = self.get_module('src.ai_client')
        return getattr(module, 'ai_client', None) if module else None
    
    def get_ai_tools(self):
        """获取AI工具处理器"""
        module = self.get_module('src.ai_tools')
        return getattr(module, 'ai_tool_processor', None) if module else None
    
    def get_keyboard_handler(self):
        """获取键盘处理器"""
        module = self.get_module('src.keyboard_handler')
        if module:
            return {
                'stop_task_monitoring': getattr(module, 'stop_task_monitoring', None),
                'is_task_interrupted': getattr(module, 'is_task_interrupted', None),
                'reset_interrupt_flag': getattr(module, 'reset_interrupt_flag', None)
            }
        return {}
    
    def get_input_handler(self):
        """获取输入处理器"""
        module = self.get_module('src.input_handler')
        return getattr(module, 'get_input_with_claude_style', None) if module else None
    
    def get_mcp_config(self):
        """获取MCP配置"""
        module = self.get_module('src.mcp_config')
        return getattr(module, 'mcp_config', None) if module else None
    
    def get_mcp_client(self):
        """获取MCP客户端"""
        module = self.get_module('src.mcp_client')
        return getattr(module, 'mcp_client', None) if module else None

# 全局延迟加载器实例
lazy_loader = LazyLoader()
