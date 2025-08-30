#!/usr/bin/env python3
"""
调试 /init 命令处理问题
"""

def test_command_matching():
    """测试命令匹配逻辑"""
    test_inputs = [
        "/init",
        "/init start", 
        "/init status",
        "/init help",
        "init start",  # 不带斜杠
        " /init start "  # 带空格
    ]
    
    for user_input in test_inputs:
        print(f"\n测试输入: '{user_input}'")
        
        # 模拟 handle_special_commands 中的处理逻辑
        cleaned_input = user_input.strip()
        print(f"清理后: '{cleaned_input}'")
        
        if cleaned_input.lower().startswith('/init'):
            print("✅ 匹配 /init 命令")
            command_parts = cleaned_input.split()
            print(f"命令部分: {command_parts}")
        else:
            print("❌ 不匹配 /init 命令")

if __name__ == "__main__":
    test_command_matching()
