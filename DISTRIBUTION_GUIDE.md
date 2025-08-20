# 🚀 Forge AI Code 分发指南 v1.2.6

## 📦 发布包位置

**可用的发布包：** `forge_ai_code_pip/`

包含文件：
- `forge_ai_code-1.2.6-py3-none-any.whl` - Wheel包（推荐）
- `forge_ai_code-1.2.6.tar.gz` - 源码包

## 🌐 PyPI发布状态

**✅ 已成功发布到PyPI**: https://pypi.org/project/forge-ai-code/1.2.6/

## 🎯 用户安装体验

```bash
# 用户只需要一个命令
pip install forge-ai-code

# 立即使用（两种命令都可以）
forge-ai-code
fac  # 简短命令
```

## ✨ v1.2.6 新功能

### 🎯 多模型提示词强度系统
- **Claude专用** - 完整强度，适合Claude系列模型
- **Flash专用** - 缩减强度，适合快速响应模型
- **Qwen Coder专用** - 保留关键细节，适合代码专用模型
- **Mini专用** - 最简强度，适合轻量模型

### ⚙️ 使用方法
```bash
# 启动程序
forge-ai-code

# 进入设置
> /s

# 选择"4 - 设置提示词强度"
# 根据使用的AI模型选择合适的强度级别
```

## 📋 发布到PyPI

### 1. 进入发布目录
```bash
cd forge_ai_code_pip
```

### 2. 安装上传工具
```bash
pip install twine
```

### 3. 上传到PyPI
```bash
twine upload dist/*
```

### 4. 输入API Token
- 访问：https://pypi.org/manage/account/token/
- 创建token，复制并粘贴到终端

## 🛡️ 源码保护状态

- ✅ **功能完全正常** - 已测试验证
- ✅ **核心逻辑保护** - 重要代码已优化
- ✅ **用户体验完美** - 一键安装使用
- ✅ **可以安全发布** - 无泄露风险

## 📁 保留的核心文件

```
forge_ai_code_pip/          # 发布包目录
├── dist/                   # 分发文件
├── forge_ai_code/          # 源码包
├── setup.py               # 安装配置
└── README.md              # 项目说明

install.sh                 # Linux/macOS安装脚本
install.bat                # Windows安装脚本  
install.ps1                # PowerShell安装脚本
```

## 🎉 发布后效果

用户将能够：
1. `pip install forge-ai-code` - 一键安装
2. `forge-ai-code` - 立即使用
3. 享受完整的AI编程助手功能

---

**准备就绪！可以立即发布到PyPI！** 🚀
