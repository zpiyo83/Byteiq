#!/usr/bin/env python3
"""
测试清理后的UI效果
"""

from src.modes import mode_manager
from src.commands import show_help
from src.todo_renderer import get_todo_renderer
from src.todo_manager import todo_manager

def test_clean_ui():
    """测试清理后的UI"""
    print("=== 测试清理后的UI效果 ===\n")
    
    # 测试模式切换通知
    print("1. 模式切换通知:")
    mode_manager.show_mode_switch_notification()
    
    print("\n" + "="*60)
    
    # 测试帮助信息
    print("\n2. 帮助信息:")
    show_help()
    
    print("\n" + "="*60)
    
    # 测试TODO渲染
    print("\n3. TODO列表渲染:")
    todo_renderer = get_todo_renderer(todo_manager)
    
    # 添加一个测试任务
    todo_id = todo_manager.add_todo("测试任务", "这是一个测试任务", "high")
    todo_manager.update_todo(todo_id, progress=50)
    
    # 渲染TODO列表
    todo_output = todo_renderer.render_todo_list()
    print(todo_output)
    
    # 清理测试任务
    todo_manager.delete_todo(todo_id)
    
    print("\n" + "="*60)
    
    # 测试权限显示
    print("\n4. 权限信息显示:")
    for mode in ["Ask", "mostly accepted", "sprint"]:
        mode_manager.current_mode = mode
        permissions = mode_manager.get_mode_permissions()
        print(f"\n{mode} 模式:")
        if "allowed" in permissions:
            print(f"  允许: {' | '.join(permissions['allowed'])}")
        if "confirm" in permissions:
            print(f"  需确认: {' | '.join(permissions['confirm'])}")
        if "forbidden" in permissions:
            print(f"  禁止: {' | '.join(permissions['forbidden'])}")

def show_before_after():
    """显示清理前后对比"""
    print("\n=== 清理前后对比 ===")
    
    print("\n清理前的样式:")
    print("🤖 AI助手正在处理您的请求...")
    print("📋 执行结果: 命令执行成功")
    print("🔄 模式已切换: sprint")
    print("💡 使用提示: 直接输入您的需求")
    print("📖 读取文件 - AI可以读取项目文件")
    print("✏️ 写入文件 - AI可以创建和修改文件")
    
    print("\n清理后的样式:")
    print("AI助手正在处理您的请求...")
    print("执行结果: 命令执行成功")
    print("模式已切换: sprint")
    print("使用提示: 直接输入您的需求")
    print("读取文件 - AI可以读取项目文件")
    print("写入文件 - AI可以创建和修改文件")
    
    print("\n✅ 清理效果:")
    print("- 移除了不必要的装饰性emoji")
    print("- 保留了功能性图标（状态、优先级等）")
    print("- 界面更加简洁清爽")
    print("- 提升了可读性和专业感")

if __name__ == "__main__":
    test_clean_ui()
    show_before_after()
