#!/usr/bin/env python3
"""
调试测试 - 检查命令过滤逻辑
"""

def get_available_commands():
    """获取所有可用命令"""
    return [
        "/help", "/status", "/clear", "/pwd", "/ls", "/cd", "/exit",
        "/chat", "/code", "/review", "/debug"
    ]

def filter_commands(partial_input):
    """根据输入过滤命令"""
    if not partial_input.startswith('/'):
        return []

    commands = get_available_commands()

    # 如果只输入了 "/"，显示所有命令
    if partial_input == '/':
        return commands

    # 否则过滤匹配的命令
    filtered = [cmd for cmd in commands if cmd.startswith(partial_input.lower())]
    return filtered

# 测试
test_inputs = ["/", "/h", "/s", "/help", "/status"]

for test_input in test_inputs:
    suggestions = filter_commands(test_input)
    available_commands = get_available_commands()
    
    print(f"输入: '{test_input}'")
    print(f"  建议: {suggestions}")
    print(f"  是否在可用命令中: {test_input in available_commands}")
    print(f"  应该显示建议: {bool(suggestions and test_input not in available_commands)}")
    print()
