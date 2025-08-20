#!/usr/bin/env python3
"""
Forge AI Code 安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="forge-ai-code",
    version="1.2.7",
    author="Forge AI Team",
    author_email="support@forgeai.dev",
    description="智能AI编程助手 - 支持多种AI模型的自适应提示词系统，新增删除文件工具和工具调用限制",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/forge-ai/forge-ai-code",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "forge-ai-code=forgeai:main",
            "fac=forgeai:main",  # 简短别名
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "*.md",
            "*.txt",
            "*.json",
        ],
    },
    keywords=[
        "ai", "artificial-intelligence", "coding", "programming",
        "assistant", "automation", "development", "cli", "tool"
    ],
    project_urls={
        "Bug Reports": "https://github.com/forge-ai/forge-ai-code/issues",
        "Source": "https://github.com/forge-ai/forge-ai-code",
        "Documentation": "https://forge-ai-code.readthedocs.io/",
        "Homepage": "https://forge-ai-code.dev/",
    },
    zip_safe=False,
)
