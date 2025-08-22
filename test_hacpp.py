#!/usr/bin/env python3
"""
HACPP模式测试脚本
"""

from src.modes import hacpp_mode
from src.hacpp_client import hacpp_client
from colorama import Fore, Style, init

# 初始化colorama
init(autoreset=True)

def test_hacpp_mode():
    """测试HACPP模式功能"""
    print(f"{Fore.CYAN}🧪 HACPP模式测试{Style.RESET_ALL}")
    print("=" * 50)
    
    # 测试1：激活HACPP模式
    print(f"\n{Fore.YELLOW}测试1: 激活HACPP模式{Style.RESET_ALL}")
    result = hacpp_mode.activate("2255")
    if result:
        print(f"{Fore.GREEN}✓ HACPP模式激活成功{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ HACPP模式激活失败{Style.RESET_ALL}")
        return
    
    # 测试2：设置便宜模型
    print(f"\n{Fore.YELLOW}测试2: 设置便宜模型{Style.RESET_ALL}")
    hacpp_mode.set_cheap_model("gpt-3.5-turbo")
    print(f"{Fore.GREEN}✓ 便宜模型设置为: {hacpp_mode.cheap_model}{Style.RESET_ALL}")
    
    # 测试3：检查HACPP模式状态
    print(f"\n{Fore.YELLOW}测试3: 检查HACPP模式状态{Style.RESET_ALL}")
    is_active = hacpp_mode.is_hacpp_active()
    if is_active:
        print(f"{Fore.GREEN}✓ HACPP模式完全激活{Style.RESET_ALL}")
        print(f"  便宜模型: {hacpp_mode.cheap_model}")
        print(f"  认证状态: {hacpp_mode.authenticated}")
    else:
        print(f"{Fore.RED}✗ HACPP模式未完全激活{Style.RESET_ALL}")
    
    # 测试4：项目结构分析
    print(f"\n{Fore.YELLOW}测试4: 项目结构分析{Style.RESET_ALL}")
    project_structure = hacpp_client._get_project_structure()
    print(f"{Fore.WHITE}项目结构:{Style.RESET_ALL}")
    print(project_structure[:500] + "..." if len(project_structure) > 500 else project_structure)
    
    # 测试5：文件解析功能
    print(f"\n{Fore.YELLOW}测试5: 文件解析功能{Style.RESET_ALL}")
    test_analysis = """
FILES_TO_MODIFY:
- src/test.py: 添加新功能
- config.json: 更新配置

ANALYSIS:
这是一个测试分析结果。

PRIORITY:
HIGH
"""
    files = hacpp_client._parse_files_from_analysis(test_analysis)
    print(f"{Fore.GREEN}✓ 解析出的文件: {files}{Style.RESET_ALL}")
    
    # 测试6：关闭HACPP模式
    print(f"\n{Fore.YELLOW}测试6: 关闭HACPP模式{Style.RESET_ALL}")
    hacpp_mode.deactivate()
    is_active_after = hacpp_mode.is_hacpp_active()
    if not is_active_after:
        print(f"{Fore.GREEN}✓ HACPP模式已成功关闭{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ HACPP模式关闭失败{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}🎉 HACPP模式测试完成！{Style.RESET_ALL}")

if __name__ == "__main__":
    test_hacpp_mode()
