#!/usr/bin/env python3
"""
测试 /档 命令功能
验证超大型项目分析模式是否正常工作
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_doc_analyzer_import():
    """测试项目文档分析器模块导入"""
    try:
        from src.project_doc_analyzer import project_doc_analyzer
        print("✅ 项目文档分析器模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 项目文档分析器模块导入失败: {str(e)}")
        return False

def test_command_integration():
    """测试命令集成"""
    try:
        from src.commands import get_available_commands, get_command_descriptions
        
        commands = get_available_commands()
        descriptions = get_command_descriptions()
        
        if "/档" in commands:
            print("✅ /档 命令已添加到可用命令列表")
        else:
            print("❌ /档 命令未在可用命令列表中")
            return False
            
        if "/档" in descriptions:
            print(f"✅ /档 命令描述: {descriptions['/档']}")
        else:
            print("❌ /档 命令缺少描述")
            return False
            
        return True
    except Exception as e:
        print(f"❌ 命令集成测试失败: {str(e)}")
        return False

def test_command_processor():
    """测试命令处理器集成"""
    try:
        from src.command_processor import handle_doc_command
        print("✅ 命令处理器中的 handle_doc_command 函数可用")
        return True
    except Exception as e:
        print(f"❌ 命令处理器集成测试失败: {str(e)}")
        return False

def test_analyzer_basic_functions():
    """测试分析器基本功能"""
    try:
        from src.project_doc_analyzer import project_doc_analyzer
        
        # 测试获取状态
        status = project_doc_analyzer.get_status()
        print(f"✅ 获取状态成功: {status}")
        
        # 测试系统提示词生成
        prompt = project_doc_analyzer.get_analyzer_system_prompt()
        if "项目文档分析器" in prompt and "反对提示词指导原则" in prompt:
            print("✅ 系统提示词包含必要内容")
        else:
            print("❌ 系统提示词缺少关键内容")
            return False
            
        return True
    except Exception as e:
        print(f"❌ 分析器基本功能测试失败: {str(e)}")
        return False

def test_file_scanning():
    """测试文件扫描功能"""
    try:
        from src.project_doc_analyzer import ProjectDocAnalyzer
        
        # 创建临时分析器实例
        analyzer = ProjectDocAnalyzer()
        analyzer.current_project_path = os.getcwd()
        
        # 测试文件扫描
        analyzer._scan_project_files()
        
        if analyzer.total_files > 0:
            print(f"✅ 文件扫描成功，发现 {analyzer.total_files} 个文件")
            print(f"   前5个文件: {analyzer.analysis_order[:5]}")
        else:
            print("⚠️ 未发现可分析的文件")
            
        return True
    except Exception as e:
        print(f"❌ 文件扫描测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试 /档 命令功能...")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_doc_analyzer_import),
        ("命令集成", test_command_integration),
        ("命令处理器", test_command_processor),
        ("基本功能", test_analyzer_basic_functions),
        ("文件扫描", test_file_scanning)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 测试 {test_name}...")
        result = test_func()
        results.append(result)
        
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 所有测试通过！({passed}/{total})")
        print("\n✨ /档 命令功能已成功集成:")
        print("- ✅ 模块正确导入")
        print("- ✅ 命令系统集成完成")
        print("- ✅ 命令处理器配置正确")
        print("- ✅ 基本功能正常")
        print("- ✅ 文件扫描机制工作正常")
        
        print(f"\n🛠️ 使用方法:")
        print("1. 启动 ByteIQ")
        print("2. 输入 '/档' 查看帮助")
        print("3. 输入 '/档 start' 开始分析当前项目")
        print("4. 输入 '/档 status' 查看分析进度")
        print("5. 输入 '/档 stop' 停止分析")
        
        return True
    else:
        print(f"❌ {total - passed}/{total} 个测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
