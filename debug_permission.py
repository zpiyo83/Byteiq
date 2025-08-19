#!/usr/bin/env python3
"""
调试权限控制问题
"""

from src.modes import mode_manager
from src.ai_tools import ai_tool_processor

def test_permission_control():
    """测试权限控制"""
    print("=== 调试权限控制问题 ===\n")
    
    # 检查当前模式
    print(f"当前模式: {mode_manager.get_current_mode()}")
    
    # 测试各种工具的权限
    tools_to_test = ['read_file', 'create_file', 'write_file', 'execute_command']
    
    for tool in tools_to_test:
        permission = mode_manager.can_auto_execute(tool)
        print(f"{tool}: {permission}")
    
    print("\n=== 测试Ask模式下的create_file ===")
    
    # 确保在Ask模式
    mode_manager.current_mode = "Ask"
    print(f"设置模式为: {mode_manager.get_current_mode()}")
    
    # 测试create_file权限
    permission = mode_manager.can_auto_execute('create_file')
    print(f"create_file权限: {permission}")
    
    # 模拟AI响应
    ai_response = '<create_file><path>test.py</path><content>print("hello")</content></create_file>'
    print(f"\n模拟AI响应: {ai_response}")
    
    # 处理响应
    result = ai_tool_processor.process_response(ai_response)
    print(f"处理结果: {result}")

def test_all_modes():
    """测试所有模式的权限"""
    print("\n=== 测试所有模式的权限 ===\n")
    
    modes = ["Ask", "mostly accepted", "sprint"]
    tools = ['create_file', 'write_file', 'execute_command']
    
    for mode in modes:
        print(f"\n{mode} 模式:")
        mode_manager.current_mode = mode
        for tool in tools:
            permission = mode_manager.can_auto_execute(tool)
            print(f"  {tool}: {permission}")

if __name__ == "__main__":
    test_permission_control()
    test_all_modes()
