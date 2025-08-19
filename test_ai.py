#!/usr/bin/env python3
"""
测试AI功能的简单脚本
"""

from src.ai_client import ai_client
from src.ai_tools import ai_tool_processor
from src.config import load_config

def test_ai_without_api():
    """测试没有API密钥时的行为"""
    print("=== 测试没有API密钥的情况 ===")
    config = load_config()
    print(f"当前配置: {config}")
    
    if not config.get('api_key'):
        print("✓ 没有API密钥，这是预期的")
    else:
        print(f"API密钥存在: {config.get('api_key')[:10]}...")

def test_tool_processor():
    """测试工具处理器"""
    print("\n=== 测试工具处理器 ===")
    
    # 测试XML解析
    test_responses = [
        "这是普通文本，没有工具调用",
        "<create_file><path>test.py</path><content>print('hello')</content></create_file>",
        "<read_file><path>test.py</path></read_file>",
        "我要创建一个文件 <create_file><path>example.txt</path><content>Hello World\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6</content></create_file> 完成",
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"\n--- 测试 {i} ---")
        print(f"输入: {response}")
        result = ai_tool_processor.process_response(response)
        print(f"有工具: {result['has_tool']}")
        print(f"显示文本: {result['display_text']}")
        if result['tool_result']:
            print(f"工具结果: {result['tool_result']}")

def test_project_structure():
    """测试项目结构获取"""
    print("\n=== 测试项目结构获取 ===")
    structure = ai_client.get_project_structure()
    print("项目结构:")
    print(structure)

if __name__ == "__main__":
    test_ai_without_api()
    test_tool_processor()
    test_project_structure()
