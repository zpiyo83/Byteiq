#!/usr/bin/env python3
"""
调试配置模块 - 开发者专用设置
这些设置只能在源代码中修改，不会出现在用户设置界面中
"""

# =============================================================================
# 🔧 开发者调试开关 - 仅限源代码修改
# =============================================================================

# 原始输出开关
# T = 显示原始AI响应数据（未经渲染的完整内容）
# F = 显示渲染后的格式化内容（用户友好的显示）
RAW_OUTPUT_ENABLED = False

# 详细日志开关
# T = 显示详细的调试日志信息
# F = 只显示基本的运行信息
VERBOSE_LOGGING = False

# API调用跟踪开关
# T = 显示所有API调用的详细信息
# F = 隐藏API调用细节
API_TRACE_ENABLED = False

# 工具执行调试开关
# T = 显示工具执行的详细过程
# F = 只显示工具执行结果
TOOL_DEBUG_ENABLED = False

# 提示词调试开关
# T = 显示发送给AI的完整提示词
# F = 隐藏提示词内容
PROMPT_DEBUG_ENABLED = False

# =============================================================================
# 🔍 调试功能函数
# =============================================================================

def is_raw_output_enabled():
    """
    检查是否启用原始输出模式
    
    Returns:
        bool: True表示显示原始数据，False表示显示渲染后内容
    """
    return RAW_OUTPUT_ENABLED

def is_verbose_logging_enabled():
    """
    检查是否启用详细日志
    
    Returns:
        bool: True表示显示详细日志，False表示基本日志
    """
    return VERBOSE_LOGGING

def is_api_trace_enabled():
    """
    检查是否启用API调用跟踪
    
    Returns:
        bool: True表示显示API调用详情，False表示隐藏
    """
    return API_TRACE_ENABLED

def is_tool_debug_enabled():
    """
    检查是否启用工具执行调试
    
    Returns:
        bool: True表示显示工具调试信息，False表示隐藏
    """
    return TOOL_DEBUG_ENABLED

def is_prompt_debug_enabled():
    """
    检查是否启用提示词调试
    
    Returns:
        bool: True表示显示完整提示词，False表示隐藏
    """
    return PROMPT_DEBUG_ENABLED

def get_debug_status():
    """
    获取所有调试开关的状态
    
    Returns:
        dict: 包含所有调试开关状态的字典
    """
    return {
        'raw_output': RAW_OUTPUT_ENABLED,
        'verbose_logging': VERBOSE_LOGGING,
        'api_trace': API_TRACE_ENABLED,
        'tool_debug': TOOL_DEBUG_ENABLED,
        'prompt_debug': PROMPT_DEBUG_ENABLED
    }

def print_debug_status():
    """
    打印当前调试配置状态（仅在开发模式下使用）
    """
    print("🔧 调试配置状态:")
    print(f"  原始输出: {'启用' if RAW_OUTPUT_ENABLED else '禁用'}")
    print(f"  详细日志: {'启用' if VERBOSE_LOGGING else '禁用'}")
    print(f"  API跟踪: {'启用' if API_TRACE_ENABLED else '禁用'}")
    print(f"  工具调试: {'启用' if TOOL_DEBUG_ENABLED else '禁用'}")
    print(f"  提示词调试: {'启用' if PROMPT_DEBUG_ENABLED else '禁用'}")

# =============================================================================
# 📝 使用说明
# =============================================================================
"""
使用方法:

1. 启用原始输出:
   将 RAW_OUTPUT_ENABLED 改为 True

2. 在代码中检查状态:
   from src.debug_config import is_raw_output_enabled
   
   if is_raw_output_enabled():
       print("原始数据:", raw_data)
   else:
       print("渲染后:", formatted_data)

3. 其他调试功能:
   - VERBOSE_LOGGING: 详细日志
   - API_TRACE_ENABLED: API调用跟踪
   - TOOL_DEBUG_ENABLED: 工具执行调试
   - PROMPT_DEBUG_ENABLED: 提示词调试

注意: 这些设置只能在源代码中修改，不会出现在用户设置界面中。
"""
