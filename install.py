#!/usr/bin/env python3
"""
Forge AI Code 安装脚本
将 FORGEAI 命令添加到系统PATH中，使其可以在任意位置调用
"""

import os
import sys
import shutil
import platform
from pathlib import Path

def create_batch_file():
    """为Windows创建批处理文件"""
    batch_content = f'''@echo off
python "{os.path.abspath("forgeai.py")}" %*
'''
    
    batch_path = Path("forgeai.bat")
    with open(batch_path, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    return batch_path

def create_shell_script():
    """为Unix/Linux/Mac创建shell脚本"""
    script_content = f'''#!/bin/bash
python3 "{os.path.abspath("forgeai.py")}" "$@"
'''
    
    script_path = Path("forgeai")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 添加执行权限
    os.chmod(script_path, 0o755)
    
    return script_path

def install_windows():
    """Windows安装"""
    print("检测到Windows系统，正在安装...")

    # 尝试找到Python Scripts目录
    python_scripts = None

    # 方法1: 检查当前Python安装的Scripts目录
    try:
        import sys
        python_dir = Path(sys.executable).parent
        scripts_dir = python_dir / "Scripts"
        if scripts_dir.exists():
            python_scripts = scripts_dir
    except:
        pass

    # 方法2: 如果没找到，使用用户bin目录
    if not python_scripts:
        python_scripts = Path.home() / "bin"
        python_scripts.mkdir(exist_ok=True)

    # 获取当前脚本的绝对路径
    script_path = os.path.abspath("forgeai.py")

    # 尝试获取短路径名以避免中文字符问题
    try:
        import subprocess
        result = subprocess.run(['powershell', '-Command',
                               f'(New-Object -ComObject Scripting.FileSystemObject).GetFile("{script_path}").ShortPath'],
                               capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            script_path = result.stdout.strip()
    except:
        pass  # 如果获取短路径失败，使用原路径

    # 创建批处理文件内容
    batch_content = f'''@echo off
python "{script_path}" %*
'''

    # 直接在目标目录创建批处理文件，使用ANSI编码避免BOM问题
    target_path = python_scripts / "forgeai.bat"
    with open(target_path, 'w', encoding='gbk') as f:
        f.write(batch_content)

    print(f"✅ 已安装到: {target_path}")

    if "Scripts" in str(python_scripts):
        print("✅ 已安装到Python Scripts目录，应该已经在PATH中")
    else:
        print(f"📁 请确保 {python_scripts} 在您的PATH环境变量中")
        print("\n🔧 如何添加到PATH:")
        print("1. 按 Win+R，输入 sysdm.cpl")
        print("2. 点击 '环境变量'")
        print("3. 在用户变量中找到 'Path'，点击编辑")
        print(f"4. 添加新路径: {python_scripts}")
        print("5. 重启命令提示符")

def install_unix():
    """Unix/Linux/Mac安装"""
    print("检测到Unix/Linux/Mac系统，正在安装...")
    
    # 创建shell脚本
    script_path = create_shell_script()
    
    # 尝试安装到用户的本地bin目录
    user_bin = Path.home() / ".local" / "bin"
    user_bin.mkdir(parents=True, exist_ok=True)
    
    target_path = user_bin / "forgeai"
    shutil.copy2(script_path, target_path)
    os.chmod(target_path, 0o755)
    
    print(f"✅ 已安装到: {target_path}")
    print(f"📁 请确保 {user_bin} 在您的PATH环境变量中")
    print("\n🔧 如何添加到PATH:")
    print(f"将以下行添加到您的 ~/.bashrc 或 ~/.zshrc 文件:")
    print(f'export PATH="$PATH:{user_bin}"')
    print("然后运行: source ~/.bashrc (或 source ~/.zshrc)")
    
    # 清理临时文件
    script_path.unlink()

def check_dependencies():
    """检查依赖"""
    try:
        import colorama
        print("✅ colorama 已安装")
        return True
    except ImportError:
        print("❌ 缺少依赖: colorama")
        print("请运行: pip install colorama")
        return False

def main():
    """主安装函数"""
    print("🚀 Forge AI Code 安装程序")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查forgeai.py是否存在
    if not Path("forgeai.py").exists():
        print("❌ 错误: forgeai.py 文件不存在")
        print("请确保在包含 forgeai.py 的目录中运行此安装脚本")
        return
    
    # 根据操作系统选择安装方式
    system = platform.system().lower()
    
    if system == "windows":
        install_windows()
    else:
        install_unix()
    
    print("\n🎉 安装完成！")
    print("现在您可以在任意位置的命令行中输入 'forgeai' 来启动程序")
    print("\n💡 提示: 如果命令不可用，请重启终端或检查PATH设置")

if __name__ == "__main__":
    main()
