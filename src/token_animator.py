"""
Token动画显示模块
提供上传和下载token的动态显示效果
"""

import threading
import time
import sys
from colorama import Fore, Style
import tiktoken

class TokenAnimator:
    def __init__(self):
        self.upload_active = False
        self.download_active = False
        self.upload_thread = None
        self.download_thread = None
        self.upload_current = 0
        self.upload_target = 0
        self.download_current = 0
        self.download_target = 0
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        try:
            return len(self.encoding.encode(text))
        except:
            # 简单估算：中文按2个字符=1token，英文按4个字符=1token
            chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
            other_chars = len(text) - chinese_chars
            return chinese_chars // 2 + other_chars // 4
    
    def start_upload_animation(self, text: str):
        """开始上传动画"""
        self.upload_target = self.count_tokens(text)
        self.upload_current = 0
        
        # 先停止之前的上传动画
        if self.upload_thread and self.upload_thread.is_alive():
            self.upload_active = False
            self.upload_thread.join(timeout=1)
        
        # 重新设置活动状态
        self.upload_active = True
            
        self.upload_thread = threading.Thread(target=self._upload_animation)
        self.upload_thread.daemon = True
        self.upload_thread.start()
    
    def start_download_animation(self, text: str):
        """开始下载动画"""
        self.download_target = self.count_tokens(text)
        self.download_current = 0
        
        # 先停止之前的下载动画
        if self.download_thread and self.download_thread.is_alive():
            self.download_active = False
            self.download_thread.join(timeout=1)
        
        # 重新设置活动状态
        self.download_active = True
            
        self.download_thread = threading.Thread(target=self._download_animation)
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def _upload_animation(self):
        """上传动画线程"""
        print(f"{Fore.CYAN}↑ 上传: {Fore.YELLOW}0{Style.RESET_ALL} tokens", end="", flush=True)
        
        while self.upload_active and self.upload_current < self.upload_target:
            # 计算增量，让动画更平滑
            increment = max(1, self.upload_target // 20)
            self.upload_current = min(self.upload_current + increment, self.upload_target)
            
            # 清除当前行并重新打印
            sys.stdout.write('\r')
            sys.stdout.write(' ' * 50)  # 清除行
            sys.stdout.write('\r')
            sys.stdout.write(f"{Fore.CYAN}↑ 上传: {Fore.YELLOW}{self.upload_current}{Style.RESET_ALL} tokens")
            sys.stdout.flush()
            
            time.sleep(0.15)  # 优化：减少CPU使用
        
        # 最终显示
        if self.upload_active:
            sys.stdout.write('\r')
            sys.stdout.write(' ' * 50)
            sys.stdout.write('\r')
            sys.stdout.write(f"{Fore.CYAN}↑ {Fore.GREEN}{self.upload_target}{Style.RESET_ALL} tokens\n")
            sys.stdout.flush()
    
    def _download_animation(self):
        """下载动画线程"""
        print(f"{Fore.MAGENTA}↓ 接收: {Fore.YELLOW}0{Style.RESET_ALL} tokens", end="", flush=True)
        
        while self.download_active and self.download_current < self.download_target:
            # 下载动画更快一些
            increment = max(1, self.download_target // 15)
            self.download_current = min(self.download_current + increment, self.download_target)
            
            # 清除当前行并重新打印
            sys.stdout.write('\r')
            sys.stdout.write(' ' * 50)
            sys.stdout.write('\r')
            sys.stdout.write(f"{Fore.MAGENTA}↓ 接收: {Fore.YELLOW}{self.download_current}{Style.RESET_ALL} tokens")
            sys.stdout.flush()
            
            time.sleep(0.08)  # 优化：减少CPU使用
        
        # 最终显示
        if self.download_active:
            sys.stdout.write('\r')
            sys.stdout.write(' ' * 50)
            sys.stdout.write('\r')
            sys.stdout.write(f"{Fore.MAGENTA}↓ {Fore.GREEN}{self.download_target}{Style.RESET_ALL} tokens\n")
            sys.stdout.flush()
    
    def stop_upload_animation(self):
        """停止上传动画"""
        self.upload_active = False
        if self.upload_thread and self.upload_thread.is_alive():
            self.upload_thread.join(timeout=1)
    
    def stop_download_animation(self):
        """停止下载动画"""
        self.download_active = False
        if self.download_thread and self.download_thread.is_alive():
            self.download_thread.join(timeout=1)
    
    def wait_upload_complete(self):
        """等待上传动画完成"""
        if self.upload_thread and self.upload_thread.is_alive():
            self.upload_thread.join()
    
    def wait_download_complete(self):
        """等待下载动画完成"""
        if self.download_thread and self.download_thread.is_alive():
            self.download_thread.join()
    
    def cleanup(self):
        """清理所有动画线程"""
        self.stop_upload_animation()
        self.stop_download_animation()

# 全局token动画器实例
token_animator = TokenAnimator()
