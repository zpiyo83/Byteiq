#!/usr/bin/env python3
"""
简化的setup.py配置
"""

from setuptools import setup
import os

# 读取README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="byteiq",
    version="1.3.2",
    author="ByteIQ Team",
    author_email="support@byteiq.dev",
    description="智能AI编程助手 - 支持多种AI模型的自适应提示词系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/byteiq/byteiq",
    py_modules=["byteiq"],
    packages=["src"],
    package_data={
        "src": ["*.py", "*.json", "*.md", "*.txt"],
    },
    include_package_data=True,
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
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "byteiq=byteiq:main",
            "ByteIQ=byteiq:main",
        ],
    },
    zip_safe=False,
)
