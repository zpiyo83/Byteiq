#!/usr/bin/env python3
"""
测试点循环动画
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.thinking_animation import show_dot_cycle_animation

def test_dot_cycle():
    """测试点循环动画"""
    print("测试点循环动画...")
    show_dot_cycle_animation("AI正在思考", 2.0)
    print("动画测试完成!")

if __name__ == "__main__":
    test_dot_cycle()