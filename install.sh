#!/bin/bash
# Forge AI Code 一键安装脚本
# 支持 Linux, macOS, Windows (Git Bash/WSL)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 图标定义
ROCKET="🚀"
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"
GEAR="⚙️"

# 打印带颜色的消息
print_message() {
    local color=$1
    local icon=$2
    local message=$3
    echo -e "${color}${icon} ${message}${NC}"
}

print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🤖 Forge AI Code                         ║"
    echo "║                   智能AI编程助手                              ║"
    echo "║                     一键安装脚本                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    print_message $BLUE $INFO "检测到操作系统: $OS"
}

# 检查Python版本
check_python() {
    print_message $BLUE $GEAR "检查Python环境..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_message $RED $CROSS "错误: 未找到Python。请先安装Python 3.8或更高版本。"
        exit 1
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_message $RED $CROSS "错误: Python版本过低 ($PYTHON_VERSION)。需要Python 3.8或更高版本。"
        exit 1
    fi
    
    print_message $GREEN $CHECK "Python版本检查通过: $PYTHON_VERSION"
}

# 检查pip
check_pip() {
    print_message $BLUE $GEAR "检查pip..."
    
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        print_message $RED $CROSS "错误: 未找到pip。请先安装pip。"
        exit 1
    fi
    
    print_message $GREEN $CHECK "pip检查通过"
}

# 安装Forge AI Code
install_forge_ai_code() {
    print_message $BLUE $GEAR "开始安装Forge AI Code..."
    
    # 方法1: 从PyPI安装 (如果已发布)
    if $PIP_CMD install forge-ai-code --upgrade 2>/dev/null; then
        print_message $GREEN $CHECK "从PyPI安装成功"
        return 0
    fi
    
    # 方法2: 从GitHub安装
    print_message $YELLOW $WARNING "PyPI安装失败，尝试从GitHub安装..."
    if $PIP_CMD install git+https://github.com/forge-ai/forge-ai-code.git 2>/dev/null; then
        print_message $GREEN $CHECK "从GitHub安装成功"
        return 0
    fi
    
    # 方法3: 下载源码安装
    print_message $YELLOW $WARNING "GitHub安装失败，尝试下载源码安装..."
    
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    if command -v curl &> /dev/null; then
        curl -L https://github.com/forge-ai/forge-ai-code/archive/main.zip -o forge-ai-code.zip
    elif command -v wget &> /dev/null; then
        wget https://github.com/forge-ai/forge-ai-code/archive/main.zip -O forge-ai-code.zip
    else
        print_message $RED $CROSS "错误: 需要curl或wget来下载源码"
        exit 1
    fi
    
    if command -v unzip &> /dev/null; then
        unzip forge-ai-code.zip
        cd forge-ai-code-main
        $PIP_CMD install .
        print_message $GREEN $CHECK "源码安装成功"
    else
        print_message $RED $CROSS "错误: 需要unzip来解压源码"
        exit 1
    fi
    
    # 清理临时文件
    cd /
    rm -rf "$TEMP_DIR"
}

# 验证安装
verify_installation() {
    print_message $BLUE $GEAR "验证安装..."
    
    if command -v forge-ai-code &> /dev/null; then
        VERSION=$(forge-ai-code --version 2>/dev/null || echo "未知版本")
        print_message $GREEN $CHECK "安装验证成功! 版本: $VERSION"
        return 0
    elif command -v fac &> /dev/null; then
        VERSION=$(fac --version 2>/dev/null || echo "未知版本")
        print_message $GREEN $CHECK "安装验证成功! 版本: $VERSION"
        return 0
    else
        print_message $RED $CROSS "安装验证失败"
        return 1
    fi
}

# 显示使用说明
show_usage() {
    print_message $CYAN $ROCKET "安装完成! 使用方法:"
    echo ""
    echo -e "${GREEN}启动Forge AI Code:${NC}"
    echo "  forge-ai-code"
    echo "  或者使用简短命令: fac"
    echo ""
    echo -e "${GREEN}首次使用:${NC}"
    echo "  1. 设置OpenAI API密钥"
    echo "  2. 选择工作模式 (Ask/mostly accepted/sprint)"
    echo "  3. 开始与AI对话编程"
    echo ""
    echo -e "${GREEN}获取帮助:${NC}"
    echo "  forge-ai-code --help"
    echo "  或在程序中输入: /help"
    echo ""
    echo -e "${GREEN}更多信息:${NC}"
    echo "  GitHub: https://github.com/forge-ai/forge-ai-code"
    echo "  文档: https://forge-ai-code.readthedocs.io/"
    echo ""
}

# 主函数
main() {
    print_header
    
    detect_os
    check_python
    check_pip
    
    print_message $BLUE $ROCKET "开始安装过程..."
    
    install_forge_ai_code
    
    if verify_installation; then
        show_usage
        print_message $GREEN $ROCKET "🎉 Forge AI Code 安装成功! 享受AI编程之旅!"
    else
        print_message $RED $CROSS "安装过程中出现问题，请检查错误信息"
        exit 1
    fi
}

# 运行主函数
main "$@"
