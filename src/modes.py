"""
工作模式管理模块
"""

from colorama import Fore, Style

# 可用模式列表
AVAILABLE_MODES = ["Ask", "mostly accepted", "sprint"]

class ModeManager:
    """模式管理器"""
    
    def __init__(self):
        self.current_mode = "Ask"  # 默认模式
    
    def get_current_mode(self):
        """获取当前模式"""
        return self.current_mode
    
    def switch_mode(self):
        """切换到下一个模式"""
        current_index = AVAILABLE_MODES.index(self.current_mode)
        next_index = (current_index + 1) % len(AVAILABLE_MODES)
        self.current_mode = AVAILABLE_MODES[next_index]
        return self.current_mode
    
    def get_mode_description(self, mode=None):
        """获取模式描述"""
        if mode is None:
            mode = self.current_mode
            
        descriptions = {
            "Ask": "询问模式 - 标准问答交互",
            "mostly accepted": "大部分接受模式 - 快速确认建议",
            "sprint": "冲刺模式 - 快速开发迭代"
        }
        return descriptions.get(mode, "未知模式")
    
    def handle_mode_switch_command(self, user_input):
        """处理模式切换命令"""
        if user_input.lower() in ['/mode', '/m', 'alt+l']:
            self.show_mode_switch_notification()
            return True
        return False
    
    def show_mode_switch_notification(self):
        """显示模式切换通知"""
        new_mode = self.switch_mode()
        description = self.get_mode_description(new_mode)
        print(f"\n{Fore.LIGHTCYAN_EX}🔄 模式已切换: {new_mode}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   {description}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   按 Alt+L 继续切换模式{Style.RESET_ALL}\n")

# 全局模式管理器实例
mode_manager = ModeManager()
