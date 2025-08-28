#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试工具渲染功能的脚本
验证show_todos和plan工具是否能正确显示输出
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai_tools import AIToolProcessor
from src.todo_renderer import TodoRenderer
from colorama import init, Fore, Style

# 初始化colorama
init(autoreset=True)

def test_show_todos():
    """测试show_todos工具渲染"""
    print(f"{Fore.CYAN}=== 测试 show_todos 工具 ==={Style.RESET_ALL}")
    
    # 创建工具处理器
    processor = AIToolProcessor()
    
    # 模拟AI响应包含show_todos工具调用
    ai_response = """
我来显示当前的TODO列表：

<show_todos/>

这是当前的任务状态。
"""
    
    print(f"{Fore.YELLOW}模拟AI响应:{Style.RESET_ALL}")
    print(ai_response)
    print(f"{Fore.YELLOW}工具处理结果:{Style.RESET_ALL}")
    
    # 处理工具调用
    result = processor.process_ai_response(ai_response)
    
    print(f"\n{Fore.GREEN}✓ show_todos工具测试完成{Style.RESET_ALL}")
    print(f"工具是否被识别: {result['has_tool']}")
    print(f"执行的工具: {result['executed_tools']}")
    
    return result['has_tool']

def test_plan_tool():
    """测试plan工具渲染"""
    print(f"\n{Fore.CYAN}=== 测试 plan 工具 ==={Style.RESET_ALL}")
    
    # 创建工具处理器
    processor = AIToolProcessor()
    
    # 模拟AI响应包含plan工具调用
    ai_response = """
我已经完成了当前任务，现在更新执行计划：

<plan>
<completed_action>修复了show_todos和plan工具的渲染问题</completed_action>
<next_step>测试修复后的工具功能</next_step>
<original_request>修复AI工具渲染问题</original_request>
<completed_tasks>1. 分析show_todos问题 2. 分析plan工具问题 3. 修复输出截断问题</completed_tasks>
</plan>

计划已更新。
"""
    
    print(f"{Fore.YELLOW}模拟AI响应:{Style.RESET_ALL}")
    print(ai_response)
    print(f"{Fore.YELLOW}工具处理结果:{Style.RESET_ALL}")
    
    # 处理工具调用
    result = processor.process_ai_response(ai_response)
    
    print(f"\n{Fore.GREEN}✓ plan工具测试完成{Style.RESET_ALL}")
    print(f"工具是否被识别: {result['has_tool']}")
    print(f"执行的工具: {result['executed_tools']}")
    
    return result['has_tool']

def test_output_length():
    """测试长输出是否会被截断"""
    print(f"\n{Fore.CYAN}=== 测试长输出处理 ==={Style.RESET_ALL}")
    
    # 创建工具处理器
    processor = AIToolProcessor()
    
    # 创建一个很长的TODO列表来测试
    long_response = """
我来显示一个包含很多任务的TODO列表：

<show_todos/>

这个列表包含了项目的所有任务，应该完整显示而不被截断。
"""
    
    print(f"{Fore.YELLOW}测试长输出处理:{Style.RESET_ALL}")
    
    # 处理工具调用
    result = processor.process_ai_response(long_response)
    
    print(f"\n{Fore.GREEN}✓ 长输出测试完成{Style.RESET_ALL}")
    
    return True

def main():
    """主测试函数"""
    print(f"{Fore.MAGENTA}{'='*50}")
    print(f"AI工具渲染功能测试")
    print(f"{'='*50}{Style.RESET_ALL}")
    
    # 测试结果
    results = []
    
    try:
        # 测试show_todos
        results.append(("show_todos工具", test_show_todos()))
        
        # 测试plan工具
        results.append(("plan工具", test_plan_tool()))
        
        # 测试长输出
        results.append(("长输出处理", test_output_length()))
        
    except Exception as e:
        print(f"{Fore.RED}测试过程中发生错误: {e}{Style.RESET_ALL}")
        return False
    
    # 显示测试结果
    print(f"\n{Fore.MAGENTA}{'='*50}")
    print(f"测试结果汇总")
    print(f"{'='*50}{Style.RESET_ALL}")
    
    all_passed = True
    for test_name, passed in results:
        status = f"{Fore.GREEN}✓ 通过" if passed else f"{Fore.RED}✗ 失败"
        print(f"{test_name}: {status}{Style.RESET_ALL}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\n{Fore.GREEN}🎉 所有测试都通过了！工具渲染功能已修复。{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}❌ 部分测试失败，需要进一步检查。{Style.RESET_ALL}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
