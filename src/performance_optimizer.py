"""
性能优化模块
提供启动速度、内存使用和响应时间的优化功能
"""

import time
import threading
import gc
import sys
import psutil
from typing import Dict, List, Optional
from functools import lru_cache
import weakref

class PerformanceOptimizer:
    def __init__(self):
        self.startup_time = time.time()
        self.module_cache = {}
        self.thread_pool = []
        self.memory_threshold = 500 * 1024 * 1024  # 500MB
        self.gc_interval = 30  # 30秒
        self.last_gc_time = time.time()
        
    def optimize_startup(self):
        """优化启动性能"""
        # 预编译正则表达式
        self._precompile_patterns()
        
        # 预热关键模块
        self._warmup_modules()
        
        # 设置垃圾回收策略
        self._configure_gc()
        
    def _precompile_patterns(self):
        """预编译常用正则表达式"""
        import re
        patterns = [
            r'<tool_call>(.*?)</tool_call>',
            r'<tool_name>(.*?)</tool_name>',
            r'<parameters>(.*?)</parameters>',
            r'\[([^\]]+)\]',
            r'```(\w+)?\n(.*?)```'
        ]
        
        self.compiled_patterns = {}
        for pattern in patterns:
            self.compiled_patterns[pattern] = re.compile(pattern, re.DOTALL)
    
    def _warmup_modules(self):
        """预热关键模块"""
        try:
            # 预热tiktoken
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            encoding.encode("warmup")
            
            # 预热colorama
            from colorama import Fore, Style
            
            # 预热json
            import json
            json.dumps({"test": "warmup"})
            
        except ImportError:
            pass
    
    def _configure_gc(self):
        """配置垃圾回收"""
        import gc
        # 设置更激进的垃圾回收阈值
        gc.set_threshold(700, 10, 10)
        # 启用垃圾回收调试（仅在开发模式）
        # gc.set_debug(gc.DEBUG_STATS)
    
    def optimize_memory(self):
        """优化内存使用"""
        current_memory = self.get_memory_usage()
        
        if current_memory > self.memory_threshold:
            self._force_garbage_collection()
            self._cleanup_thread_pool()
            self._clear_module_cache()
    
    def get_memory_usage(self) -> int:
        """获取当前内存使用量（字节）"""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except:
            return 0
    
    def _force_garbage_collection(self):
        """强制垃圾回收"""
        import gc
        collected = gc.collect()
        self.last_gc_time = time.time()
        return collected
    
    def _cleanup_thread_pool(self):
        """清理线程池"""
        # 移除已完成的线程
        self.thread_pool = [t for t in self.thread_pool if t.is_alive()]
    
    def _clear_module_cache(self):
        """清理模块缓存"""
        # 清理弱引用缓存
        self.module_cache.clear()
    
    def optimize_animation_performance(self):
        """优化动画性能"""
        # 减少动画帧率以节省CPU
        return {
            'upload_interval': 0.15,  # 从0.1增加到0.15
            'download_interval': 0.08,  # 从0.05增加到0.08
            'thinking_interval': 0.12   # 从0.1增加到0.12
        }
    
    def create_thread_pool(self, max_threads: int = 3):
        """创建受限的线程池"""
        if len(self.thread_pool) >= max_threads:
            # 等待最老的线程完成
            oldest_thread = self.thread_pool.pop(0)
            if oldest_thread.is_alive():
                oldest_thread.join(timeout=1)
    
    def monitor_performance(self) -> Dict:
        """监控性能指标"""
        current_time = time.time()
        uptime = current_time - self.startup_time
        memory_mb = self.get_memory_usage() / 1024 / 1024
        
        return {
            'uptime_seconds': uptime,
            'memory_mb': memory_mb,
            'active_threads': threading.active_count(),
            'cached_modules': len(self.module_cache),
            'last_gc_seconds_ago': current_time - self.last_gc_time
        }
    
    def should_run_gc(self) -> bool:
        """判断是否应该运行垃圾回收"""
        return (time.time() - self.last_gc_time) > self.gc_interval
    
    def get_optimization_suggestions(self) -> List[str]:
        """获取优化建议"""
        suggestions = []
        stats = self.monitor_performance()
        
        if stats['memory_mb'] > 300:
            suggestions.append("内存使用较高，建议重启程序")
        
        if stats['active_threads'] > 10:
            suggestions.append("线程数量较多，可能影响性能")
        
        if stats['uptime_seconds'] > 3600:  # 1小时
            suggestions.append("程序运行时间较长，建议定期重启")
        
        return suggestions

# 单例模式
_performance_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """获取性能优化器实例"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer

# 装饰器：性能监控
def performance_monitor(func):
    """性能监控装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            if execution_time > 1.0:  # 超过1秒的函数记录
                print(f"⚠️ 函数 {func.__name__} 执行时间: {execution_time:.2f}秒")
    return wrapper

# LRU缓存装饰器的优化版本
def optimized_lru_cache(maxsize=128):
    """优化的LRU缓存，支持内存压力时自动清理"""
    def decorator(func):
        cached_func = lru_cache(maxsize=maxsize)(func)
        
        def wrapper(*args, **kwargs):
            optimizer = get_performance_optimizer()
            
            # 如果内存压力大，清理缓存
            if optimizer.get_memory_usage() > optimizer.memory_threshold:
                cached_func.cache_clear()
            
            return cached_func(*args, **kwargs)
        
        wrapper.cache_info = cached_func.cache_info
        wrapper.cache_clear = cached_func.cache_clear
        return wrapper
    
    return decorator
