#!/usr/bin/env python3
"""
Forge AI Code 安装配置 - 最新版本
"""

from setuptools import setup, find_packages

# 读取版本号
def get_version():
    with open("forge_ai_code/__init__.py", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.2.0"

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    long_description = "Forge AI Code - 智能AI编程助手"

setup(
    name="forge-ai-code",
    version=get_version(),
    author="Forge AI Team",
    author_email="support@forgeai.dev",
    description="智能AI编程助手 - 通过自然语言对话进行编程开发",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/forge-ai/forge-ai-code",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        'colorama>=0.4.4',
        'requests>=2.25.1'
    ],
    entry_points={
        "console_scripts": [
            "forge-ai-code=forge_ai_code.main:main",
            "fac=forge_ai_code.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
