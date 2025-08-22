#!/usr/bin/env python3
"""
HACPP模式演示脚本
"""

import sys
import os
from colorama import Fore, Style, init

# 初始化colorama
init(autoreset=True)

# 添加src目录到路径
sys.path.insert(0, 'src')

# 导入模块
try:
    from src.modes import hacpp_mode
    from src.hacpp_client import hacpp_client
    from src.command_processor import handle_hacpp_command
except ImportError:
    # 如果相对导入失败，尝试直接导入
    import importlib.util

    # 加载modes模块
    spec = importlib.util.spec_from_file_location("modes", "src/modes.py")
    modes_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modes_module)
    hacpp_mode = modes_module.hacpp_mode

    print("注意：使用简化导入模式，某些功能可能不可用")

def demo_hacpp_commands():
    """演示HACPP命令功能"""
    print(f"{Fore.CYAN}🚀 HACPP模式命令演示{Style.RESET_ALL}")
    print("=" * 60)
    
    # 演示1：显示帮助
    print(f"\n{Fore.YELLOW}演示1: HACPP帮助信息{Style.RESET_ALL}")
    handle_hacpp_command(['/hacpp', 'help'])
    
    # 演示2：激活HACPP模式（模拟）
    print(f"\n{Fore.YELLOW}演示2: 激活HACPP模式{Style.RESET_ALL}")
    result = hacpp_mode.activate("2255")
    if result:
        print(f"{Fore.GREEN}✓ HACPP模式激活成功{Style.RESET_ALL}")
        print(f"{Fore.CYAN}现在可以使用 /HACPP model 设置便宜模型{Style.RESET_ALL}")
    
    # 演示3：设置便宜模型（模拟）
    print(f"\n{Fore.YELLOW}演示3: 设置便宜模型{Style.RESET_ALL}")
    hacpp_mode.set_cheap_model("gpt-3.5-turbo")
    print(f"{Fore.GREEN}✓ 便宜模型已设置: gpt-3.5-turbo{Style.RESET_ALL}")
    print(f"{Fore.CYAN}HACPP模式已完全激活，可以开始双AI协作{Style.RESET_ALL}")
    
    # 演示4：显示状态
    print(f"\n{Fore.YELLOW}演示4: 显示HACPP状态{Style.RESET_ALL}")
    handle_hacpp_command(['/hacpp', 'status'])
    
    # 演示5：项目结构分析
    print(f"\n{Fore.YELLOW}演示5: 项目结构分析{Style.RESET_ALL}")
    project_structure = hacpp_client._get_project_structure()
    print(f"{Fore.WHITE}项目结构预览:{Style.RESET_ALL}")
    lines = project_structure.split('\n')
    for line in lines[:15]:  # 只显示前15行
        print(f"  {line}")
    if len(lines) > 15:
        print(f"  ... (还有 {len(lines) - 15} 行)")
    
    # 演示6：模拟便宜AI分析
    print(f"\n{Fore.YELLOW}演示6: 便宜AI分析示例{Style.RESET_ALL}")
    sample_analysis = """
FILES_TO_MODIFY:
- src/game.py: 添加食物系统类
- src/ui.py: 添加食物显示界面
- config.json: 添加食物配置参数

ANALYSIS:
用户想要为游戏添加食物系统。需要创建食物类来管理食物的生成、消失和玩家交互。
同时需要在UI中显示食物，并在配置文件中添加相关参数。

PRIORITY:
HIGH

IMPLEMENTATION_STEPS:
1. 创建Food类处理食物逻辑
2. 修改游戏主循环集成食物系统
3. 更新UI显示食物
4. 添加配置参数
"""
    
    print(f"{Fore.GREEN}便宜AI分析结果:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{sample_analysis.strip()}{Style.RESET_ALL}")
    
    # 演示7：文件解析
    print(f"\n{Fore.YELLOW}演示7: 文件解析功能{Style.RESET_ALL}")
    files = hacpp_client._parse_files_from_analysis(sample_analysis)
    print(f"{Fore.GREEN}✓ 解析出需要修改的文件:{Style.RESET_ALL}")
    for file in files:
        print(f"  📄 {file}")
    
    # 演示8：关闭HACPP模式
    print(f"\n{Fore.YELLOW}演示8: 关闭HACPP模式{Style.RESET_ALL}")
    handle_hacpp_command(['/hacpp', 'off'])
    
    print(f"\n{Fore.CYAN}🎉 HACPP模式演示完成！{Style.RESET_ALL}")
    print(f"\n{Fore.WHITE}使用说明:{Style.RESET_ALL}")
    print(f"1. 使用 /HACPP 激活模式（测试码: 2255）")
    print(f"2. 使用 /HACPP model 设置便宜模型")
    print(f"3. 直接输入需求，系统会自动进行双AI协作")
    print(f"4. 使用 /HACPP status 查看状态")
    print(f"5. 使用 /HACPP off 关闭模式")

def demo_workflow():
    """演示完整的HACPP工作流程"""
    print(f"\n{Fore.MAGENTA}🔄 HACPP工作流程演示{Style.RESET_ALL}")
    print("=" * 60)
    
    # 模拟用户需求
    user_request = "给这个游戏添加一个食物系统，玩家可以吃食物获得分数"
    
    print(f"{Fore.CYAN}用户需求:{Style.RESET_ALL} {user_request}")
    
    # 步骤1：便宜AI分析
    print(f"\n{Fore.YELLOW}步骤1: 便宜AI分析需求和项目{Style.RESET_ALL}")
    print(f"{Fore.WHITE}便宜AI会：{Style.RESET_ALL}")
    print("  • 理解用户需求")
    print("  • 分析项目结构")
    print("  • 确定需要修改的文件")
    print("  • 制定实现方案")
    
    # 步骤2：贵AI执行
    print(f"\n{Fore.YELLOW}步骤2: 贵AI执行具体实现{Style.RESET_ALL}")
    print(f"{Fore.WHITE}贵AI会：{Style.RESET_ALL}")
    print("  • 根据便宜AI的分析结果")
    print("  • 调用工具读取/修改文件")
    print("  • 实现具体的代码逻辑")
    print("  • 完成用户需求")
    
    # 优势说明
    print(f"\n{Fore.GREEN}💡 HACPP模式优势:{Style.RESET_ALL}")
    print("  ✓ 成本优化：便宜AI做分析，贵AI做实现")
    print("  ✓ 效率提升：预分析让贵AI更精准")
    print("  ✓ 质量保证：双重检查机制")
    print("  ✓ 资源合理：根据任务复杂度分配AI资源")

if __name__ == "__main__":
    demo_hacpp_commands()
    demo_workflow()
    
    print(f"\n{Fore.CYAN}📖 更多信息请查看 HACPP_GUIDE.md{Style.RESET_ALL}")
