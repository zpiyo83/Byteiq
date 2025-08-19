#!/usr/bin/env python3
"""
测试TODO功能
"""

from src.todo_manager import todo_manager
from src.todo_renderer import get_todo_renderer
from src.ai_tools import ai_tool_processor

def test_todo_basic():
    """测试基本TODO功能"""
    print("=== 测试基本TODO功能 ===")
    
    # 清空现有数据
    todo_manager.todos.clear()
    
    # 添加测试任务
    task1_id = todo_manager.add_todo("学习Python", "学习Python基础语法", "high")
    task2_id = todo_manager.add_todo("写代码", "完成项目开发", "medium")
    task3_id = todo_manager.add_todo("测试功能", "测试所有功能模块", "low")
    
    print(f"添加了3个任务:")
    print(f"- 任务1 ID: {task1_id[:8]}")
    print(f"- 任务2 ID: {task2_id[:8]}")
    print(f"- 任务3 ID: {task3_id[:8]}")
    
    # 更新任务状态
    todo_manager.update_todo(task1_id, status="in_progress", progress=50)
    todo_manager.update_todo(task2_id, status="completed", progress=100)
    
    print("\n更新了任务状态")
    
    # 显示任务列表
    renderer = get_todo_renderer(todo_manager)
    print(renderer.render_todo_list())
    
    # 显示统计
    stats = todo_manager.get_stats()
    print(f"\n统计信息: {stats}")

def test_todo_xml():
    """测试TODO的XML工具调用"""
    print("\n=== 测试TODO XML工具调用 ===")
    
    # 测试添加任务
    xml_add = '<add_todo><title>AI测试任务</title><description>通过AI添加的测试任务</description><priority>urgent</priority></add_todo>'
    result = ai_tool_processor.process_response(xml_add)
    print(f"添加任务结果: {result}")
    
    # 测试显示任务
    xml_show = '<show_todos></show_todos>'
    result = ai_tool_processor.process_response(xml_show)
    print(f"显示任务结果: {result}")
    
    # 获取第一个任务ID进行更新测试
    if todo_manager.todos:
        first_todo_id = list(todo_manager.todos.keys())[0]
        xml_update = f'<update_todo><id>{first_todo_id[:8]}</id><status>completed</status><progress>100</progress></update_todo>'
        result = ai_tool_processor.process_response(xml_update)
        print(f"更新任务结果: {result}")

def test_todo_subtasks():
    """测试子任务功能"""
    print("\n=== 测试子任务功能 ===")
    
    # 添加主任务
    main_task_id = todo_manager.add_todo("开发网站", "完整的网站开发项目", "high")
    
    # 添加子任务
    sub1_id = todo_manager.add_todo("设计界面", "设计用户界面", "medium", main_task_id)
    sub2_id = todo_manager.add_todo("后端开发", "开发后端API", "high", main_task_id)
    sub3_id = todo_manager.add_todo("测试部署", "测试和部署", "medium", main_task_id)
    
    print(f"添加了主任务和3个子任务")
    
    # 更新子任务状态
    todo_manager.update_todo(sub1_id, status="completed", progress=100)
    todo_manager.update_todo(sub2_id, status="in_progress", progress=60)
    
    # 显示任务列表
    renderer = get_todo_renderer(todo_manager)
    print(renderer.render_todo_list())

def test_todo_renderer():
    """测试TODO渲染功能"""
    print("\n=== 测试TODO渲染功能 ===")
    
    renderer = get_todo_renderer(todo_manager)
    
    # 测试摘要渲染
    print("任务摘要:")
    print(renderer.render_todo_summary())
    
    # 测试详情渲染
    if todo_manager.todos:
        first_todo_id = list(todo_manager.todos.keys())[0]
        print(f"\n任务详情:")
        print(renderer.render_todo_item_detail(first_todo_id))

if __name__ == "__main__":
    test_todo_basic()
    test_todo_xml()
    test_todo_subtasks()
    test_todo_renderer()
    
    print(f"\n=== 测试完成 ===")
    print(f"总任务数: {len(todo_manager.todos)}")
