#!/usr/bin/env python3
"""
测试优化后的系统提示词
"""

from src.ai_client import ai_client

def test_prompt_structure():
    """测试提示词结构"""
    print("=== 测试优化后的系统提示词 ===\n")
    
    prompt = ai_client.get_system_prompt()
    
    # 检查关键部分是否存在
    key_sections = [
        "🛠️ 可用工具及使用场景",
        "📖 文件读取工具",
        "✏️ 文件创建和写入工具", 
        "🎯 精确代码编辑工具",
        "⚡ 系统命令工具",
        "📋 TODO任务管理工具",
        "🎯 工具选择决策指南",
        "📋 标准工作流程",
        "⚠️ 重要规则",
        "💡 最佳实践"
    ]
    
    print("检查提示词结构:")
    for section in key_sections:
        if section in prompt:
            print(f"✅ {section}")
        else:
            print(f"❌ {section}")
    
    print(f"\n提示词总长度: {len(prompt)} 字符")
    print(f"提示词行数: {len(prompt.splitlines())} 行")

def show_prompt_improvements():
    """显示提示词改进点"""
    print("\n=== 提示词优化改进 ===\n")
    
    print("🔧 主要改进:")
    print("1. 📖 明确的使用场景说明")
    print("   - 每个工具都有详细的使用场景描述")
    print("   - 清楚说明何时使用哪个工具")
    
    print("\n2. 🎯 决策指南")
    print("   - 文件操作决策树")
    print("   - 任务管理决策流程")
    print("   - 系统命令使用场景")
    
    print("\n3. 📋 标准工作流程")
    print("   - 新项目开发流程")
    print("   - 代码修改流程")
    print("   - 问题排查流程")
    
    print("\n4. ⚠️ 重要规则强化")
    print("   - XML格式要求")
    print("   - Windows系统命令")
    print("   - 先读后写原则")
    
    print("\n5. 💡 最佳实践指导")
    print("   - 优先使用精确编辑")
    print("   - 测试驱动开发")
    print("   - 任务进度管理")

def show_decision_examples():
    """显示决策示例"""
    print("\n=== 工具选择决策示例 ===\n")
    
    scenarios = [
        {
            "用户请求": "创建一个计算器程序",
            "AI应该": "1. add_todo记录任务 → 2. dir查看目录 → 3. create_file创建calculator.py → 4. 编写代码 → 5. execute_command测试 → 6. task_complete总结"
        },
        {
            "用户请求": "修改现有函数的一行代码",
            "AI应该": "1. read_file查看现有代码 → 2. 定位需要修改的行 → 3. replace_code替换特定行 → 4. 测试验证"
        },
        {
            "用户请求": "在文件开头添加import语句",
            "AI应该": "1. read_file查看现有代码 → 2. insert_code在第1行插入import → 3. 验证语法"
        },
        {
            "用户请求": "查看当前项目有什么文件",
            "AI应该": "1. execute_command使用dir命令 → 2. 分析项目结构 → 3. 向用户说明"
        },
        {
            "用户请求": "显示我的任务进度",
            "AI应该": "1. show_todos显示任务列表 → 2. 分析进度状态 → 3. 向用户汇报"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. 场景: {scenario['用户请求']}")
        print(f"   AI决策: {scenario['AI应该']}")
        print()

def show_before_after():
    """显示优化前后对比"""
    print("=== 优化前后对比 ===\n")
    
    print("优化前的问题:")
    print("❌ 工具说明过于简单")
    print("❌ 缺少使用场景指导")
    print("❌ 没有决策流程")
    print("❌ AI不知道何时用哪个工具")
    print("❌ 容易选择错误的工具")
    
    print("\n优化后的改进:")
    print("✅ 详细的使用场景说明")
    print("✅ 清晰的决策指南")
    print("✅ 标准工作流程")
    print("✅ 最佳实践指导")
    print("✅ AI能智能选择合适工具")
    
    print("\n预期效果:")
    print("🎯 AI更准确地选择工具")
    print("🎯 减少不必要的工具调用")
    print("🎯 提高工作效率")
    print("🎯 更好的用户体验")

if __name__ == "__main__":
    test_prompt_structure()
    show_prompt_improvements()
    show_decision_examples()
    show_before_after()
