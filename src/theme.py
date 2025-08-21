"""
主题色管理模块
"""

from colorama import Fore, Style

# 预定义主题色
THEMES = {
    "default": {
        "create": Fore.CYAN,
        "read": Fore.GREEN,
        "execute": Fore.YELLOW,
        "delete": Fore.RED,
        "info": Fore.BLUE,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED
    },
    "ocean": {
        "create": Fore.BLUE,
        "read": Fore.CYAN,
        "execute": Fore.MAGENTA,
        "delete": Fore.RED,
        "info": Fore.BLUE,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED
    },
    "forest": {
        "create": Fore.GREEN,
        "read": Fore.LIGHTGREEN_EX,
        "execute": Fore.YELLOW,
        "delete": Fore.RED,
        "info": Fore.GREEN,
        "success": Fore.LIGHTGREEN_EX,
        "warning": Fore.LIGHTYELLOW_EX,
        "error": Fore.LIGHTRED_EX
    },
    "sunset": {
        "create": Fore.MAGENTA,
        "read": Fore.YELLOW,
        "execute": Fore.RED,
        "delete": Fore.LIGHTRED_EX,
        "info": Fore.MAGENTA,
        "success": Fore.YELLOW,
        "warning": Fore.LIGHTYELLOW_EX,
        "error": Fore.LIGHTRED_EX
    },
    "monochrome": {
        "create": Fore.WHITE,
        "read": Fore.LIGHTWHITE_EX,
        "execute": Fore.WHITE,
        "delete": Fore.LIGHTBLACK_EX,
        "info": Fore.WHITE,
        "success": Fore.LIGHTWHITE_EX,
        "warning": Fore.LIGHTBLACK_EX,
        "error": Fore.LIGHTBLACK_EX
    },
    "neon": {
        "create": Fore.LIGHTCYAN_EX,
        "read": Fore.LIGHTGREEN_EX,
        "execute": Fore.LIGHTMAGENTA_EX,
        "delete": Fore.LIGHTRED_EX,
        "info": Fore.LIGHTBLUE_EX,
        "success": Fore.LIGHTGREEN_EX,
        "warning": Fore.LIGHTYELLOW_EX,
        "error": Fore.LIGHTRED_EX
    },
    "orange": {
        "create": Fore.LIGHTYELLOW_EX,
        "read": Fore.LIGHTGREEN_EX,
        "execute": Fore.LIGHTRED_EX,
        "delete": Fore.RED,
        "info": Fore.YELLOW,
        "success": Fore.GREEN,
        "warning": Fore.LIGHTYELLOW_EX,
        "error": Fore.LIGHTRED_EX
    }
}

# 默认主题
DEFAULT_THEME = "default"

class ThemeManager:
    """主题管理器"""
    
    def __init__(self):
        self.current_theme = DEFAULT_THEME
    
    def set_theme(self, theme_name):
        """设置主题"""
        if theme_name in THEMES:
            self.current_theme = theme_name
            return True
        return False
    
    def get_theme(self):
        """获取当前主题"""
        return self.current_theme
    
    def get_color(self, color_type):
        """获取指定类型的颜色"""
        theme = THEMES.get(self.current_theme, THEMES[DEFAULT_THEME])
        return theme.get(color_type, Fore.WHITE)
    
    def get_tool_color(self, tool_name):
        """根据工具名称获取颜色"""
        tool_colors = {
            "create": "create",
            "read": "read",
            "execute": "execute",
            "delete": "delete"
        }
        color_type = tool_colors.get(tool_name.lower(), "info")
        return self.get_color(color_type)
    
    def format_tool_header(self, tool_name, content):
        """格式化工具头部显示"""
        color = self.get_tool_color(tool_name)
        return f"{color}[ {tool_name.capitalize()} ] ──── {content} ────{Style.RESET_ALL}"
    
    def get_available_themes(self):
        """获取可用主题列表"""
        return list(THEMES.keys())

# 全局主题管理器实例
theme_manager = ThemeManager()