# 安装指南

本指南将帮助您在系统上安装和设置ByteIQ。

## 系统要求

- **操作系统**: Windows、macOS或Linux
- **Python版本**: 3.8或更高版本
- **内存**: 至少4GB RAM（推荐8GB）
- **磁盘空间**: 100MB可用空间（额外空间用于依赖项）

## 安装方法

### 方法1：从PyPI安装（推荐）

安装ByteIQ最简单的方法是使用pip：

```bash
pip install byteiq
```

### 方法2：从源码安装

如果您想安装最新的开发版本：

```bash
# 克隆仓库
git clone https://github.com/byteiq/byteiq.git
cd byteiq

# 以开发模式安装
pip install -e .
```

### 方法3：使用pip和Git安装

您也可以直接从GitHub仓库安装：

```bash
pip install git+https://github.com/byteiq/byteiq.git
```

## 验证安装

安装完成后，您可以验证ByteIQ是否正确安装：

```bash
byteiq --version
```

或者运行ByteIQ查看欢迎消息：

```bash
byteiq
```

## 初始设置

### 1. 配置API密钥

ByteIQ需要AI提供商的API密钥才能运行。您可以通过两种方式设置：

**交互式设置：**
```bash
byteiq
# 输入 /s 进入设置
# 选择选项2设置API密钥
```

**环境变量：**
```bash
export BYTEIQ_API_KEY="your-api-key-here"
```

### 2. 支持的AI提供商

ByteIQ支持多个AI提供商：
- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo
- **Anthropic**: Claude 3 Haiku, Sonnet, Opus
- **Google**: Gemini Pro
- **Meta**: Llama 2 70B

### 3. 配置模型

您可以设置首选的AI模型：

```bash
byteiq
# 输入 /s 进入设置
# 选择选项3设置模型
```

## Web界面依赖

如果您计划使用Web界面，首次使用时将自动安装额外的依赖项：

- Flask
- Flask-SocketIO

如果您愿意，可以预先安装它们：

```bash
pip install flask flask-socketio
```

## 故障排除

### 常见问题

1. **权限错误**: 如果出现权限错误，请尝试使用 `pip install --user byteiq`

2. **Python版本**: 确保您使用的是Python 3.8或更高版本：
   ```bash
   python --version
   ```

3. **虚拟环境**: 建议使用虚拟环境：
   ```bash
   python -m venv byteiq-env
   source byteiq-env/bin/activate  # Windows上：byteiq-env\Scripts\activate
   pip install byteiq
   ```

### 获取帮助

如果您在安装过程中遇到任何问题，请查看：
- [GitHub Issues](https://github.com/byteiq/byteiq/issues)
- [故障排除指南](troubleshooting.md)
- [支持](support.md)