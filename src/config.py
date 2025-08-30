"""
配置管理模块
"""

import os
import json
import getpass
from colorama import Fore, Style

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".byteiq_config.json")
DEFAULT_API_URL = "https://api-inference.modelscope.cn/v1/chat/completions"

def load_config():
    """加载配置文件"""
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(cfg: dict):
    """保存配置文件"""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"{Fore.RED}保存配置失败: {e}{Style.RESET_ALL}")
        return False

def set_api_key_interactive():
    """交互式设置 API 密钥"""
    cfg = load_config()
    print(f"\n{Fore.CYAN}API 密钥设置{Style.RESET_ALL}")
    print(f"配置文件位置: {CONFIG_PATH}")
    
    existing = cfg.get("api_key")
    if existing:
        print(f"{Fore.YELLOW}当前已设置 API Key (已隐藏显示){Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}尚未设置 API Key{Style.RESET_ALL}")

    # 使用 getpass 隐藏输入
    try:
        new_key = getpass.getpass("请输入新的 API Key (输入将被隐藏，回车跳过): ")
    except Exception:
        new_key = input("请输入新的 API Key (回车跳过): ")

    if new_key.strip():
        cfg["api_key"] = new_key.strip()
        if save_config(cfg):
            print(f"{Fore.GREEN}✓ API Key 已保存成功！{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ API Key 保存失败{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}未修改 API Key{Style.RESET_ALL}")

def set_language_interactive():
    """交互式设置语言"""
    cfg = load_config()
    current_lang = cfg.get("language", "zh-CN")
    
    print(f"\n{Fore.CYAN}语言设置{Style.RESET_ALL}")
    print(f"当前语言: {current_lang}")
    print(f"\n{Fore.CYAN}可选语言:{Style.RESET_ALL}")
    print(f"  1 - 中文 (zh-CN)")
    print(f"  2 - English (en-US)")
    print(f"  3 - 日本語 (ja-JP)")
    print(f"  回车 - 保持不变")
    
    choice = input(f"\n{Fore.WHITE}请选择语言 > {Style.RESET_ALL}").strip()
    
    lang_map = {
        "1": "zh-CN",
        "2": "en-US", 
        "3": "ja-JP"
    }
    
    if choice in lang_map:
        cfg["language"] = lang_map[choice]
        if save_config(cfg):
            print(f"{Fore.GREEN}✓ 语言设置已保存！{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ 语言设置保存失败{Style.RESET_ALL}")
    elif choice == "":
        print(f"{Fore.CYAN}语言设置未修改{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}无效选择{Style.RESET_ALL}")

def set_model_interactive():
    """交互式设置AI模型"""
    cfg = load_config()
    current_model = cfg.get("model", "gpt-3.5-turbo")

    print(f"\n{Fore.CYAN}AI模型设置{Style.RESET_ALL}")
    print(f"当前模型: {current_model}")
    print(f"\n{Fore.CYAN}常用模型示例:{Style.RESET_ALL}")
    print(f"  gpt-3.5-turbo, gpt-4, gpt-4-turbo")
    print(f"  claude-3-haiku, claude-3-sonnet, claude-3-opus")
    print(f"  gemini-pro, llama2-70b, 等...")
    print(f"\n{Fore.YELLOW}提示: 直接输入模型名称，回车保持不变{Style.RESET_ALL}")

    new_model = input(f"\n{Fore.WHITE}请输入模型名称 > {Style.RESET_ALL}").strip()

    if new_model:
        cfg["model"] = new_model
        if save_config(cfg):
            print(f"{Fore.GREEN}✓ AI模型设置已保存: {new_model}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ AI模型设置保存失败{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}AI模型设置未修改{Style.RESET_ALL}")

def set_prompt_strength_interactive():
    """交互式设置提示词强度"""
    cfg = load_config()
    current_strength = cfg.get("prompt_strength", "claude")

    print(f"\n{Fore.CYAN}提示词强度设置{Style.RESET_ALL}")
    print(f"当前强度: {current_strength}")
    print(f"\n{Fore.CYAN}可选强度级别:{Style.RESET_ALL}")
    print(f"  1 - claude   (Claude模型专用 - 完整强度)")
    print(f"  2 - flash    (Flash模型专用 - 缩减强度)")
    print(f"  3 - qwen     (Qwen Coder专用 - 保留关键细节)")
    print(f"  4 - mini     (Mini模型专用 - 最简强度)")
    print(f"  回车 - 保持不变")

    print(f"\n{Fore.YELLOW}说明:{Style.RESET_ALL}")
    print(f"  • Claude: 适用于Claude系列模型，提示词最详细完整")
    print(f"  • Flash: 适用于Flash等快速模型，提示词适度缩减")
    print(f"  • Qwen: 适用于Qwen Coder等代码模型，保留关键编程细节")
    print(f"  • Mini: 适用于Mini/Nano/Lite等轻量模型，提示词最简化")

    choice = input(f"\n{Fore.WHITE}请选择强度级别 (1-4) > {Style.RESET_ALL}").strip()

    strength_map = {
        "1": "claude",
        "2": "flash",
        "3": "qwen",
        "4": "mini"
    }

    if choice in strength_map:
        cfg["prompt_strength"] = strength_map[choice]
        if save_config(cfg):
            print(f"{Fore.GREEN}✓ 提示词强度已保存: {strength_map[choice]}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ 提示词强度保存失败{Style.RESET_ALL}")
    elif choice == "":
        print(f"{Fore.CYAN}提示词强度设置未修改{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}无效选择{Style.RESET_ALL}")

def set_theme_interactive():
    """交互式设置主题"""
    from .theme import theme_manager
    
    cfg = load_config()
    current_theme = cfg.get("theme", "default")
    
    print(f"\n{Fore.CYAN}主题设置{Style.RESET_ALL}")
    print(f"当前主题: {current_theme}")
    print(f"\n{Fore.CYAN}可选主题:{Style.RESET_ALL}")
    
    themes = theme_manager.get_available_themes()
    for i, theme in enumerate(themes, 1):
        print(f"  {i} - {theme}")
    print(f"  回车 - 保持不变")
    
    choice = input(f"\n{Fore.WHITE}请选择主题 > {Style.RESET_ALL}").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(themes):
        selected_theme = themes[int(choice) - 1]
        cfg["theme"] = selected_theme
        if save_config(cfg):
            theme_manager.set_theme(selected_theme)
            print(f"{Fore.GREEN}✓ 主题设置已保存: {selected_theme}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ 主题设置保存失败{Style.RESET_ALL}")
    elif choice == "":
        print(f"{Fore.CYAN}主题设置未修改{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}无效选择{Style.RESET_ALL}")

def set_think_mode_interactive():
    """交互式设置深度思考模式"""
    cfg = load_config()
    current_think = cfg.get("think_mode", False)
    
    print(f"\n{Fore.CYAN}深度思考模式设置{Style.RESET_ALL}")
    print(f"当前状态: {'开启' if current_think else '关闭'}")
    print(f"\n{Fore.YELLOW}说明:{Style.RESET_ALL}")
    print(f"  • 开启后，AI将显示思考过程（灰色字体）")
    print(f"  • 思考内容不参与工具调用，仅供参考")
    print(f"  • 可使用 /think 命令快速切换")
    
    print(f"\n{Fore.CYAN}选项:{Style.RESET_ALL}")
    print(f"  1 - 开启深度思考")
    print(f"  2 - 关闭深度思考")
    print(f"  回车 - 保持不变")
    
    choice = input(f"\n{Fore.WHITE}请选择 (1-2) > {Style.RESET_ALL}").strip()
    
    if choice == "1":
        cfg["think_mode"] = True
        if save_config(cfg):
            print(f"{Fore.GREEN}✓ 深度思考模式已开启{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ 设置保存失败{Style.RESET_ALL}")
    elif choice == "2":
        cfg["think_mode"] = False
        if save_config(cfg):
            print(f"{Fore.GREEN}✓ 深度思考模式已关闭{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ 设置保存失败{Style.RESET_ALL}")
    elif choice == "":
        print(f"{Fore.CYAN}深度思考模式设置未修改{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}无效选择{Style.RESET_ALL}")

def get_think_mode():
    """获取深度思考模式状态"""
    cfg = load_config()
    return cfg.get("think_mode", False)

def toggle_think_mode():
    """切换深度思考模式"""
    cfg = load_config()
    current = cfg.get("think_mode", False)
    cfg["think_mode"] = not current
    
    if save_config(cfg):
        status = "开启" if not current else "关闭"
        print(f"{Fore.GREEN}✓ 深度思考模式已{status}{Style.RESET_ALL}")
        return not current
    else:
        print(f"{Fore.RED}✗ 设置保存失败{Style.RESET_ALL}")
        return current

def show_settings():
    """显示设置菜单"""
    from .theme import theme_manager
    
    while True:
        cfg = load_config()
        api_key_status = "已设置 ********" if cfg.get("api_key") else "未设置"
        language_status = cfg.get("language", "zh-CN")
        model_status = cfg.get("model", "gpt-3.5-turbo")
        prompt_strength_status = cfg.get("prompt_strength", "claude")
        theme_status = cfg.get("theme", "default")
        think_status = "开启" if cfg.get("think_mode", False) else "关闭"

        print(f"\n{Fore.LIGHTCYAN_EX}ByteIQ 设置{Style.RESET_ALL}")
        print(f"{'='*60}")
        print(f"API Key: {api_key_status}")
        print(f"语言: {language_status}")
        print(f"AI模型: {model_status}")
        print(f"提示词强度: {prompt_strength_status}")
        print(f"主题: {theme_status}")
        print(f"深度思考: {think_status}")
        print(f"配置文件: {CONFIG_PATH}")
        print(f"{'='*60}")
        print(f"\n{Fore.CYAN}请选择操作:{Style.RESET_ALL}")
        print(f"  1 - 设置语言")
        print(f"  2 - 设置API密钥")
        print(f"  3 - 设置模型")
        print(f"  4 - 设置提示词强度")
        print(f"  5 - 设置主题")
        print(f"  6 - 设置深度思考")
        print(f"  7 - 退出设置")

        choice = input(f"\n{Fore.WHITE}请输入选项 (1-7) > {Style.RESET_ALL}").strip()

        if choice == "1":
            set_language_interactive()
        elif choice == "2":
            set_api_key_interactive()
        elif choice == "3":
            set_model_interactive()
        elif choice == "4":
            set_prompt_strength_interactive()
        elif choice == "5":
            set_theme_interactive()
        elif choice == "6":
            set_think_mode_interactive()
        elif choice == "7":
            print(f"{Fore.CYAN}退出设置{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.YELLOW}无效选择，请输入 1-7{Style.RESET_ALL}")
            input(f"{Fore.CYAN}按回车继续...{Style.RESET_ALL}")
