#!/usr/bin/env python3
"""
简单测试AI功能
"""

from src.ai_client import ai_client
from src.ai_tools import ai_tool_processor

def test_simple_request():
    """测试简单的AI请求"""
    print("=== 测试简单AI请求 ===")
    
    # 测试简单的文件创建
    user_input = "创建一个简单的hello.py文件，内容是print('Hello World')"
    
    print(f"用户输入: {user_input}")
    print("发送给AI...")
    
    # 发送消息给AI
    ai_response = ai_client.send_message(user_input)
    print(f"AI响应: {ai_response}")
    
    # 处理AI响应
    result = ai_tool_processor.process_response(ai_response)
    print(f"工具处理结果: {result}")

if __name__ == "__main__":
    test_simple_request()
