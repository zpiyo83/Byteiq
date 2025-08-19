#!/usr/bin/env python3
"""
检查剩余的emoji
"""

import os
import re

def check_emojis_in_file(filepath):
    """检查文件中的emoji"""
    emoji_pattern = r'[🤖📋📝✅❌🔄💡🎯🚀⚙️🎨📖✏️⚡🔧📦🎮📄🤔❓💬📁🗑️➕🟢🔴]'
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        found_emojis = []
        for i, line in enumerate(lines, 1):
            matches = re.findall(emoji_pattern, line)
            if matches:
                found_emojis.append((i, line.strip(), matches))
        
        return found_emojis
    except Exception as e:
        return []

def main():
    """主函数"""
    print("=== 检查剩余的装饰性emoji ===\n")
    
    # 要检查的文件
    files_to_check = [
        'forgeai.py',
        'main.py',
        'src/ai_client.py',
        'src/ai_tools.py',
        'src/modes.py',
        'src/commands.py',
        'src/todo_renderer.py',
        'src/todo_manager.py',
        'src/ui.py',
        'src/config.py'
    ]
    
    total_found = 0
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            emojis = check_emojis_in_file(filepath)
            if emojis:
                print(f"📁 {filepath}:")
                for line_num, line_content, emoji_list in emojis:
                    print(f"  第{line_num}行: {emoji_list} - {line_content[:80]}...")
                print()
                total_found += len(emojis)
    
    if total_found == 0:
        print("✅ 所有装饰性emoji已清理完成！")
    else:
        print(f"⚠️  还有 {total_found} 处emoji需要处理")
    
    print("\n=== 保留的功能性图标 ===")
    print("以下图标被保留，因为它们是功能性的：")
    print("- ⏳ 🔄 ✅ ❌ (任务状态图标)")
    print("- 🔵 🟡 🟠 🔴 (优先级图标)")
    print("- ❓ ⚪ (默认图标)")
    print("- █ ░ (进度条字符)")

if __name__ == "__main__":
    main()
