#!/usr/bin/env python3
"""
AI思考状态动画显示
"""

import random
import time
import threading
import sys
from colorama import Fore, Style, init

# 初始化colorama
init(autoreset=True)

class ThinkingAnimation:
    """AI思考动画类"""
    
    def __init__(self):
        self.is_running = False
        self.animation_thread = None
        self.stop_event = threading.Event()
        
        # 思考状态词汇
        self.thinking_words = [
            "编码", "理解", "整理", "思考", "分析", 
            "规划", "设计", "构建", "优化", "检查"
        ]
        
        # 颜色配置
        self.text_color = Fore.CYAN
        self.highlight_color = Fore.WHITE + Style.BRIGHT
        self.dim_color = Fore.LIGHTBLACK_EX
        
    def start(self):
        """开始思考动画"""
        if self.is_running:
            return
            
        self.is_running = True
        self.stop_event.clear()
        self.animation_thread = threading.Thread(target=self._animate, daemon=True)
        self.animation_thread.start()
        
    def stop(self):
        """停止思考动画"""
        if not self.is_running:
            return

        self.is_running = False
        self.stop_event.set()

        # 等待线程结束，但不要无限等待
        if self.animation_thread and self.animation_thread.is_alive():
            try:
                self.animation_thread.join(timeout=2)
            except:
                pass

        # 强制清理
        self.animation_thread = None

        # 清除动画行
        try:
            self._clear_line()
        except:
            pass
        
    def _animate(self):
        """动画主循环"""
        while not self.stop_event.is_set():
            # 随机选择一个思考词汇
            word = random.choice(self.thinking_words)
            
            # 显示高光动画
            self._show_highlight_animation(word)
            
            # 等待一段时间再切换到下一个词
            if self.stop_event.wait(1.5):
                break
                
    def _show_highlight_animation(self, word):
        """显示单词的高光动画"""
        # 高光动画参数
        highlight_width = 1  # 高光宽度
        animation_speed = 0.12  # 动画速度

        # 先显示完整的暗色词汇
        dim_word = f"{self.dim_color}{word}{Style.RESET_ALL}"
        self._update_line(f"{dim_word}...")
        time.sleep(0.2)

        # 高光从左到右扫过
        for i in range(len(word)):
            if self.stop_event.is_set():
                break

            # 构建显示字符串
            display_chars = []

            for j, char in enumerate(word):
                if j == i:
                    # 当前字符高光
                    display_chars.append(f"{self.highlight_color}{char}{Style.RESET_ALL}")
                else:
                    # 其他字符正常颜色
                    display_chars.append(f"{self.text_color}{char}{Style.RESET_ALL}")

            # 显示当前帧
            display_text = "".join(display_chars)
            self._update_line(f"{display_text}...")

            # 等待下一帧
            time.sleep(animation_speed)

        # 再次高光扫过（第二遍）
        for i in range(len(word)):
            if self.stop_event.is_set():
                break

            # 构建显示字符串
            display_chars = []

            for j, char in enumerate(word):
                if j == i:
                    # 当前字符高光
                    display_chars.append(f"{self.highlight_color}{char}{Style.RESET_ALL}")
                else:
                    # 其他字符正常颜色
                    display_chars.append(f"{self.text_color}{char}{Style.RESET_ALL}")

            # 显示当前帧
            display_text = "".join(display_chars)
            self._update_line(f"{display_text}...")

            # 等待下一帧
            time.sleep(animation_speed * 0.8)  # 第二遍稍快一些

        # 最后显示完整的高亮词汇
        bright_word = f"{self.highlight_color}{word}{Style.RESET_ALL}"
        self._update_line(f"{bright_word}...")
        time.sleep(0.4)
        
    def _update_line(self, text):
        """更新当前行的显示"""
        # 移动到行首，清除行，显示新文本
        sys.stdout.write(f"\r{' ' * 50}\r{text}")
        sys.stdout.flush()
        
    def _clear_line(self):
        """清除当前行"""
        sys.stdout.write(f"\r{' ' * 50}\r")
        sys.stdout.flush()

# 全局动画实例
thinking_animation = ThinkingAnimation()

def start_thinking():
    """开始思考动画"""
    thinking_animation.start()
    
def stop_thinking():
    """停止思考动画"""
    thinking_animation.stop()

def show_simple_thinking(message="AI正在处理您的请求..."):
    """显示简单的思考消息（无动画）"""
    print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")

# 测试函数
def test_animation():
    """测试动画效果"""
    print("测试思考动画效果...")
    print("按Ctrl+C停止测试")
    
    try:
        start_thinking()
        time.sleep(10)  # 运行10秒
    except KeyboardInterrupt:
        print("\n测试被中断")
    finally:
        stop_thinking()
        print("动画测试结束")

if __name__ == "__main__":
    test_animation()
