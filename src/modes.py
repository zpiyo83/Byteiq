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
            "Ask": "询问模式 - 只读模式，AI只回答问题和读取文件",
            "mostly accepted": "半自动模式 - 读取自动，写入/执行需确认",
            "sprint": "冲刺模式 - 全自动，所有操作无需确认"
        }
        return descriptions.get(mode, "未知模式")

    def can_auto_execute(self, tool_name):
        """检查当前模式是否可以自动执行指定工具"""
        # 只读工具（所有模式都可以自动执行）
        read_only_tools = ['read_file', 'show_todos', 'task_complete']

        if tool_name in read_only_tools:
            return True

        # 写入/执行工具的权限控制
        write_execute_tools = ['write_file', 'create_file', 'insert_code', 'replace_code', 'execute_command', 'add_todo', 'update_todo']

        if tool_name in write_execute_tools:
            if self.current_mode == "Ask":
                return False  # Ask模式禁止写入/执行
            elif self.current_mode == "mostly accepted":
                return "confirm"  # 需要用户确认
            elif self.current_mode == "sprint":
                return True  # 自动执行

        return True  # 默认允许

    def get_mode_permissions(self, mode=None):
        """获取模式权限说明"""
        if mode is None:
            mode = self.current_mode

        permissions = {
            "Ask": {
                "allowed": ["回答问题", "读取文件", "显示TODO"],
                "forbidden": ["创建文件", "写入文件", "插入代码", "替换代码", "执行命令"]
            },
            "mostly accepted": {
                "allowed": ["回答问题", "读取文件", "显示TODO"],
                "confirm": ["创建文件(需确认)", "写入文件(需确认)", "插入代码(需确认)", "替换代码(需确认)", "执行命令(需确认)"]
            },
            "sprint": {
                "allowed": ["回答问题", "读取文件", "显示TODO", "创建文件", "写入文件", "插入代码", "替换代码", "执行命令"]
            }
        }
        return permissions.get(mode, {})
    
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
        permissions = self.get_mode_permissions(new_mode)

        print(f"\n{Fore.LIGHTCYAN_EX}模式已切换: {new_mode}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   {description}{Style.RESET_ALL}")

        # 显示权限信息
        if "allowed" in permissions:
            print(f"{Fore.GREEN}   允许: {' | '.join(permissions['allowed'])}{Style.RESET_ALL}")
        if "confirm" in permissions:
            print(f"{Fore.YELLOW}   需确认: {' | '.join(permissions['confirm'])}{Style.RESET_ALL}")
        if "forbidden" in permissions:
            print(f"{Fore.RED}   禁止: {' | '.join(permissions['forbidden'])}{Style.RESET_ALL}")

        print(f"{Fore.YELLOW}   使用 /mode 继续切换模式{Style.RESET_ALL}\n")

# 全局模式管理器实例
mode_manager = ModeManager()
