"""
性能监控模块
提供实时性能监控和报告功能
"""

import time
import psutil
import threading
from typing import Dict, List
from colorama import Fore, Style

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            'memory_peak': 0,
            'cpu_peak': 0,
            'function_calls': {},
            'slow_operations': []
        }
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """开始性能监控"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 获取内存使用
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                self.metrics['memory_peak'] = max(self.metrics['memory_peak'], memory_mb)
                
                # 获取CPU使用率
                cpu_percent = psutil.Process().cpu_percent()
                self.metrics['cpu_peak'] = max(self.metrics['cpu_peak'], cpu_percent)
                
                time.sleep(1)  # 每秒检查一次
            except:
                pass
    
    def record_function_call(self, func_name: str, duration: float):
        """记录函数调用"""
        if func_name not in self.metrics['function_calls']:
            self.metrics['function_calls'][func_name] = {
                'count': 0,
                'total_time': 0,
                'max_time': 0
            }
        
        stats = self.metrics['function_calls'][func_name]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['max_time'] = max(stats['max_time'], duration)
        
        # 记录慢操作
        if duration > 2.0:  # 超过2秒
            self.metrics['slow_operations'].append({
                'function': func_name,
                'duration': duration,
                'timestamp': time.time()
            })
    
    def get_performance_report(self) -> str:
        """生成性能报告"""
        uptime = time.time() - self.start_time
        
        report = f"""
{Fore.CYAN}=== 性能监控报告 ==={Style.RESET_ALL}

{Fore.WHITE}运行时间:{Style.RESET_ALL} {uptime:.1f} 秒
{Fore.WHITE}内存峰值:{Style.RESET_ALL} {self.metrics['memory_peak']:.1f} MB
{Fore.WHITE}CPU峰值:{Style.RESET_ALL} {self.metrics['cpu_peak']:.1f}%

{Fore.WHITE}函数调用统计:{Style.RESET_ALL}"""
        
        # 按平均执行时间排序
        sorted_functions = sorted(
            self.metrics['function_calls'].items(),
            key=lambda x: x[1]['total_time'] / x[1]['count'],
            reverse=True
        )
        
        for func_name, stats in sorted_functions[:5]:  # 只显示前5个
            avg_time = stats['total_time'] / stats['count']
            report += f"""
  {func_name}: {stats['count']}次调用, 平均{avg_time:.3f}s, 最大{stats['max_time']:.3f}s"""
        
        # 慢操作
        if self.metrics['slow_operations']:
            report += f"\n\n{Fore.YELLOW}慢操作记录:{Style.RESET_ALL}"
            for op in self.metrics['slow_operations'][-3:]:  # 只显示最近3个
                report += f"""
  {op['function']}: {op['duration']:.2f}秒"""
        
        return report
    
    def get_optimization_suggestions(self) -> List[str]:
        """获取优化建议"""
        suggestions = []
        
        if self.metrics['memory_peak'] > 200:
            suggestions.append("内存使用较高，考虑优化数据结构或增加垃圾回收")
        
        if self.metrics['cpu_peak'] > 80:
            suggestions.append("CPU使用率较高，考虑优化算法或减少计算密集操作")
        
        slow_ops = len(self.metrics['slow_operations'])
        if slow_ops > 5:
            suggestions.append(f"检测到{slow_ops}个慢操作，考虑优化相关函数")
        
        return suggestions

# 全局监控器实例
performance_monitor = PerformanceMonitor()

def monitor_function(func):
    """函数性能监控装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            performance_monitor.record_function_call(func.__name__, duration)
    return wrapper
