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
    version="1.0.0",
    author="Forge AI Team",
    author_email="contact@forgeai.com",
    description="AI编程助手命令行工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/forgeai/forge-ai-code",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "forgeai=forgeai:main",
        ],
    },
    keywords="ai, coding, assistant, cli, programming",
    project_urls={
        "Bug Reports": "https://github.com/forgeai/forge-ai-code/issues",
        "Source": "https://github.com/forgeai/forge-ai-code",
    },
)
