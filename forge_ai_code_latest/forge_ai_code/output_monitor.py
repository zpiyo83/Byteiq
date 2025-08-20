#!/usr/bin/env python3
"""
输出监控模块 - 监控命令行输出，防止程序卡死
"""

import threading
import time
import sys
from colorama import Fore, Style

class OutputMonitor:
    """输出监控器 - 检测程序是否长时间无输出"""
    
    def __init__(self, timeout_seconds=15):
        self.timeout_seconds = timeout_seconds
        self.last_output_time = time.time()
        self.is_monitoring = False
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.timeout_callback = None
        self.lock = threading.Lock()
        
    def start_monitoring(self, timeout_callback=None):
        """开始监控输出"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.stop_event.clear()
        self.timeout_callback = timeout_callback
        self.last_output_time = time.time()
        
        self.monitor_thread = threading.Thread(target=self._monitor_output, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """停止监控输出"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            try:
                self.monitor_thread.join(timeout=1)
            except:
                pass
                
        self.monitor_thread = None
        
    def update_output_time(self):
        """更新最后输出时间"""
        with self.lock:
            self.last_output_time = time.time()
            
    def _monitor_output(self):
        """监控输出的主循环"""
        while not self.stop_event.is_set():
            try:
                current_time = time.time()
                
                with self.lock:
                    time_since_last_output = current_time - self.last_output_time
                
                # 检查是否超时
                if time_since_last_output > self.timeout_seconds:
                    self._handle_timeout()
                    break
                    
                # 每秒检查一次
                self.stop_event.wait(1)
                
            except Exception as e:
                # 忽略监控过程中的异常
                pass
                
    def _handle_timeout(self):
        """处理超时情况"""
        print(f"\n{Fore.YELLOW}⚠️ 检测到程序超过{self.timeout_seconds}秒无输出，可能卡死{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}正在自动恢复...{Style.RESET_ALL}")
        
        if self.timeout_callback:
            try:
                self.timeout_callback()
            except Exception as e:
                print(f"{Fore.RED}自动恢复时出错: {e}{Style.RESET_ALL}")
                
        self.stop_monitoring()

# 全局输出监控器实例
output_monitor = OutputMonitor()

def start_output_monitoring(timeout_callback=None, timeout_seconds=15):
    """开始输出监控"""
    output_monitor.timeout_seconds = timeout_seconds
    output_monitor.start_monitoring(timeout_callback)
    
def stop_output_monitoring():
    """停止输出监控"""
    output_monitor.stop_monitoring()
    
def update_output_time():
    """更新输出时间（在有输出时调用）"""
    output_monitor.update_output_time()

# 重写print函数，自动更新输出时间
original_print = print

def monitored_print(*args, **kwargs):
    """带监控的print函数"""
    try:
        result = original_print(*args, **kwargs)
        update_output_time()
        return result
    except Exception as e:
        # 如果print失败，尝试基本输出
        try:
            import sys
            sys.__stdout__.write(str(args) + '\n')
            sys.__stdout__.flush()
            update_output_time()
        except Exception:
            # 如果还是失败，忽略错误
            pass

# 重写sys.stdout.write，捕获所有输出
class MonitoredStdout:
    """监控的标准输出"""

    def __init__(self, original_stdout):
        self.original_stdout = original_stdout

    def write(self, text):
        try:
            result = self.original_stdout.write(text)
            if text.strip():  # 只有非空输出才更新时间
                update_output_time()
            return result
        except Exception:
            # 如果写入失败，尝试直接写入原始stdout
            try:
                return self.original_stdout.write(text)
            except Exception:
                # 如果还是失败，忽略错误
                return len(text)

    def flush(self):
        try:
            return self.original_stdout.flush()
        except Exception:
            # 忽略flush错误
            pass

    def __getattr__(self, name):
        try:
            return getattr(self.original_stdout, name)
        except Exception:
            # 如果获取属性失败，返回None
            return None

original_stdout = sys.stdout

def enable_stdout_monitoring():
    """启用stdout监控"""
    sys.stdout = MonitoredStdout(original_stdout)

def disable_stdout_monitoring():
    """禁用stdout监控"""
    sys.stdout = original_stdout

def enable_print_monitoring():
    """启用print监控"""
    import builtins
    builtins.print = monitored_print
    enable_stdout_monitoring()

def disable_print_monitoring():
    """禁用print监控"""
    import builtins
    builtins.print = original_print
    disable_stdout_monitoring()

# 测试函数
def test_output_monitor():
    """测试输出监控器"""
    print("测试输出监控器...")
    
    def on_timeout():
        print("检测到超时！")
        
    # 启用print监控
    enable_print_monitoring()
    
    try:
        start_output_monitoring(on_timeout, timeout_seconds=5)
        
        print("开始测试，5秒后应该触发超时...")
        time.sleep(3)
        print("3秒过去了...")
        time.sleep(3)  # 总共6秒，应该触发超时
        print("这行不应该被打印，因为应该已经超时了")
        
    except Exception as e:
        print(f"测试出错: {e}")
    finally:
        stop_output_monitoring()
        disable_print_monitoring()
        print("测试结束")

if __name__ == "__main__":
    test_output_monitor()
