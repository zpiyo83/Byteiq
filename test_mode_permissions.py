#!/usr/bin/env python3
"""
测试模式权限功能
"""

from src.modes import mode_manager
from src.ai_tools import ai_tool_processor

def test_mode_permissions():
    """测试不同模式的权限控制"""
    print("=== 测试模式权限功能 ===\n")
    
    # 测试所有模式
    modes = ["Ask", "mostly accepted", "sprint"]
    
    for mode in modes:
        print(f"🔄 切换到 {mode} 模式")
        mode_manager.current_mode = mode
        
        # 显示模式信息
        description = mode_manager.get_mode_description()
        permissions = mode_manager.get_mode_permissions()
        
        print(f"📋 描述: {description}")
        
        if "allowed" in permissions:
            print(f"✅ 允许: {' | '.join(permissions['allowed'])}")
        if "confirm" in permissions:
            print(f"❓ 需确认: {' | '.join(permissions['confirm'])}")
        if "forbidden" in permissions:
            print(f"❌ 禁止: {' | '.join(permissions['forbidden'])}")
        
        # 测试权限检查
        test_tools = ['read_file', 'write_file', 'create_file', 'execute_command', 'add_todo', 'show_todos']
        
        print(f"🧪 权限测试:")
        for tool in test_tools:
            permission = mode_manager.can_auto_execute(tool)
            if permission is True:
                status = "✅ 自动执行"
            elif permission == "confirm":
                status = "❓ 需要确认"
            elif permission is False:
                status = "❌ 禁止执行"
            else:
                status = "❔ 未知"
            
            print(f"   {tool}: {status}")
        
        print("-" * 60)

def test_xml_processing():
    """测试XML处理在不同模式下的行为"""
    print("\n=== 测试XML处理 ===\n")
    
    test_xmls = [
        '<read_file><path>README.md</path></read_file>',
        '<write_file><path>test.txt</path><content>Hello World</content></write_file>',
        '<execute_command><command>echo "test"</command></execute_command>',
        '<show_todos></show_todos>'
    ]
    
    modes = ["Ask", "mostly accepted", "sprint"]
    
    for mode in modes:
        print(f"🔄 测试 {mode} 模式")
        mode_manager.current_mode = mode
        
        for xml in test_xmls:
            print(f"\n测试XML: {xml}")
            # 注意：这里只是模拟，实际的用户确认会被跳过
            result = ai_tool_processor.process_response(xml)
            print(f"结果: {result['display_text']}")
        
        print("-" * 50)

def show_mode_switch_demo():
    """演示模式切换"""
    print("\n=== 模式切换演示 ===\n")
    
    print("当前模式:", mode_manager.get_current_mode())
    
    for i in range(4):  # 切换一圈
        mode_manager.show_mode_switch_notification()
        print(f"第 {i+1} 次切换完成\n")

if __name__ == "__main__":
    test_mode_permissions()
    test_xml_processing()
    show_mode_switch_demo()
