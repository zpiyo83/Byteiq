#!/usr/bin/env python3
"""
测试不完整工具调用检测功能
"""

from src.ai_tools import AIToolProcessor

def test_incomplete_tool_detection():
    """测试不完整工具调用检测"""
    processor = AIToolProcessor()
    
    # 测试用例
    test_cases = [
        {
            "name": "完整的工具调用",
            "input": "<read_file><path>test.py</path></read_file>",
            "should_detect": False
        },
        {
            "name": "不完整的内容",
            "input": "<read_file></read_file>",
            "should_detect": True
        },
        {
            "name": "只有开始标签",
            "input": "<write_file",
            "should_detect": True
        },
        {
            "name": "缺少参数的工具调用",
            "input": "<create_file><path>test.py</path></create_file>",
            "should_detect": True
        },
        {
            "name": "正常文本",
            "input": "这是一段普通的文本，没有工具调用",
            "should_detect": False
        },
        {
            "name": "部分工具调用",
            "input": "我想要 <execute_command 执行一个命令",
            "should_detect": True
        }
    ]
    
    print("🧪 测试不完整工具调用检测功能\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试 {i}: {test_case['name']}")
        print(f"输入: {test_case['input']}")
        
        result = processor.process_response(test_case['input'])
        
        has_incomplete = result.get('has_tool') and '不完整' in result.get('tool_result', '')
        
        if has_incomplete == test_case['should_detect']:
            print("✅ 通过")
        else:
            print("❌ 失败")
            print(f"   期望检测: {test_case['should_detect']}")
            print(f"   实际检测: {has_incomplete}")
            if has_incomplete:
                print(f"   检测结果: {result.get('tool_result')}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_incomplete_tool_detection()
