#!/usr/bin/env python3
"""
键盘事件处理器
"""

import threading
import sys
import msvcrt  # Windows专用
from colorama import Fore, Style

class KeyboardHandler:
    """键盘事件处理器"""
    
    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.interrupt_callback = None
        
    def start_monitoring(self, interrupt_callback=None):
        """开始监控键盘事件"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.stop_event.clear()
        self.interrupt_callback = interrupt_callback
        
        self.monitor_thread = threading.Thread(target=self._monitor_keys, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """停止监控键盘事件"""
        if not self.is_monitoring:
            return

        self.is_monitoring = False
        self.stop_event.set()

        # 等待线程结束，但不要无限等待
        if self.monitor_thread and self.monitor_thread.is_alive():
            try:
                self.monitor_thread.join(timeout=1)
            except:
                pass

        # 强制清理
        self.monitor_thread = None
            
    def _monitor_keys(self):
        """监控键盘按键"""
        while not self.stop_event.is_set():
            try:
                # 检查是否有按键
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    
                    # ESC键的ASCII码是27
                    if ord(key) == 27:
                        self._handle_escape()
                        break
                        
                # 短暂休眠避免CPU占用过高
                self.stop_event.wait(0.1)
                
            except Exception as e:
                # 忽略键盘监控错误
                pass
                
    def _handle_escape(self):
        """处理ESC键按下"""
        print(f"\n{Fore.YELLOW}检测到ESC键，正在停止任务...{Style.RESET_ALL}")
        
        if self.interrupt_callback:
            self.interrupt_callback()
            
        self.stop_monitoring()

# 全局键盘处理器实例
keyboard_handler = KeyboardHandler()

def start_task_monitoring(interrupt_callback=None):
    """开始任务监控（监听ESC键）"""
    keyboard_handler.start_monitoring(interrupt_callback)
    
def stop_task_monitoring():
    """停止任务监控"""
    keyboard_handler.stop_monitoring()

def show_esc_hint():
    """显示ESC提示"""
    print(f"{Fore.LIGHTBLACK_EX}提示: 按ESC键可随时停止任务{Style.RESET_ALL}")

# 任务中断标志
task_interrupted = threading.Event()

def interrupt_current_task():
    """中断当前任务"""
    task_interrupted.set()
    
def is_task_interrupted():
    """检查任务是否被中断"""
    return task_interrupted.is_set()
    
def reset_interrupt_flag():
    """重置中断标志"""
    task_interrupted.clear()

# 测试函数
def test_keyboard_handler():
    """测试键盘处理器"""
    print("测试键盘处理器...")
    print("按ESC键测试中断功能，按Ctrl+C退出测试")
    
    def on_interrupt():
        print("任务被中断！")
        
    try:
        start_task_monitoring(on_interrupt)
        show_esc_hint()
        
        # 模拟长时间任务
        import time
        for i in range(30):
            if is_task_interrupted():
                print("检测到中断，退出循环")
                break
            print(f"模拟任务进行中... {i+1}/30")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n测试被Ctrl+C中断")
    finally:
        stop_task_monitoring()
        print("键盘处理器测试结束")

if __name__ == "__main__":
    test_keyboard_handler()
