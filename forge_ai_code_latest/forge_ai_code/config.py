"""
配置管理模块
"""

import os
import json
import getpass
from colorama import Fore, Style

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".forgeai_config.json")
DEFAULT_API_URL = "https://www.lumjf.com/v1/chat/completions"

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

def show_settings():
    """显示设置菜单"""
    while True:
        cfg = load_config()
        api_key_status = "已设置 ********" if cfg.get("api_key") else "未设置"
        language_status = cfg.get("language", "zh-CN")
        model_status = cfg.get("model", "gpt-3.5-turbo")
        
        print(f"\n{Fore.LIGHTCYAN_EX}Forge AI Code 设置{Style.RESET_ALL}")
        print(f"{'='*50}")
        print(f"API Key: {api_key_status}")
        print(f"语言: {language_status}")
        print(f"AI模型: {model_status}")
        print(f"配置文件: {CONFIG_PATH}")
        print(f"{'='*50}")
        print(f"\n{Fore.CYAN}请选择操作:{Style.RESET_ALL}")
        print(f"  1 - 设置语言")
        print(f"  2 - 设置API密钥")
        print(f"  3 - 设置模型")
        print(f"  4 - 退出设置")
        
        choice = input(f"\n{Fore.WHITE}请输入选项 (1-4) > {Style.RESET_ALL}").strip()
        
        if choice == "1":
            set_language_interactive()
        elif choice == "2":
            set_api_key_interactive()
        elif choice == "3":
            set_model_interactive()
        elif choice == "4":
            print(f"{Fore.CYAN}退出设置{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.YELLOW}无效选择，请输入 1-4{Style.RESET_ALL}")
            input(f"{Fore.CYAN}按回车继续...{Style.RESET_ALL}")
