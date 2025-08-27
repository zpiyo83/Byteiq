#!/usr/bin/env python3
"""
测试ByteIQ启动性能
"""

import time
import sys
import os

def test_startup_performance():
    """测试启动性能"""
    print("测试ByteIQ启动性能...")
    
    # 测试导入时间
    start_time = time.time()
    try:
        import byteiq
        import_time = time.time() - start_time
        print(f"✓ 模块导入时间: {import_time:.3f}秒")
    except Exception as e:
        print(f"✗ 模块导入失败: {e}")
        return
    
    # 测试各个组件的导入时间
    components = [
        ('colorama', 'colorama'),
        ('配置管理', 'src.config'),
        ('UI组件', 'src.ui'),
        ('延迟加载器', 'src.lazy_loader'),
    ]
    
    print("\n组件导入时间测试:")
    for name, module in components:
        start = time.time()
        try:
            __import__(module)
            elapsed = time.time() - start
            print(f"  {name}: {elapsed:.3f}秒")
        except Exception as e:
            print(f"  {name}: 导入失败 - {e}")
    
    # 测试延迟加载的组件
    print("\n延迟加载组件测试:")
    lazy_components = [
        ('AI客户端', 'src.ai_client'),
        ('AI工具', 'src.ai_tools'),
        ('MCP配置', 'src.mcp_config'),
        ('MCP客户端', 'src.mcp_client'),
        ('输入处理器', 'src.input_handler'),
        ('键盘处理器', 'src.keyboard_handler'),
    ]
    
    for name, module in lazy_components:
        start = time.time()
        try:
            __import__(module)
            elapsed = time.time() - start
            print(f"  {name}: {elapsed:.3f}秒")
        except Exception as e:
            print(f"  {name}: 导入失败 - {e}")

if __name__ == "__main__":
    test_startup_performance()
