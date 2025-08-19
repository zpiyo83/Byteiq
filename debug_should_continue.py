#!/usr/bin/env python3
"""
调试should_continue逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from forgeai import AIToolProcessor

def debug_logic():
    """调试逻辑"""
    processor = AIToolProcessor()
    
    response = "我为您创建了文件，包含了所需的功能。文件已保存到指定位置。 <create_file><path>app.py</path><content>完整的应用代码</content></create_file>"
    
    print("调试响应:", response)
    print()
    
    # 检查各个条件
    print("检查条件:")
    print(f"1. 包含task_complete: {'task_complete' in response}")
    print(f"2. 包含继续关键词: {any(keyword in response.lower() for keyword in ['继续', 'continue', '接下来', '然后', '下一步'])}")
    
    # 提取display_text
    import re
    tool_patterns = {
        'create_file': r'<create_file><path>(.*?)</path><content>(.*?)</content></create_file>',
    }
    
    display_text = response
    for tool_name, pattern in tool_patterns.items():
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            # 移除XML标签
            display_text = re.sub(pattern, '', response, flags=re.DOTALL).strip()
            break
    
    print(f"3. display_text长度: {len(display_text.strip())} ('{display_text.strip()}')")
    print(f"4. 响应很短: {len(display_text.strip()) < 30}")
    print(f"5. 包含完成词汇: {any(keyword in response for keyword in ['已完成', '完成了', '已保存', '已创建', '任务完成', '全部完成'])}")
    
    # 实际处理
    result = processor.process_response(response)
    print(f"\n实际结果: should_continue = {result['should_continue']}")

if __name__ == "__main__":
    debug_logic()
