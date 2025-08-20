"""
AI工具系统 - 处理AI的工具调用
"""

import os
import re
import subprocess
from colorama import Fore, Style
from .todo_manager import todo_manager
from .todo_renderer import get_todo_renderer
from .modes import mode_manager

class AIToolProcessor:
    """AI工具处理器"""
    
    def __init__(self):
        self.tools = {
            'read_file': self.read_file,
            'write_file': self.write_file,
            'create_file': self.create_file,
            'insert_code': self.insert_code,
            'replace_code': self.replace_code,
            'execute_command': self.execute_command,
            'add_todo': self.add_todo,
            'update_todo': self.update_todo,
            'show_todos': self.show_todos,
            'task_complete': self.task_complete
        }
        self.todo_renderer = get_todo_renderer(todo_manager)
    
    def process_response(self, ai_response):
        """处理AI响应，提取和执行工具调用"""
        # 查找XML工具调用
        tool_patterns = {
            'read_file': r'<read_file><path>(.*?)</path></read_file>',
            'write_file': r'<write_file><path>(.*?)</path><content>(.*?)</content></write_file>',
            'create_file': r'<create_file><path>(.*?)</path><content>(.*?)</content></create_file>',
            'insert_code': r'<insert_code><path>(.*?)</path><line>(.*?)</line><content>(.*?)</content></insert_code>',
            'replace_code': r'<replace_code><path>(.*?)</path><start_line>(.*?)</start_line><end_line>(.*?)</end_line><content>(.*?)</content></replace_code>',
            'execute_command': r'<execute_command><command>(.*?)</command></execute_command>',
            'add_todo': r'<add_todo><title>(.*?)</title><description>(.*?)</description><priority>(.*?)</priority></add_todo>',
            'update_todo': r'<update_todo><id>(.*?)</id><status>(.*?)</status><progress>(.*?)</progress></update_todo>',
            'show_todos': r'<show_todos></show_todos>',
            'task_complete': r'<task_complete><summary>(.*?)</summary></task_complete>'
        }
        
        tool_found = False
        tool_result = ""
        display_text = ai_response
        
        for tool_name, pattern in tool_patterns.items():
            matches = re.findall(pattern, ai_response, re.DOTALL)
            if matches:
                tool_found = True

                # 检查模式权限
                permission = mode_manager.can_auto_execute(tool_name)

                if permission is False:
                    # Ask模式禁止的操作
                    tool_result = f"当前模式 ({mode_manager.get_current_mode()}) 不允许此操作"
                    display_text = f"操作被禁止: {tool_name}"
                elif permission == "confirm":
                    # mostly accepted模式需要确认的操作
                    if tool_name in ['write_file', 'create_file']:
                        path, content = matches[0]
                        action = "创建文件" if tool_name == 'create_file' else "写入文件"
                        content_preview = self._get_content_preview(content.strip())

                        # 显示预览并询问确认
                        print(f"\n{Fore.YELLOW}AI想要{action}: {path.strip()}{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}内容预览:\n{content_preview}{Style.RESET_ALL}")

                        if self._ask_user_confirmation(f"{action} {path.strip()}"):
                            tool_result = self.tools[tool_name](path.strip(), content.strip())
                            display_text = f"用户确认 - {action} {path.strip()}"
                        else:
                            tool_result = "用户取消了操作"
                            display_text = f"用户取消 - {action} {path.strip()}"
                    elif tool_name in ['insert_code', 'replace_code']:
                        # 代码编辑操作的确认
                        if tool_name == 'insert_code':
                            path, line, content = matches[0]
                            action = f"在第{line.strip()}行插入代码"
                            preview_info = f"文件: {path.strip()}\n插入位置: 第{line.strip()}行"
                        else:  # replace_code
                            path, start_line, end_line, content = matches[0]
                            action = f"替换第{start_line.strip()}-{end_line.strip()}行代码"
                            preview_info = f"文件: {path.strip()}\n替换范围: 第{start_line.strip()}-{end_line.strip()}行"

                        content_preview = self._get_content_preview(content.strip())

                        # 显示代码编辑预览
                        print(f"\n{Fore.YELLOW}AI想要{action}: {path.strip()}{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}{preview_info}{Style.RESET_ALL}")

                        # 显示原始代码（如果是替换操作）
                        if tool_name == 'replace_code':
                            original_lines = self._get_file_lines(path.strip(), int(start_line.strip()), int(end_line.strip()))
                            if original_lines:
                                print(f"{Fore.RED}删除的代码:{Style.RESET_ALL}")
                                for i, line in enumerate(original_lines, int(start_line.strip())):
                                    print(f"{Fore.RED}- {i:3d}: {line.rstrip()}{Style.RESET_ALL}")

                        # 显示新代码
                        print(f"{Fore.GREEN}{'插入' if tool_name == 'insert_code' else '替换'}的代码:{Style.RESET_ALL}")
                        for i, line in enumerate(content.strip().split('\n'), 1):
                            print(f"{Fore.GREEN}+ {i:3d}: {line}{Style.RESET_ALL}")

                        if self._ask_user_confirmation(action):
                            if tool_name == 'insert_code':
                                tool_result = self.tools[tool_name](path.strip(), int(line.strip()), content.strip())
                            else:
                                tool_result = self.tools[tool_name](path.strip(), int(start_line.strip()), int(end_line.strip()), content.strip())
                            display_text = f"用户确认 - {action}"
                        else:
                            tool_result = "用户取消了代码编辑操作"
                            display_text = f"用户取消 - {action}"
                    elif tool_name == 'execute_command':
                        command = matches[0].strip()
                        print(f"\n{Fore.YELLOW}AI想要执行命令: {command}{Style.RESET_ALL}")

                        if self._ask_user_confirmation(f"执行命令: {command}"):
                            tool_result = self.tools[tool_name](command)
                            display_text = f"用户确认 - 执行命令: {command}"
                        else:
                            tool_result = "用户取消了命令执行"
                            display_text = f"用户取消 - 执行命令: {command}"
                    else:
                        # 其他需要确认的操作
                        if self._ask_user_confirmation(f"执行 {tool_name} 操作"):
                            tool_result = self._execute_tool_with_matches(tool_name, matches)
                            display_text = f"用户确认 - {tool_name}"
                        else:
                            tool_result = "用户取消了操作"
                            display_text = f"用户取消 - {tool_name}"
                else:
                    # 自动执行（sprint模式或允许的操作）
                    tool_result, display_text = self._execute_tool_with_matches(tool_name, matches)

                break
        
        # 如果没有工具调用，移除XML标签显示纯文本
        if not tool_found:
            display_text = self._remove_xml_tags(ai_response)
        
        # 智能继续判断逻辑
        should_continue = False
        if tool_found:
            # 明确的停止条件
            if 'task_complete' in ai_response:
                should_continue = False
            else:
                # 根据模式和工具结果决定是否继续
                should_continue = self._should_continue_based_on_context(tool_name, tool_result, ai_response)

        return {
            'has_tool': tool_found,
            'tool_result': tool_result,
            'display_text': display_text,
            'should_continue': should_continue
        }
    
    def _get_content_preview(self, content, max_lines=5):
        """获取内容预览（前5行）"""
        lines = content.split('\n')
        if len(lines) <= max_lines:
            return content
        else:
            preview_lines = lines[:max_lines]
            return '\n'.join(preview_lines) + f"\n... (还有 {len(lines) - max_lines} 行)"
    
    def _remove_xml_tags(self, text):
        """移除XML标签"""
        # 移除所有XML标签
        clean_text = re.sub(r'<[^>]+>', '', text)
        return clean_text.strip()
    
    def read_file(self, path):
        """读取文件工具"""
        try:
            if not os.path.exists(path):
                return f"错误：文件 {path} 不存在"
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"成功读取文件 {path}，内容长度: {len(content)} 字符"
        except Exception as e:
            return f"读取文件失败: {str(e)}"
    
    def write_file(self, path, content):
        """写入文件工具"""
        try:
            # 显示文件写入预览
            self._show_file_write_preview(path, content)

            # 确保目录存在
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"成功写入文件 {path}"
        except Exception as e:
            return f"写入文件失败: {str(e)}"
    
    def create_file(self, path, content):
        """创建文件工具"""
        try:
            # 显示文件创建预览
            self._show_file_creation_preview(path, content)

            if os.path.exists(path):
                print(f"{Fore.YELLOW}⚠️ 警告：文件 {path} 已存在，将被覆盖{Style.RESET_ALL}")

            # 确保目录存在
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"成功创建文件 {path}"
        except Exception as e:
            return f"创建文件失败: {str(e)}"

    def insert_code(self, path, line_number, content):
        """插入代码工具"""
        try:
            if not os.path.exists(path):
                return f"错误：文件 {path} 不存在"

            # 读取文件内容
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 验证行号
            if line_number < 1 or line_number > len(lines) + 1:
                return f"错误：行号 {line_number} 超出文件范围 (1-{len(lines) + 1})"

            # 显示插入预览
            self._show_code_insertion_preview(path, line_number, content)

            # 插入新内容（行号从1开始，数组索引从0开始）
            insert_lines = content.split('\n')
            # 确保每行都有换行符（除了最后一行如果原本没有）
            insert_lines = [line + '\n' if not line.endswith('\n') else line for line in insert_lines]

            # 在指定位置插入
            lines[line_number - 1:line_number - 1] = insert_lines

            # 写回文件
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            return f"成功在 {path} 第{line_number}行插入 {len(insert_lines)} 行代码"
        except Exception as e:
            return f"插入代码失败: {str(e)}"

    def replace_code(self, path, start_line, end_line, content):
        """替换代码工具"""
        try:
            if not os.path.exists(path):
                return f"错误：文件 {path} 不存在"

            # 读取文件内容
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 验证行号范围
            if start_line < 1 or end_line < start_line or end_line > len(lines):
                return f"错误：行号范围 {start_line}-{end_line} 无效，文件共 {len(lines)} 行"

            # 获取被替换的原始代码
            original_lines = lines[start_line - 1:end_line]

            # 显示替换对比
            self._show_code_replacement_diff(path, start_line, end_line, original_lines, content)

            # 准备替换内容
            replace_lines = content.split('\n')
            # 确保每行都有换行符（除了最后一行如果原本没有）
            replace_lines = [line + '\n' if not line.endswith('\n') else line for line in replace_lines]

            # 替换指定范围的行（行号从1开始，数组索引从0开始）
            lines[start_line - 1:end_line] = replace_lines

            # 写回文件
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            replaced_count = end_line - start_line + 1
            return f"成功替换 {path} 第{start_line}-{end_line}行 ({replaced_count}行) 为 {len(replace_lines)} 行新代码"
        except Exception as e:
            return f"替换代码失败: {str(e)}"
    
    def execute_command(self, command):
        """执行命令工具"""
        try:
            # 安全检查 - 禁止危险命令
            dangerous_commands = ['rm -rf', 'del /f', 'format', 'fdisk', 'mkfs']
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                return "错误：禁止执行危险命令"
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'
            )
            
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            output = stdout + stderr
            return_code = result.returncode

            if return_code == 0:
                return f"命令执行成功:\n{output}" if output.strip() else "命令执行成功"
            else:
                return f"命令执行失败 (返回码: {return_code}):\n{output}"
                
        except subprocess.TimeoutExpired:
            return "命令执行超时"
        except Exception as e:
            return f"执行命令失败: {str(e)}"

    def add_todo(self, title: str, description: str = "", priority: str = "medium"):
        """添加TODO任务工具"""
        try:
            todo_id = todo_manager.add_todo(title, description, priority)
            return f"成功添加任务: {title} (ID: {todo_id[:8]})"
        except Exception as e:
            return f"添加任务失败: {str(e)}"

    def update_todo(self, todo_id: str, status: str, progress: int = 0):
        """更新TODO任务工具"""
        try:
            # 如果是短ID，尝试匹配完整ID
            if len(todo_id) == 8:
                full_id = None
                for tid in todo_manager.todos.keys():
                    if tid.startswith(todo_id):
                        full_id = tid
                        break
                if full_id:
                    todo_id = full_id
                else:
                    return f"未找到ID为 {todo_id} 的任务"

            success = todo_manager.update_todo(todo_id, status=status, progress=progress)
            if success:
                todo = todo_manager.get_todo(todo_id)
                return f"成功更新任务: {todo.title} -> {status} ({progress}%)"
            else:
                return f"更新任务失败: 任务不存在"
        except Exception as e:
            return f"更新任务失败: {str(e)}"

    def show_todos(self):
        """显示TODO列表工具"""
        try:
            return self.todo_renderer.render_todo_list()
        except Exception as e:
            return f"显示任务列表失败: {str(e)}"

    def task_complete(self, summary):
        """任务完成工具"""
        return f"任务已完成: {summary}"

    def _ask_user_confirmation(self, action_description):
        """询问用户确认"""
        while True:
            try:
                response = input(f"{Fore.YELLOW}是否执行 {action_description}? (Y/n): {Style.RESET_ALL}").strip().lower()
                if response in ['', 'y', 'yes', '是', 'ok']:
                    return True
                elif response in ['n', 'no', '否', 'cancel']:
                    return False
                else:
                    print(f"{Fore.RED}请输入 Y(是) 或 N(否){Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}操作已取消{Style.RESET_ALL}")
                return False

    def _execute_tool_with_matches(self, tool_name, matches):
        """执行工具并返回结果和显示文本"""
        if tool_name in ['write_file', 'create_file']:
            path, content = matches[0]
            tool_result = self.tools[tool_name](path.strip(), content.strip())
            action = "创建文件" if tool_name == 'create_file' else "写入文件"
            # 不再显示内容预览，因为工具内部已经显示了可视化预览
            display_text = f"{action} {path.strip()}"
        elif tool_name == 'insert_code':
            path, line, content = matches[0]
            tool_result = self.tools[tool_name](path.strip(), int(line.strip()), content.strip())
            # 不再显示详细内容，因为工具内部已经显示了可视化预览
            display_text = f"插入代码到 {path.strip()} 第{line.strip()}行"
        elif tool_name == 'replace_code':
            path, start_line, end_line, content = matches[0]
            tool_result = self.tools[tool_name](path.strip(), int(start_line.strip()), int(end_line.strip()), content.strip())
            # 不再显示详细内容，因为工具内部已经显示了可视化预览
            display_text = f"替换 {path.strip()} 第{start_line.strip()}-{end_line.strip()}行代码"
        elif tool_name == 'read_file':
            path = matches[0].strip()
            tool_result = self.tools[tool_name](path)
            display_text = f"读取文件 {path}"
        elif tool_name == 'execute_command':
            command = matches[0].strip()
            tool_result = self.tools[tool_name](command)
            display_text = f"执行命令: {command}"
        elif tool_name == 'add_todo':
            title, description, priority = matches[0]
            tool_result = self.tools[tool_name](title.strip(), description.strip(), priority.strip())
            display_text = f"添加任务: {title.strip()}"
        elif tool_name == 'update_todo':
            todo_id, status, progress = matches[0]
            tool_result = self.tools[tool_name](todo_id.strip(), status.strip(), int(progress.strip()) if progress.strip().isdigit() else 0)
            display_text = f"更新任务: {todo_id.strip()}"
        elif tool_name == 'show_todos':
            tool_result = self.tools[tool_name]()
            display_text = "显示任务列表"
        elif tool_name == 'task_complete':
            summary = matches[0].strip()
            tool_result = self.tools[tool_name](summary)
            display_text = f"任务完成: {summary}"
        else:
            tool_result = "未知工具"
            display_text = f"未知工具: {tool_name}"

        return tool_result, display_text

    def _is_command_real_failure(self, tool_result):
        """智能检测命令是否真正失败"""
        if not tool_result:
            return False

        result_lower = tool_result.lower()

        # 检查是否包含明确的失败标志
        failure_indicators = [
            'error:',
            'failed',
            'exception',
            'traceback',
            'could not',
            'cannot',
            'unable to',
            'permission denied',
            'access denied',
            'no such file',
            'not found',
            'invalid',
            'syntax error',
            'command not found',
            'no matching distribution found',  # pip特有错误
            'could not find a version',        # pip特有错误
            'is not recognized as an internal or external command',  # Windows命令不存在
            'not recognized',
            '找不到',
            '无法找到',
            '不是内部或外部命令'
        ]

        # 检查是否有真正的错误
        has_real_error = any(indicator in result_lower for indicator in failure_indicators)

        # 特殊处理：如果包含"命令执行失败"但同时有很多成功信息，需要更仔细分析
        if '命令执行失败' in result_lower:
            # 检查是否有严重错误（不仅仅是警告）
            serious_errors = [
                'could not find a version',
                'no matching distribution found',
                'error: could not',
                'fatal:',
                'critical:',
                'exception:',
                'traceback',
                'syntax error',
                'permission denied',
                'access denied'
            ]

            has_serious_error = any(error in result_lower for error in serious_errors)

            # 如果有严重错误，即使有成功信息也认为是失败
            if has_serious_error:
                return True

            # 如果只是pip升级提示等非关键信息，不认为是真正失败
            if 'requirement already satisfied' in result_lower and 'notice' in result_lower:
                # 检查错误是否只是包依赖问题
                dependency_errors = ['no matching distribution found', 'could not find a version']
                has_dependency_error = any(error in result_lower for error in dependency_errors)
                if has_dependency_error:
                    return True  # 依赖问题是真正的失败

        return has_real_error

    def _should_continue_based_on_context(self, tool_name, tool_result, ai_response):
        """基于上下文智能判断是否应该继续"""
        from .modes import mode_manager
        current_mode = mode_manager.get_current_mode()

        # Sprint模式：更积极的继续策略
        if current_mode == "sprint":
            # 明确的继续信号
            if any(keyword in ai_response.lower() for keyword in ['继续', 'continue', '接下来', '然后', '下一步']):
                return True

            # 检查是否有错误需要修复
            if tool_result and any(error_keyword in tool_result.lower() for error_keyword in
                                 ['失败', '错误', 'error', 'failed', '异常', 'exception', '返回码']):
                return True  # 有错误，让AI继续处理

            # 检查是否是创建/修改文件后需要测试
            if tool_name in ['create_file', 'write_file', 'insert_code', 'replace_code']:
                return True  # 创建/修改文件后应该继续测试

            # 检查是否是执行命令
            if tool_name == 'execute_command':
                # 智能检测命令是否真正失败
                is_real_failure = self._is_command_real_failure(tool_result)

                if is_real_failure:
                    return True  # 命令真正失败时必须继续，让AI分析和修复

                # 如果命令成功，检查是否需要继续
                if tool_result and '成功' in tool_result:
                    # 如果AI的响应中暗示还有后续步骤，继续
                    if any(keyword in ai_response.lower() for keyword in ['测试', 'test', '运行', 'run', '验证']):
                        return True

                return True  # 命令执行后默认继续，让AI决定下一步

            # 其他工具调用在sprint模式下默认继续
            return True

        # 其他模式：保守的继续策略
        else:
            # 明确的继续信号
            if any(keyword in ai_response.lower() for keyword in ['继续', 'continue', '接下来']):
                return True

            # 命令执行失败时必须继续，让AI有机会分析和建议解决方案
            if tool_name == 'execute_command' and self._is_command_real_failure(tool_result):
                return True

            # 其他工具有错误时也应该继续，让AI有机会解释或建议解决方案
            if tool_result and any(error_keyword in tool_result.lower() for error_keyword in
                                 ['失败', '错误', 'error', 'failed']):
                return True

            # 默认不继续，避免无限循环
            return False

    def _show_code_replacement_diff(self, path, start_line, end_line, original_lines, new_content):
        """显示代码替换的对比差异"""
        print(f"\n{Fore.CYAN}📝 代码替换预览: {path} (第{start_line}-{end_line}行){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        # 显示被删除的代码（红色）
        print(f"{Fore.RED}🗑️  删除的代码:{Style.RESET_ALL}")
        for i, line in enumerate(original_lines, start_line):
            clean_line = line.rstrip('\n\r')
            print(f"{Fore.RED}- {i:3d}: {clean_line}{Style.RESET_ALL}")

        print()  # 空行分隔

        # 显示新增的代码（绿色）
        print(f"{Fore.GREEN}✅ 新增的代码:{Style.RESET_ALL}")
        new_lines = new_content.split('\n')
        for i, line in enumerate(new_lines, start_line):
            print(f"{Fore.GREEN}+ {i:3d}: {line}{Style.RESET_ALL}")

        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

    def _show_file_creation_preview(self, path, content):
        """显示文件创建预览"""
        print(f"\n{Fore.CYAN}📄 创建文件: {path}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        # 显示文件内容预览（前10行）
        lines = content.split('\n')
        preview_lines = min(10, len(lines))

        print(f"{Fore.GREEN}✅ 文件内容 (前{preview_lines}行):{Style.RESET_ALL}")
        for i, line in enumerate(lines[:preview_lines], 1):
            print(f"{Fore.GREEN}+ {i:3d}: {line}{Style.RESET_ALL}")

        if len(lines) > preview_lines:
            remaining = len(lines) - preview_lines
            print(f"{Fore.LIGHTBLACK_EX}... 还有 {remaining} 行内容{Style.RESET_ALL}")

        print(f"{Fore.CYAN}📊 文件统计: {len(lines)} 行, {len(content)} 字符{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

    def _show_file_write_preview(self, path, content):
        """显示文件写入预览"""
        print(f"\n{Fore.CYAN}📝 写入文件: {path}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        # 如果文件存在，显示原内容
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    original_content = f.read()

                original_lines = original_content.split('\n')
                print(f"{Fore.RED}🗑️  原文件内容 (前5行):{Style.RESET_ALL}")
                for i, line in enumerate(original_lines[:5], 1):
                    print(f"{Fore.RED}- {i:3d}: {line}{Style.RESET_ALL}")

                if len(original_lines) > 5:
                    print(f"{Fore.RED}... 原文件共 {len(original_lines)} 行{Style.RESET_ALL}")

                print()  # 空行分隔
            except:
                print(f"{Fore.YELLOW}⚠️ 无法读取原文件内容{Style.RESET_ALL}")

        # 显示新内容
        lines = content.split('\n')
        preview_lines = min(10, len(lines))

        print(f"{Fore.GREEN}✅ 新文件内容 (前{preview_lines}行):{Style.RESET_ALL}")
        for i, line in enumerate(lines[:preview_lines], 1):
            print(f"{Fore.GREEN}+ {i:3d}: {line}{Style.RESET_ALL}")

        if len(lines) > preview_lines:
            remaining = len(lines) - preview_lines
            print(f"{Fore.LIGHTBLACK_EX}... 还有 {remaining} 行内容{Style.RESET_ALL}")

        print(f"{Fore.CYAN}📊 新文件统计: {len(lines)} 行, {len(content)} 字符{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

    def _show_code_insertion_preview(self, path, line_number, content):
        """显示代码插入的预览"""
        print(f"\n{Fore.CYAN}📝 代码插入预览: {path} (第{line_number}行后){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        # 显示插入位置的上下文
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 显示插入位置前后的代码
            context_start = max(1, line_number - 2)
            context_end = min(len(lines), line_number + 2)

            print(f"{Fore.LIGHTBLACK_EX}📍 插入位置上下文:{Style.RESET_ALL}")
            for i in range(context_start, line_number + 1):
                if i <= len(lines):
                    clean_line = lines[i-1].rstrip('\n\r')
                    print(f"{Fore.LIGHTBLACK_EX}  {i:3d}: {clean_line}{Style.RESET_ALL}")

            print()  # 空行分隔

            # 显示要插入的代码（绿色）
            print(f"{Fore.GREEN}✅ 插入的代码:{Style.RESET_ALL}")
            insert_lines = content.split('\n')
            for i, line in enumerate(insert_lines):
                print(f"{Fore.GREEN}+ {line_number + i + 1:3d}: {line}{Style.RESET_ALL}")

            print()  # 空行分隔

            # 显示插入位置后的代码
            print(f"{Fore.LIGHTBLACK_EX}📍 插入后的上下文:{Style.RESET_ALL}")
            for i in range(line_number + 1, context_end + 1):
                if i <= len(lines):
                    clean_line = lines[i-1].rstrip('\n\r')
                    print(f"{Fore.LIGHTBLACK_EX}  {i + len(insert_lines):3d}: {clean_line}{Style.RESET_ALL}")

        except Exception:
            # 如果无法读取上下文，只显示插入的代码
            print(f"{Fore.GREEN}✅ 插入的代码:{Style.RESET_ALL}")
            insert_lines = content.split('\n')
            for i, line in enumerate(insert_lines):
                print(f"{Fore.GREEN}+ {line_number + i + 1:3d}: {line}{Style.RESET_ALL}")

        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

    def _get_file_lines(self, path, start_line, end_line):
        """获取文件指定行范围的内容"""
        try:
            if not os.path.exists(path):
                return None

            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if start_line < 1 or end_line > len(lines) or start_line > end_line:
                return None

            # 返回指定范围的行（去掉换行符）
            return [line.rstrip('\n\r') for line in lines[start_line - 1:end_line]]
        except Exception:
            return None

# 全局工具处理器实例
ai_tool_processor = AIToolProcessor()
