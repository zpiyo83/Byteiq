#!/usr/bin/env python3
"""
测试 /init 命令处理
"""

import sys
import os
sys.path.insert(0, '.')

def test_init_command():
    """测试 /init 命令是否被正确处理"""
    print("=== 测试 /init 命令处理 ===")
    
    # 测试 byteiq.py 中的 handle_special_commands
    try:
        from byteiq import handle_special_commands
        
        print("\n1. 测试 handle_special_commands('/init'):")
        result1 = handle_special_commands('/init')
        print(f"   结果: {result1}")
        
        print("\n2. 测试 handle_special_commands('/init start'):")
        result2 = handle_special_commands('/init start')
        print(f"   结果: {result2}")
        
        if result1 and result2:
            print("\n✅ byteiq.py 中的命令处理正常")
        else:
            print("\n❌ byteiq.py 中的命令处理有问题")
            
    except Exception as e:
        print(f"\n❌ byteiq.py 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试 command_processor.py 中的处理
    try:
        from src.command_processor import handle_init_command
        
        print("\n3. 测试 handle_init_command(['init']):")
        handle_init_command(['init'])
        
        print("\n4. 测试 handle_init_command(['init', 'start']):")
        handle_init_command(['init', 'start'])
        
        print("\n✅ command_processor.py 中的命令处理正常")
        
    except Exception as e:
        print(f"\n❌ command_processor.py 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_init_command()
