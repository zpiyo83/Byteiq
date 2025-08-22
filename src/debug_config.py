import json
import os

# 使用绝对路径定位到项目根目录下的debug_settings.json
DEBUG_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'debug_settings.json')

def _load_debug_config():
    """加载调试配置文件"""
    if not os.path.exists(DEBUG_CONFIG_PATH):
        # 默认值为 False
        return {'raw_output': False}
    try:
        with open(DEBUG_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 兼容 'T'/'F' 格式，并转换为布尔值
            if 'raw_output' in config and isinstance(config['raw_output'], str):
                config['raw_output'] = config['raw_output'].upper() == 'T'
            return config
    except (json.JSONDecodeError, IOError):
        return {'raw_output': False}

def _save_debug_config(config):
    """保存调试配置文件"""
    try:
        with open(DEBUG_CONFIG_PATH, 'w', encoding='utf-8') as f:
            # 将布尔值保存为 'T' 或 'F' 以满足用户要求
            save_data = config.copy()
            if 'raw_output' in save_data:
                save_data['raw_output'] = 'T' if save_data['raw_output'] else 'F'
            json.dump(save_data, f, indent=2)
        return True
    except IOError:
        return False

def toggle_raw_output():
    """切换原始输出模式的状态"""
    config = _load_debug_config()
    current_state = config.get('raw_output', False)
    config['raw_output'] = not current_state
    if _save_debug_config(config):
        return not current_state
    return None # 表示保存失败

"""
调试配置模块 - 开发者专用设置
"""

def is_raw_output_enabled():
    """检查是否启用了原始输出模式"""
    config = _load_debug_config()
    return config.get('raw_output', False)


