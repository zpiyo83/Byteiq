#!/usr/bin/env python3
"""
Forge AI Code 打包脚本
创建可发布的pip包
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_package():
    """创建发布包"""
    print("🔧 创建发布包...")
    
    # 创建包目录
    package_root = Path("forge_ai_code_pip")
    if package_root.exists():
        shutil.rmtree(package_root)
    
    package_root.mkdir()
    package_dir = package_root / "forge_ai_code"
    package_dir.mkdir()
    
    # 复制源文件
    if Path("main.py").exists():
        shutil.copy2("main.py", package_dir / "main.py")
    
    if Path("src").exists():
        for item in Path("src").iterdir():
            if item.is_file() and item.suffix == ".py":
                shutil.copy2(item, package_dir / item.name)
    
    # 创建__init__.py
    init_content = '''"""Forge AI Code - 智能AI编程助手"""
__version__ = "1.1.0"
from .main import main
__all__ = ["main"]
'''
    (package_dir / "__init__.py").write_text(init_content, encoding='utf-8')
    
    # 修复导入语句
    fix_imports(package_dir)
    
    # 创建配置文件
    create_setup_files(package_root)
    
    # 构建包
    build_package(package_root)
    
    print("✅ 发布包创建完成！")
    print(f"📦 位置: {package_root}")
    print("🚀 可以发布: cd forge_ai_code_pip && twine upload dist/*")

def fix_imports(package_dir):
    """修复导入语句"""
    import re
    
    for py_file in package_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        content = py_file.read_text(encoding='utf-8')
        content = re.sub(r'from src\.(\w+)', r'from .\1', content)
        content = re.sub(r'import src\.(\w+)', r'from . import \1', content)
        py_file.write_text(content, encoding='utf-8')

def create_setup_files(package_root):
    """创建setup.py"""
    setup_content = '''from setuptools import setup, find_packages

setup(
    name="forge-ai-code",
    version="1.1.0",
    author="Forge AI Team",
    author_email="support@forgeai.dev",
    description="智能AI编程助手",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['colorama>=0.4.4', 'requests>=2.25.1'],
    entry_points={
        "console_scripts": [
            "forge-ai-code=forge_ai_code.main:main",
            "fac=forge_ai_code.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
'''
    (package_root / "setup.py").write_text(setup_content, encoding='utf-8')
    
    # 复制README
    if Path("README.md").exists():
        shutil.copy2("README.md", package_root / "README.md")
    else:
        readme_content = """# Forge AI Code

智能AI编程助手

## 安装
```bash
pip install forge-ai-code
```

## 使用
```bash
forge-ai-code
```
"""
        (package_root / "README.md").write_text(readme_content, encoding='utf-8')

def build_package(package_root):
    """构建分发包"""
    original_cwd = os.getcwd()
    os.chdir(package_root)
    
    try:
        subprocess.run([sys.executable, "setup.py", "sdist", "bdist_wheel"], check=True)
        print("✅ 包构建成功")
    except subprocess.CalledProcessError:
        print("❌ 包构建失败")
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    create_package()
