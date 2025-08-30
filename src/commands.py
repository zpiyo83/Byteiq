"""
命令系统模块
"""

import os
from colorama import Fore, Style
from .todo_manager import todo_manager
from .todo_renderer import get_todo_renderer

def get_available_commands():
    """获取所有可用命令"""
    return [
        "/help", "/status", "/clear", "/pwd", "/ls", "/cd", "/exit",
        "/s", "/mode", "/clear-history", "/todo", "/todos", "/compact",
        "/hacpp", "/fix", "/analyze", "/chat", "/export", "/init", "/think"
    ]

def get_command_descriptions():
    """获取命令描述"""
    return {
        "/help": "显示帮助信息",
        "/status": "显示当前状态",
        "/clear": "清除上下文",
        "/pwd": "显示当前目录",
        "/ls": "列出当前目录文件",
        "/cd": "切换目录",
        "/exit": "退出程序",
        "/s": "设置管理",
        "/mode": "切换工作模式",
        "/clear-history": "清除AI对话历史",
        "/todo": "TODO任务管理",
        "/todos": "显示TODO列表",
        "/compact": "压缩上下文",
        "/hacpp": "HACPP双AI协作模式",
        "/fix": "AI辅助调试",
        "/analyze": "分析项目并生成BYTEIQ.md配置文件",
        "/chat": "聊天上下文管理 (save/load/delete)",
        "/export": "导出上下文到当前目录",
        "/init": "超大型项目分析模式 - 生成完整项目文档",
        "/think": "切换深度思考模式"
    }

def filter_commands(partial_input):
    """根据输入过滤命令"""
    if not partial_input.startswith('/'):
        return []
    
    commands = get_available_commands()
    descriptions = get_command_descriptions()
    
    # 过滤匹配的命令
    matching_commands = []
    for cmd in commands:
        if cmd.startswith(partial_input):
            matching_commands.append((cmd, descriptions.get(cmd, "")))
    
    return matching_commands

def show_help():
    """显示帮助信息"""
    help_text = f"""
{Fore.LIGHTCYAN_EX}ByteIQ - 命令帮助{Style.RESET_ALL}

{Fore.CYAN}基础命令:{Style.RESET_ALL}
  {Fore.WHITE}/help{Style.RESET_ALL}     - 显示此帮助信息
  {Fore.WHITE}/status{Style.RESET_ALL}   - 显示当前状态
  {Fore.WHITE}/clear{Style.RESET_ALL}    - 清除上下文
  {Fore.WHITE}/pwd{Style.RESET_ALL}      - 显示当前目录
  {Fore.WHITE}/ls{Style.RESET_ALL}       - 列出当前目录文件
  {Fore.WHITE}/cd <dir>{Style.RESET_ALL} - 切换目录
  {Fore.WHITE}/exit{Style.RESET_ALL}     - 退出程序

{Fore.CYAN}AI功能:{Style.RESET_ALL}
  {Fore.GREEN}直接输入{Style.RESET_ALL}        - 与AI助手对话（无需命令前缀）
  {Fore.WHITE}/s{Style.RESET_ALL}        - 设置（API密钥、语言、模型、主题）
  {Fore.WHITE}/mode{Style.RESET_ALL}     - 切换工作模式
  {Fore.WHITE}/clear-history{Style.RESET_ALL} - 清除AI对话历史
  {Fore.WHITE}/compact{Style.RESET_ALL}      - 压缩上下文
  {Fore.WHITE}/analyze{Style.RESET_ALL}      - AI增强项目分析并生成BYTEIQ.md配置文件
  {Fore.WHITE}/init{Style.RESET_ALL}        - 超大型项目分析模式 - 生成完整项目文档
  {Fore.WHITE}/context{Style.RESET_ALL}      - 上下文管理 (set/status/clear/save/load)
  {Fore.WHITE}/chat save{Style.RESET_ALL}    - 保存上下文到软件目录
  {Fore.WHITE}/chat load{Style.RESET_ALL}    - 交互式加载上下文
  {Fore.WHITE}/chat delete{Style.RESET_ALL}  - 交互式删除上下文
  {Fore.WHITE}/export{Style.RESET_ALL}       - 导出上下文到当前目录
  {Fore.WHITE}/fix{Style.RESET_ALL}          - AI辅助调试 (bug/status/end)
  {Fore.WHITE}/think{Style.RESET_ALL}        - 切换深度思考模式

{Fore.MAGENTA}HACPP模式 (双AI协作):{Style.RESET_ALL}
  {Fore.WHITE}/HACPP{Style.RESET_ALL}        - 激活HACPP模式（需要测试码）
  {Fore.WHITE}/HACPP model{Style.RESET_ALL}  - 设置便宜模型名称
  {Fore.WHITE}/HACPP status{Style.RESET_ALL} - 显示HACPP模式状态
  {Fore.WHITE}/HACPP off{Style.RESET_ALL}    - 关闭HACPP模式

{Fore.CYAN}TODO任务管理:{Style.RESET_ALL}
  {Fore.WHITE}/todos{Style.RESET_ALL}    - 显示TODO任务列表
  {Fore.WHITE}/todo{Style.RESET_ALL}     - TODO任务管理菜单

{Fore.CYAN}MCP服务器管理:{Style.RESET_ALL}
  {Fore.WHITE}/mcp{Style.RESET_ALL}      - MCP服务器管理 (start/stop/status/config)

{Fore.CYAN}AI工具能力:{Style.RESET_ALL}
  {Fore.YELLOW}读取文件{Style.RESET_ALL}     - AI可以读取项目文件
  {Fore.YELLOW}写入文件{Style.RESET_ALL}     - AI可以创建和修改文件
  {Fore.YELLOW}执行命令{Style.RESET_ALL}     - AI可以执行系统命令
  {Fore.YELLOW}任务管理{Style.RESET_ALL}     - AI可以创建和管理TODO任务
  {Fore.YELLOW}项目感知{Style.RESET_ALL}     - AI自动了解项目结构

{Fore.CYAN}工作模式:{Style.RESET_ALL}
  {Fore.YELLOW}Ask{Style.RESET_ALL}            - 询问模式（标准问答交互）
  {Fore.YELLOW}mostly accepted{Style.RESET_ALL} - 大部分接受模式（快速确认建议）
  {Fore.YELLOW}sprint{Style.RESET_ALL}         - 冲刺模式（快速开发迭代）

{Fore.GREEN}使用提示: 直接输入您的需求，AI会自动帮您完成编程任务！{Style.RESET_ALL}
"""
    print(help_text)

def show_status():
    """显示当前状态"""
    from .config import load_config
    from .modes import mode_manager
    
    cfg = load_config()
    api_key_status = "已设置" if cfg.get("api_key") else "未设置"
    language = cfg.get("language", "zh-CN")
    model = cfg.get("model", "gpt-3.5-turbo")
    current_mode = mode_manager.get_current_mode()
    
    status_text = f"""
{Fore.LIGHTCYAN_EX}ByteIQ - 当前状态{Style.RESET_ALL}

{Fore.CYAN}系统信息:{Style.RESET_ALL}
  当前目录: {Fore.WHITE}{os.getcwd()}{Style.RESET_ALL}
  工作模式: {Fore.YELLOW}{current_mode}{Style.RESET_ALL}

{Fore.CYAN}配置信息:{Style.RESET_ALL}
  API Key: {Fore.WHITE}{api_key_status}{Style.RESET_ALL}
  语言: {Fore.WHITE}{language}{Style.RESET_ALL}
  AI模型: {Fore.WHITE}{model}{Style.RESET_ALL}

{Fore.CYAN}AI功能状态:{Style.RESET_ALL}
  {Fore.YELLOW}所有AI功能正在开发中...{Style.RESET_ALL}
"""
    print(status_text)

def handle_todo_command():
    """处理TODO命令"""
    todo_renderer = get_todo_renderer(todo_manager)

    while True:
        print(f"\n{Fore.LIGHTCYAN_EX}TODO任务管理{Style.RESET_ALL}")
        print(f"{Fore.CYAN}可用命令:{Style.RESET_ALL}")
        print("  /h, /help, /?           - 显示此帮助信息")
        print("  /s, /setting, /settings - 进入设置菜单")
        print("  /t, /todo, /todos       - 显示TODO列表")
        print("  /mcp, /m                - MCP协议管理")
        print("  /hacpp [on|off|status]  - HACPP双AI协作模式")
        print("  /fix [error_description] - AI辅助调试")
        print("  /compact                - 上下文压缩")
        print("  /debug raw              - 切换原始输出模式")
        print("  /clear, /c              - 智能清除选项")
        print("  /exit, /quit, /q        - 退出程序")
        print()
        print(f"{Fore.MAGENTA}🚀 Claude Code 增强功能:{Style.RESET_ALL}")
        print("  /context, /ctx          - 上下文管理（200K token窗口）")
        print("  /context clear          - 清除所有上下文")
        print("  /context save [文件名]  - 保存上下文到文件")
        print("  /context load [文件名]  - 从文件加载上下文")
        print("  /agent                  - 代理式编程状态")
        print("  /agent clear            - 清除执行计划")
        print("  /agent next             - 显示下一个任务")
        print()
        print(f"{Fore.YELLOW}工作模式:{Style.RESET_ALL}")
        print("  /ask                    - Ask模式（需要确认）")
        print("  /mostly                 - Mostly Accepted模式（大部分自动执行）")
        print("  /sprint                 - Sprint模式（完全自动执行）")
        print()
        print(f"{Fore.CYAN}🧠 思考模式关键词:{Style.RESET_ALL}")
        print("  think                   - 基础深度思考")
        print("  think hard              - 加强深度思考")
        print("  think harder            - 高级深度思考")
        print("  ultrathink              - 最高级深度思考")
        print()
        print(f"{Fore.GREEN}提示: 在任何时候按ESC可以中断AI处理{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}请选择操作:{Style.RESET_ALL}")
        print(f"  1 - 显示任务列表")
        print(f"  2 - 添加新任务")
        print(f"  3 - 更新任务状态")
        print(f"  4 - 删除任务")
        print(f"  5 - 清除已完成任务")
        print(f"  6 - 任务统计")
        print(f"  0 - 返回主菜单")

        choice = input(f"\n{Fore.WHITE}请输入选项 (0-6) > {Style.RESET_ALL}").strip()

        if choice == "0":
            break
        elif choice == "1":
            print(todo_renderer.render_todo_list())
        elif choice == "2":
            add_todo_interactive()
        elif choice == "3":
            update_todo_interactive()
        elif choice == "4":
            delete_todo_interactive()
        elif choice == "5":
            todo_manager.clear_completed()
            print(f"{Fore.GREEN}已清除所有已完成的任务{Style.RESET_ALL}")
        elif choice == "6":
            show_todo_stats()
        else:
            print(f"{Fore.YELLOW}无效选择，请输入 0-6{Style.RESET_ALL}")

        if choice != "0":
            input(f"{Fore.CYAN}按回车继续...{Style.RESET_ALL}")

def add_todo_interactive():
    """交互式添加TODO"""
    print(f"\n{Fore.CYAN}添加新任务{Style.RESET_ALL}")

    title = input(f"任务标题: ").strip()
    if not title:
        print(f"{Fore.RED}任务标题不能为空{Style.RESET_ALL}")
        return

    description = input(f"任务描述 (可选): ").strip()

    print(f"优先级选择:")
    print(f"  1 - 低 (low)")
    print(f"  2 - 中 (medium)")
    print(f"  3 - 高 (high)")
    print(f"  4 - 紧急 (urgent)")

    priority_choice = input(f"优先级 (1-4, 默认2): ").strip()
    priority_map = {"1": "low", "2": "medium", "3": "high", "4": "urgent"}
    priority = priority_map.get(priority_choice, "medium")

    todo_id = todo_manager.add_todo(title, description, priority)
    print(f"{Fore.GREEN}成功添加任务: {title} (ID: {todo_id[:8]}){Style.RESET_ALL}")

def update_todo_interactive():
    """交互式更新TODO"""
    print(f"\n{Fore.CYAN}更新任务状态{Style.RESET_ALL}")

    # 显示当前任务
    todos = todo_manager.get_root_todos()
    if not todos:
        print(f"{Fore.YELLOW}暂无任务{Style.RESET_ALL}")
        return

    print(f"当前任务:")
    for i, todo in enumerate(todos, 1):
        status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "cancelled": "❌"}.get(todo.status, "❓")
        print(f"  {i}. {status_icon} {todo.title} (ID: {todo.id[:8]})")

    choice = input(f"选择任务编号或输入任务ID: ").strip()

    # 确定任务ID
    todo_id = None
    if choice.isdigit() and 1 <= int(choice) <= len(todos):
        todo_id = todos[int(choice) - 1].id
    else:
        # 尝试匹配ID
        for todo in todo_manager.todos.values():
            if todo.id.startswith(choice) or todo.id == choice:
                todo_id = todo.id
                break

    if not todo_id:
        print(f"{Fore.RED}未找到指定的任务{Style.RESET_ALL}")
        return

    todo = todo_manager.get_todo(todo_id)
    print(f"\n当前任务: {todo.title}")
    print(f"当前状态: {todo.status}")

    print(f"新状态选择:")
    print(f"  1 - 待办 (pending)")
    print(f"  2 - 进行中 (in_progress)")
    print(f"  3 - 已完成 (completed)")
    print(f"  4 - 已取消 (cancelled)")

    status_choice = input(f"新状态 (1-4): ").strip()
    status_map = {"1": "pending", "2": "in_progress", "3": "completed", "4": "cancelled"}
    new_status = status_map.get(status_choice)

    if not new_status:
        print(f"{Fore.RED}无效的状态选择{Style.RESET_ALL}")
        return

    progress = 0
    if new_status == "in_progress":
        progress_input = input(f"进度 (0-100, 默认0): ").strip()
        if progress_input.isdigit():
            progress = min(100, max(0, int(progress_input)))
    elif new_status == "completed":
        progress = 100

    success = todo_manager.update_todo(todo_id, status=new_status, progress=progress)
    if success:
        print(f"{Fore.GREEN}成功更新任务状态{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}更新任务失败{Style.RESET_ALL}")

def delete_todo_interactive():
    """交互式删除TODO"""
    print(f"\n{Fore.CYAN}删除任务{Style.RESET_ALL}")

    todos = todo_manager.get_root_todos()
    if not todos:
        print(f"{Fore.YELLOW}暂无任务{Style.RESET_ALL}")
        return

    print(f"当前任务:")
    for i, todo in enumerate(todos, 1):
        status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "cancelled": "❌"}.get(todo.status, "❓")
        print(f"  {i}. {status_icon} {todo.title} (ID: {todo.id[:8]})")

    choice = input(f"选择要删除的任务编号或输入任务ID: ").strip()

    # 确定任务ID
    todo_id = None
    if choice.isdigit() and 1 <= int(choice) <= len(todos):
        todo_id = todos[int(choice) - 1].id
    else:
        for todo in todo_manager.todos.values():
            if todo.id.startswith(choice) or todo.id == choice:
                todo_id = todo.id
                break

    if not todo_id:
        print(f"{Fore.RED}未找到指定的任务{Style.RESET_ALL}")
        return

    todo = todo_manager.get_todo(todo_id)
    confirm = input(f"确认删除任务 '{todo.title}'? (y/N): ").strip().lower()

    if confirm == 'y':
        success = todo_manager.delete_todo(todo_id)
        if success:
            print(f"{Fore.GREEN}成功删除任务{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}删除任务失败{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}已取消删除{Style.RESET_ALL}")

def show_todo_stats():
    """显示TODO统计"""
    stats = todo_manager.get_stats()
    todo_renderer = get_todo_renderer(todo_manager)

    print(f"\n{Fore.LIGHTCYAN_EX}TODO统计信息{Style.RESET_ALL}")
    print(f"总任务数: {stats['total']}")
    print(f"待办任务: {Fore.YELLOW}{stats['pending']}{Style.RESET_ALL}")
    print(f"进行中: {Fore.CYAN}{stats['in_progress']}{Style.RESET_ALL}")
    print(f"已完成: {Fore.GREEN}{stats['completed']}{Style.RESET_ALL}")
    print(f"已取消: {Fore.RED}{stats['cancelled']}{Style.RESET_ALL}")

    if stats['total'] > 0:
        completion_rate = (stats['completed'] / stats['total']) * 100
        print(f"完成率: {Fore.GREEN}{completion_rate:.1f}%{Style.RESET_ALL}")

def handle_think_command():
    """处理/think命令"""
    from .config import toggle_think_mode, get_think_mode
    
    new_status = toggle_think_mode()
    status_text = "开启" if new_status else "关闭"
    
    print(f"\n{Fore.CYAN}🧠 深度思考模式已{status_text}{Style.RESET_ALL}")
    
    if new_status:
        print(f"{Fore.YELLOW}说明:{Style.RESET_ALL}")
        print(f"  • AI将显示思考过程（灰色字体）")
        print(f"  • 思考内容不参与工具调用")
        print(f"  • 再次输入 /think 可关闭")
    else:
        print(f"{Fore.YELLOW}深度思考模式已关闭{Style.RESET_ALL}")

def show_todos():
    """显示TODO列表"""
    todo_renderer = get_todo_renderer(todo_manager)
    print(todo_renderer.render_todo_list())
