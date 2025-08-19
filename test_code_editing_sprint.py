#!/usr/bin/env python3
"""
测试sprint模式下的代码编辑功能
"""

from src.ai_tools import ai_tool_processor
from src.modes import mode_manager

def test_sprint_mode():
    """测试sprint模式下的代码编辑"""
    print("=== 测试Sprint模式代码编辑 ===")
    
    # 切换到sprint模式
    mode_manager.current_mode = "sprint"
    print(f"当前模式: {mode_manager.get_current_mode()}")
    
    # 创建测试文件
    test_content = """def hello():
    print("Hello World")

def add(a, b):
    return a + b

def main():
    hello()
    result = add(1, 2)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
"""
    
    with open("test_sprint.py", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print("\n✅ 创建测试文件 test_sprint.py")
    print("原始内容:")
    for i, line in enumerate(test_content.split('\n'), 1):
        if line.strip():  # 只显示非空行
            print(f"{i:2d}: {line}")
    
    print("\n" + "="*60)
    
    # 测试插入代码
    print("\n📝 测试插入代码功能")
    xml_insert = '<insert_code><path>test_sprint.py</path><line>3</line><content>    # 这是插入的注释行</content></insert_code>'
    
    result = ai_tool_processor.process_response(xml_insert)
    print(f"插入结果: {result['tool_result']}")
    print(f"显示信息: {result['display_text']}")
    
    # 显示插入后的文件
    with open("test_sprint.py", "r", encoding="utf-8") as f:
        content = f.read()
    print("\n插入后的文件内容:")
    for i, line in enumerate(content.split('\n'), 1):
        if line.strip():  # 只显示非空行
            print(f"{i:2d}: {line}")
    
    print("\n" + "="*60)
    
    # 测试替换代码
    print("\n🔄 测试替换代码功能")
    xml_replace = '''<replace_code><path>test_sprint.py</path><start_line>5</start_line><end_line>6</end_line><content>def multiply(a, b):
    """计算两个数的乘积"""
    return a * b</content></replace_code>'''
    
    result = ai_tool_processor.process_response(xml_replace)
    print(f"替换结果: {result['tool_result']}")
    print(f"显示信息: {result['display_text']}")
    
    # 显示替换后的文件
    with open("test_sprint.py", "r", encoding="utf-8") as f:
        content = f.read()
    print("\n替换后的文件内容:")
    for i, line in enumerate(content.split('\n'), 1):
        if line.strip():  # 只显示非空行
            print(f"{i:2d}: {line}")
    
    # 清理
    import os
    try:
        os.remove("test_sprint.py")
        print("\n🗑️  清理测试文件")
    except:
        pass

if __name__ == "__main__":
    test_sprint_mode()
