#!/usr/bin/env python3
"""
测试代码编辑工具
"""

from src.ai_tools import ai_tool_processor
from src.modes import mode_manager

def create_test_file():
    """创建测试文件"""
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
    
    with open("test_sample.py", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print("✅ 创建测试文件 test_sample.py")
    print("原始内容:")
    print(test_content)
    print("-" * 50)

def test_insert_code():
    """测试插入代码功能"""
    print("\n=== 测试插入代码功能 ===")
    
    # 测试在第3行插入代码
    xml = '<insert_code><path>test_sample.py</path><line>3</line><content>    # 这是插入的注释</content></insert_code>'
    
    print(f"测试XML: {xml}")
    result = ai_tool_processor.process_response(xml)
    print(f"结果: {result['tool_result']}")
    print(f"显示: {result['display_text']}")
    
    # 显示修改后的文件内容
    with open("test_sample.py", "r", encoding="utf-8") as f:
        content = f.read()
    print("\n修改后的文件内容:")
    for i, line in enumerate(content.split('\n'), 1):
        print(f"{i:2d}: {line}")

def test_replace_code():
    """测试替换代码功能"""
    print("\n=== 测试替换代码功能 ===")
    
    # 测试替换第4-5行
    xml = '''<replace_code><path>test_sample.py</path><start_line>4</start_line><end_line>5</end_line><content>def multiply(a, b):
    """乘法函数"""
    return a * b</content></replace_code>'''
    
    print(f"测试XML: {xml}")
    result = ai_tool_processor.process_response(xml)
    print(f"结果: {result['tool_result']}")
    print(f"显示: {result['display_text']}")
    
    # 显示修改后的文件内容
    with open("test_sample.py", "r", encoding="utf-8") as f:
        content = f.read()
    print("\n修改后的文件内容:")
    for i, line in enumerate(content.split('\n'), 1):
        print(f"{i:2d}: {line}")

def test_mode_permissions():
    """测试不同模式下的权限"""
    print("\n=== 测试模式权限 ===")
    
    modes = ["Ask", "mostly accepted", "sprint"]
    test_xml = '<insert_code><path>test_sample.py</path><line>1</line><content># 测试权限</content></insert_code>'
    
    for mode in modes:
        print(f"\n🔄 测试 {mode} 模式")
        mode_manager.current_mode = mode
        
        permission = mode_manager.can_auto_execute('insert_code')
        print(f"权限检查: {permission}")
        
        if permission is False:
            print("❌ 该模式禁止代码编辑操作")
        elif permission == "confirm":
            print("❓ 该模式需要用户确认代码编辑操作")
        else:
            print("✅ 该模式允许自动执行代码编辑操作")

def cleanup():
    """清理测试文件"""
    import os
    try:
        os.remove("test_sample.py")
        print("\n🗑️  清理测试文件")
    except:
        pass

if __name__ == "__main__":
    create_test_file()
    test_insert_code()
    test_replace_code()
    test_mode_permissions()
    cleanup()
