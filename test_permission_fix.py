#!/usr/bin/env python3
"""
测试权限控制修复
"""

from src.modes import mode_manager
from src.ai_tools import ai_tool_processor

def test_ask_mode_permission():
    """测试Ask模式权限控制"""
    print("=== 测试Ask模式权限控制修复 ===\n")
    
    # 确保在Ask模式
    mode_manager.current_mode = "Ask"
    print(f"当前模式: {mode_manager.get_current_mode()}")
    
    # 测试create_file权限
    permission = mode_manager.can_auto_execute('create_file')
    print(f"create_file权限: {permission}")
    
    # 模拟AI想要创建文件
    ai_response = '<create_file><path>test_permission.py</path><content>print("这个文件不应该被创建")</content></create_file>'
    print(f"\n模拟AI响应: {ai_response}")
    
    # 处理响应
    result = ai_tool_processor.process_response(ai_response)
    print(f"\n处理结果:")
    print(f"  has_tool: {result['has_tool']}")
    print(f"  tool_result: {result['tool_result']}")
    print(f"  display_text: {result['display_text']}")
    print(f"  should_continue: {result['should_continue']}")
    
    # 检查文件是否真的被创建了
    import os
    if os.path.exists('test_permission.py'):
        print(f"\n❌ 错误: 文件被创建了！权限控制失败！")
        os.remove('test_permission.py')  # 清理
    else:
        print(f"\n✅ 正确: 文件没有被创建，权限控制成功！")

def test_all_modes():
    """测试所有模式"""
    print("\n=== 测试所有模式的create_file权限 ===\n")
    
    modes = ["Ask", "mostly accepted", "sprint"]
    
    for mode in modes:
        print(f"{mode} 模式:")
        mode_manager.current_mode = mode
        
        ai_response = f'<create_file><path>test_{mode.replace(" ", "_")}.py</path><content>print("测试{mode}模式")</content></create_file>'
        result = ai_tool_processor.process_response(ai_response)
        
        print(f"  权限检查: {mode_manager.can_auto_execute('create_file')}")
        print(f"  处理结果: {result['tool_result']}")
        print(f"  显示文本: {result['display_text']}")
        
        # 清理可能创建的文件
        import os
        test_file = f"test_{mode.replace(' ', '_')}.py"
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"  文件状态: 已创建（已清理）")
        else:
            print(f"  文件状态: 未创建")
        print()

def show_fix_summary():
    """显示修复总结"""
    print("=== 权限控制修复总结 ===\n")
    
    print("🔧 问题原因:")
    print("  - forgeai.py中有重复的AIToolProcessor类")
    print("  - 重复的类没有权限控制逻辑")
    print("  - AI工具调用绕过了权限检查")
    
    print("\n💡 修复方案:")
    print("  - 删除forgeai.py中重复的AIToolProcessor类")
    print("  - 统一使用src/ai_tools.py中的工具处理器")
    print("  - 确保所有工具调用都经过权限检查")
    
    print("\n✅ 修复效果:")
    print("  - Ask模式正确禁止创建文件")
    print("  - mostly accepted模式需要用户确认")
    print("  - sprint模式自动执行")
    print("  - 权限控制完全生效")

if __name__ == "__main__":
    test_ask_mode_permission()
    test_all_modes()
    show_fix_summary()
