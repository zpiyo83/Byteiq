#!/usr/bin/env python3
"""
AI思考状态动画显示
"""

import random
import time
import threading
import asyncio
import itertools
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
            "思考", "构建", "理解", "摸鱼", "整理",
            "规划", "吐槽", "分析", "编码", "设计",
            "优化", "检查", "琢磨", "构思", "推演",
            "推敲", "酝酿", "实现", "开发", "调试",
            "测试", "梳理", "归纳", "演绎", "剖析",
            "研判", "改进", "迭代", "审核", "校验",
            "复盘", "总结", "钻研", "探究", "摸索",
            "冥想", "沉思", "盘算", "策划", "部署",
            "评估", "权衡", "考量", "解读", "阐释",
            "编译", "重构", "复审", "排查", "调侃",
            "划水", "斟酌", "思忖", "揣摩", "思辨",
            "创作", "撰写", "草拟", "推进", "实施",
            "集成", "运维", "规整", "核查", "反刍",
            "闲聊", "打磨", "雕琢", "擘画", "筹谋",
            "研析", "品析", "解构", "搭建", "回味",
            "念叨", "嘀咕", "捋顺"
        ]

        # 颜色配置
        self.text_color = Fore.CYAN
        self.highlight_color = Fore.WHITE + Style.BRIGHT
        self.dim_color = Fore.LIGHTBLACK_EX

    def start(self):
        """开始思考动画"""
        # 先输出一个换行符
        print()
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
        frames = itertools.cycle(['·', '•', '●', '◆', '●', '•'])
        word_change_counter = 0
        word = random.choice(self.thinking_words)

        while not self.stop_event.is_set():
            frame = next(frames)

            # 每隔一段时间（约1.5秒）更换一次文字
            if word_change_counter >= 15: # 15 * 0.1s = 1.5s
                word = random.choice(self.thinking_words)
                word_change_counter = 0

            self._update_line(f"{frame} {word}中...")
            time.sleep(0.12)  # 优化：减少CPU使用
            word_change_counter += 1



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

def show_dot_cycle_animation(action_text="执行", duration=0.3):
    """显示一个短暂的点循环动画（阻塞式），用于快速操作。"""
    frames = itertools.cycle(['·', '•', '●', '◆', '●', '•'])
    start_time = time.time()

    while time.time() - start_time < duration:
        frame = next(frames)
        # The extra spaces at the end are to overwrite previous, longer text
        print(f"\r{Fore.CYAN}{frame} {action_text}...          {Style.RESET_ALL}", end="")
        time.sleep(0.1)

    # Clear the animation line
    print(f"\r{' ' * (len(action_text) + 20)}\r", end="")

async def show_dot_cycle_animation_async(action_text, duration=1.0):
    """显示一个短暂的点循环动画（异步版本）"""
    frames = ['·', '•', '●', '◆', '●', '•']
    start_time = time.time()
    frame_index = 0

    try:
        while time.time() - start_time < duration:
            frame = frames[frame_index % len(frames)]
            print(f"\r{Fore.CYAN}{frame} {action_text}...{Style.RESET_ALL}", end="")
            await asyncio.sleep(0.1)
            frame_index += 1
    except asyncio.CancelledError:
        pass
    finally:
        print("\r" + " " * (len(action_text) + 20) + "\r", end="")


