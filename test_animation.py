#!/usr/bin/env python3
"""
测试动画效果
"""

from src.thinking_animation import show_dot_cycle_animation
import time

def test_dot_cycle_animation():
    """测试循环点动画"""
    print("测试循环点动画...")
    
    # 测试不同消息的动画
    messages = ["AI正在思考", "AI正在处理", "AI正在执行工具", "AI完成任务"]
    
    for message in messages:
        print(f"\n测试消息: {message}")
        stop_animation = show_dot_cycle_animation(message)
        time.sleep(3)  # 显示3秒
        stop_animation()
        print(f"{message} 完成!")
    
    print("\n所有动画测试完成!")

if __name__ == "__main__":
    test_dot_cycle_animation()