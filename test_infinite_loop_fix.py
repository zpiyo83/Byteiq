#!/usr/bin/env python3
"""
测试无限循环修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from forgeai import AIToolProcessor

def test_should_continue_logic():
    """测试should_continue逻辑"""
    print("=== 测试should_continue逻辑 ===\n")
    
    processor = AIToolProcessor()
    
    # 测试用例
    test_cases = [
        {
            "name": "包含task_complete",
            "response": "任务完成 <task_complete><summary>完成了文件创建</summary></task_complete>",
            "expected": False
        },
        {
            "name": "只有工具调用，响应很短",
            "response": "<create_file><path>test.py</path><content>print('hello')</content></create_file>",
            "expected": True
        },
        {
            "name": "包含继续关键词",
            "response": "文件已创建，接下来我将继续添加更多功能 <create_file><path>test2.py</path><content>code</content></create_file>",
            "expected": True
        },
        {
            "name": "正常完成，无继续意图",
            "response": "我为您创建了文件，包含了所需的功能。文件已保存到指定位置。 <create_file><path>app.py</path><content>完整的应用代码</content></create_file>",
            "expected": False
        },
        {
            "name": "没有工具调用",
            "response": "这是一个普通的回答，没有工具调用。",
            "expected": False
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. 测试: {case['name']}")
        result = processor.process_response(case['response'])
        actual = result['should_continue']
        expected = case['expected']
        
        status = "✅ 通过" if actual == expected else "❌ 失败"
        print(f"   预期: {expected}, 实际: {actual} - {status}")
        
        if actual != expected:
            print(f"   响应: {case['response'][:100]}...")
        print()

def test_iteration_limit():
    """测试迭代限制"""
    print("=== 测试迭代限制 ===\n")
    
    print("模拟场景: AI一直返回需要继续的响应")
    print("预期结果: 在10次迭代后自动停止")
    print("实际测试需要在真实环境中进行")
    print()

def show_fix_summary():
    """显示修复总结"""
    print("=== 修复总结 ===\n")
    
    print("🔧 修复的问题:")
    print("   - AI处理卡住不动")
    print("   - 无限循环导致程序无响应")
    print("   - 缺少循环保护机制")
    
    print("\n💡 修复方案:")
    print("   1. 添加最大迭代次数限制 (10次)")
    print("   2. 改进should_continue判断逻辑")
    print("   3. 添加迭代计数显示")
    print("   4. 智能检测继续条件")
    
    print("\n✅ 修复效果:")
    print("   - 防止无限循环")
    print("   - 提供清晰的进度反馈")
    print("   - 智能判断何时停止")
    print("   - 保持功能完整性")
    
    print("\n🎯 新的判断逻辑:")
    print("   - task_complete -> 停止")
    print("   - 响应很短 + 有工具 -> 继续")
    print("   - 包含继续关键词 -> 继续")
    print("   - 其他情况 -> 停止")

if __name__ == "__main__":
    test_should_continue_logic()
    test_iteration_limit()
    show_fix_summary()
