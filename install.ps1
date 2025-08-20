# Forge AI Code PowerShell 一键安装脚本
# 支持 Windows PowerShell 和 PowerShell Core

param(
    [switch]$Force,
    [switch]$Dev,
    [string]$Version = "latest"
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色定义
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
    Magenta = "Magenta"
}

# 图标定义
$Icons = @{
    Rocket = "🚀"
    Check = "✅"
    Cross = "❌"
    Warning = "⚠️"
    Info = "ℹ️"
    Gear = "⚙️"
}

function Write-ColorMessage {
    param(
        [string]$Message,
        [string]$Color = "White",
        [string]$Icon = ""
    )
    
    $fullMessage = if ($Icon) { "$Icon $Message" } else { $Message }
    Write-Host $fullMessage -ForegroundColor $Color
}

function Write-Header {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║                    🤖 Forge AI Code                         ║" -ForegroundColor Magenta
    Write-Host "║                   智能AI编程助手                              ║" -ForegroundColor Magenta
    Write-Host "║                 PowerShell 一键安装                          ║" -ForegroundColor Magenta
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
}

function Test-PythonInstallation {
    Write-ColorMessage "检查Python环境..." $Colors.Blue $Icons.Gear
    
    $pythonCommands = @("python", "python3", "py")
    $pythonCmd = $null
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $pythonCmd = $cmd
                break
            }
        }
        catch {
            continue
        }
    }
    
    if (-not $pythonCmd) {
        Write-ColorMessage "错误: 未找到Python。请先安装Python 3.8或更高版本。" $Colors.Red $Icons.Cross
        Write-ColorMessage "下载地址: https://www.python.org/downloads/" $Colors.Yellow $Icons.Info
        exit 1
    }
    
    # 检查Python版本
    $versionOutput = & $pythonCmd --version 2>&1
    $versionMatch = $versionOutput -match "Python (\d+)\.(\d+)\.(\d+)"
    
    if ($versionMatch) {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-ColorMessage "错误: Python版本过低 ($versionOutput)。需要Python 3.8或更高版本。" $Colors.Red $Icons.Cross
            exit 1
        }
        
        Write-ColorMessage "Python版本检查通过: $versionOutput" $Colors.Green $Icons.Check
        return $pythonCmd
    }
    else {
        Write-ColorMessage "警告: 无法解析Python版本，继续安装..." $Colors.Yellow $Icons.Warning
        return $pythonCmd
    }
}

function Test-PipInstallation {
    param([string]$PythonCmd)
    
    Write-ColorMessage "检查pip..." $Colors.Blue $Icons.Gear
    
    try {
        & $PythonCmd -m pip --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorMessage "pip检查通过" $Colors.Green $Icons.Check
            return $true
        }
    }
    catch {
        Write-ColorMessage "错误: pip未正确安装。" $Colors.Red $Icons.Cross
        exit 1
    }
}

function Install-ForgeAICode {
    param(
        [string]$PythonCmd,
        [string]$Version,
        [bool]$DevMode
    )
    
    Write-ColorMessage "开始安装Forge AI Code..." $Colors.Blue $Icons.Gear
    
    # 升级pip
    Write-ColorMessage "升级pip..." $Colors.Blue $Icons.Gear
    & $PythonCmd -m pip install --upgrade pip
    
    $installArgs = @()
    
    if ($DevMode) {
        $installArgs += @("--editable", ".")
        Write-ColorMessage "开发模式安装..." $Colors.Yellow $Icons.Info
    }
    else {
        # 方法1: 从PyPI安装
        Write-ColorMessage "尝试从PyPI安装..." $Colors.Blue $Icons.Info
        try {
            if ($Version -eq "latest") {
                & $PythonCmd -m pip install forge-ai-code --upgrade
            }
            else {
                & $PythonCmd -m pip install "forge-ai-code==$Version" --upgrade
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-ColorMessage "从PyPI安装成功" $Colors.Green $Icons.Check
                return $true
            }
        }
        catch {
            Write-ColorMessage "PyPI安装失败，尝试其他方法..." $Colors.Yellow $Icons.Warning
        }
        
        # 方法2: 从GitHub安装
        Write-ColorMessage "尝试从GitHub安装..." $Colors.Blue $Icons.Info
        try {
            & $PythonCmd -m pip install git+https://github.com/forge-ai/forge-ai-code.git
            
            if ($LASTEXITCODE -eq 0) {
                Write-ColorMessage "从GitHub安装成功" $Colors.Green $Icons.Check
                return $true
            }
        }
        catch {
            Write-ColorMessage "GitHub安装失败" $Colors.Yellow $Icons.Warning
        }
        
        # 方法3: 手动指导
        Write-ColorMessage "自动安装失败，请手动安装:" $Colors.Red $Icons.Cross
        Write-Host ""
        Write-Host "1. 下载源码: https://github.com/forge-ai/forge-ai-code/archive/main.zip"
        Write-Host "2. 解压到任意目录"
        Write-Host "3. 在解压目录中运行: pip install ."
        Write-Host ""
        exit 1
    }
}

function Test-Installation {
    Write-ColorMessage "验证安装..." $Colors.Blue $Icons.Gear
    
    $commands = @("forge-ai-code", "fac")
    
    foreach ($cmd in $commands) {
        try {
            $version = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-ColorMessage "安装验证成功! 版本: $version" $Colors.Green $Icons.Check
                return $true
            }
        }
        catch {
            continue
        }
    }
    
    Write-ColorMessage "安装验证失败" $Colors.Red $Icons.Cross
    return $false
}

function Show-Usage {
    Write-ColorMessage "安装完成! 使用方法:" $Colors.Cyan $Icons.Rocket
    Write-Host ""
    Write-Host "启动Forge AI Code:" -ForegroundColor Green
    Write-Host "  forge-ai-code"
    Write-Host "  或者使用简短命令: fac"
    Write-Host ""
    Write-Host "首次使用:" -ForegroundColor Green
    Write-Host "  1. 设置OpenAI API密钥"
    Write-Host "  2. 选择工作模式 (Ask/mostly accepted/sprint)"
    Write-Host "  3. 开始与AI对话编程"
    Write-Host ""
    Write-Host "获取帮助:" -ForegroundColor Green
    Write-Host "  forge-ai-code --help"
    Write-Host "  或在程序中输入: /help"
    Write-Host ""
    Write-Host "更多信息:" -ForegroundColor Green
    Write-Host "  GitHub: https://github.com/forge-ai/forge-ai-code"
    Write-Host "  文档: https://forge-ai-code.readthedocs.io/"
    Write-Host ""
}

# 主函数
function Main {
    Write-Header
    
    # 检查管理员权限（可选）
    if (-not $Force) {
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        
        if (-not $isAdmin) {
            Write-ColorMessage "建议以管理员身份运行以避免权限问题" $Colors.Yellow $Icons.Warning
            Write-ColorMessage "继续安装..." $Colors.Blue $Icons.Info
        }
    }
    
    try {
        $pythonCmd = Test-PythonInstallation
        Test-PipInstallation -PythonCmd $pythonCmd
        
        Write-ColorMessage "开始安装过程..." $Colors.Blue $Icons.Rocket
        
        Install-ForgeAICode -PythonCmd $pythonCmd -Version $Version -DevMode $Dev
        
        if (Test-Installation) {
            Show-Usage
            Write-ColorMessage "🎉 Forge AI Code 安装成功! 享受AI编程之旅!" $Colors.Green $Icons.Rocket
        }
        else {
            Write-ColorMessage "安装过程中出现问题，请检查错误信息" $Colors.Red $Icons.Cross
            exit 1
        }
    }
    catch {
        Write-ColorMessage "安装过程中出现错误: $($_.Exception.Message)" $Colors.Red $Icons.Cross
        exit 1
    }
}

# 运行主函数
Main
