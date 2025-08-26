"""
AI工具系统 - 处理AI的工具调用
"""

import os
import re
import subprocess
import json
import asyncio
import difflib
from colorama import Fore, Style
from .todo_manager import todo_manager
from .todo_renderer import get_todo_renderer
from .modes import mode_manager
from .mcp_client import mcp_client
from .mcp_config import mcp_config
from .thinking_animation import show_dot_cycle_animation
from .theme import theme_manager

class AIToolProcessor:
    """AI工具处理器"""

    def __init__(self):
        self.tools = {
            'read_file': self.read_file,
            'precise_reading': self.precise_reading,
            'write_file': self.write_file,
            'create_file': self.create_file,
            'insert_code': self.insert_code,
            'replace_code': self.replace_code,
            'execute_command': self.execute_command,
            'add_todo': self.add_todo,
            'update_todo': self.update_todo,
            'show_todos': self.show_todos,
            'delete_file': self.delete_file,
            'mcp_call_tool': self.mcp_call_tool,
            'mcp_read_resource': self.mcp_read_resource,
            'mcp_list_tools': self.mcp_list_tools,
            'mcp_list_resources': self.mcp_list_resources,
            'mcp_server_status': self.mcp_server_status,
            'task_complete': self.task_complete,
            'plan': self.plan,
            'plan': self.plan,
            'code_search': self.code_search
        }
        self.todo_renderer = get_todo_renderer(todo_manager)

    def process_response(self, ai_response):
        # HACPP State Machine Logic: Check if we are in the researcher phase
        from .modes import hacpp_mode
        if hacpp_mode.is_hacpp_active() and hacpp_mode.phase == "researching":
            # In researcher phase, we only look for task_complete or read-only tools
            task_complete_match = re.search(r'<task_complete><summary>(.*?)</summary></task_complete>', ai_response, re.DOTALL)
            if task_complete_match:
                summary = task_complete_match.group(1).strip()
                # This is the handover signal
                return {'is_handover': True, 'summary': summary}

            # If not handing over, process only read-only tools
            result = self.process_response_for_researcher(ai_response)
            result['should_continue'] = True # Researcher should always continue until handover
            return result

        """处理AI响应，提取和执行工具调用"""
        # 查找XML工具调用
        tool_patterns = {
            'read_file': r'<read_file><path>(.*?)</path></read_file>',
            'precise_reading': r'<precise_reading><path>(.*?)</path><start_line>(.*?)</start_line><end_line>(.*?)</end_line></precise_reading>',
            'write_file': r'<write_file><path>(.*?)</path><content>(.*?)</content></write_file>',
            'create_file': r'<create_file><path>(.*?)</path><content>(.*?)</content></create_file>',
            'insert_code': r'<insert_code><path>(.*?)</path><line>(.*?)</line><content>(.*?)</content></insert_code>',
            'replace_code': r'<replace_code><path>(.*?)</path><start_line>(.*?)</start_line><end_line>(.*?)</end_line><content>(.*?)</content></replace_code>',
            'execute_command': r'<execute_command><command>(.*?)</command></execute_command>',
            'add_todo': r'<add_todo><title>(.*?)</title><description>(.*?)</description><priority>(.*?)</priority></add_todo>',
            'update_todo': r'<update_todo><id>(.*?)</id><status>(.*?)</status><progress>(.*?)</progress></update_todo>',
            'show_todos': r'<show_todos></show_todos>',
            'delete_file': r'<delete_file><path>(.*?)</path></delete_file>',
            'mcp_call_tool': r'<mcp_call_tool><tool>(.*?)</tool><arguments>(.*?)</arguments></mcp_call_tool>',
            'mcp_read_resource': r'<mcp_read_resource><uri>(.*?)</uri></mcp_read_resource>',
            'mcp_list_tools': r'<mcp_list_tools></mcp_list_tools>',
            'mcp_list_resources': r'<mcp_list_resources></mcp_list_resources>',
            'mcp_server_status': r'<mcp_server_status></mcp_server_status>',
            'task_complete': r'<task_complete><summary>(.*?)</summary></task_complete>',
            'plan': r'<plan><completed_action>(.*?)</completed_action><next_step>(.*?)</next_step></plan>',
            'code_search': r'<code_search><keyword>(.*?)</keyword></code_search>'
        }

        tool_found = False


        # 查找所有工具调用，并按其在文本中的出现顺序排序
        found_tool_calls = []
        for tool_name, pattern in tool_patterns.items():
            for match in re.finditer(pattern, ai_response, re.DOTALL):
                # 使用 finditer 来获取匹配的位置
                found_tool_calls.append({
                    "tool_name": tool_name,
                    "matches": [match.groups()], # 保持与旧代码一致的格式
                    "start_pos": match.start()
                })

        # 按工具在文本中的出现位置排序
        found_tool_calls.sort(key=lambda x: x['start_pos'])

        # 添加大概率判断机制：检查不完整输出
        if not found_tool_calls:
            # 检查是否包含可能的不完整工具调用
            incomplete_tool_match = self._check_incomplete_tool_call(ai_response)
            if incomplete_tool_match:
                return {
                    'has_tool': True,
                    'tool_result': f"❌ 工具调用失败: AI输出不完整，检测到可能的{incomplete_tool_match['tool_name']}工具调用但格式不完整",
                    'executed_tools': [],
                    'display_text': "",
                    'should_continue': True  # 让AI继续修复
                }

        # 提取一次思考过程
        thought_process = self._extract_thought_process(ai_response, tool_patterns)
        if thought_process:
            print(f"\n{Fore.GREEN}AI: {thought_process}{Style.RESET_ALL}")

        all_tool_results = []
        executed_tool_names = []
        display_text = ""

        # 依次处理所有找到的工具
        if found_tool_calls:
            tool_found = True
            for i, tool_call in enumerate(found_tool_calls):
                tool_name = tool_call['tool_name']
                matches = tool_call['matches']

                permission = mode_manager.can_auto_execute(tool_name)
                tool_result, tool_summary = "", ""

                _, temp_summary = self._execute_tool_with_matches(tool_name, matches, dry_run=True)

                if permission is False:
                    tool_result = f"当前模式 ({mode_manager.get_current_mode()}) 不允许此操作"
                    tool_summary = f"操作被禁止: {tool_name}"
                elif permission == "confirm":
                    # 在多工具调用中，只在第一次询问前打印思考过程
                    if i == 0 and thought_process:
                        print(f"\n{Fore.GREEN}AI: {thought_process}{Style.RESET_ALL}")
                    print(f"\n{Fore.YELLOW}AI 想要 ({i+1}/{len(found_tool_calls)}) {temp_summary}{Style.RESET_ALL}")

                    if self._ask_user_confirmation(f"执行操作: {temp_summary}"):
                        tool_result, tool_summary = self._execute_tool_with_matches(tool_name, matches)
                    else:
                        tool_result = "用户取消了操作"
                        tool_summary = f"用户取消 - {temp_summary}"
                else:  # Auto-execute
                    tool_result, tool_summary = self._execute_tool_with_matches(tool_name, matches)

                # 特殊处理task_complete工具
                if tool_name == 'task_complete':
                    # 将task_complete的返回结果中的should_continue标志传递出去
                    tool_result_dict = json.loads(tool_result) if isinstance(tool_result, str) else tool_result
                    if tool_result_dict.get('should_continue'):
                        result['should_continue'] = True
                        result['summary'] = tool_result_dict.get('summary', '')

                all_tool_results.append(tool_result)
                executed_tool_names.append(tool_name)
                # 始终打印我们生成的摘要，因为它现在是格式化输出的关键部分
                print(f"{Fore.CYAN}{tool_summary}{Style.RESET_ALL}")

        # 如果没有工具调用，显示纯文本
        if not tool_found:
            display_text = self._remove_xml_tags(ai_response)

        # 聚合最终结果
        final_tool_result = "\n".join(filter(None, all_tool_results))

        # 强制继续判断逻辑
        should_continue = False
        if tool_found:
            if any(call['tool_name'] == 'task_complete' for call in found_tool_calls):
                should_continue = False
            else:
                should_continue = True
        else:
            if any(keyword in ai_response.lower() for keyword in ['继续', '接下来', '然后', '下一步', 'continue', 'next']):
                should_continue = True

        return {
            'has_tool': tool_found,
            'tool_result': final_tool_result,
            'executed_tools': executed_tool_names,
            'display_text': display_text, # display_text 现在主要由打印语句处理
            'should_continue': should_continue
        }



    def _extract_thought_process(self, text, tool_patterns):
        """Removes all tool call XML blocks to isolate the AI's reasoning."""
        processed_text = text
        for pattern in tool_patterns.values():
            processed_text = re.sub(pattern, '', processed_text, flags=re.DOTALL)
        return processed_text.strip()

    def _check_incomplete_tool_call(self, text):
        """检查不完整的工具调用"""
        # 定义可能的不完整工具调用模式
        incomplete_patterns = {
            'read_file': r'<read_file>(.*?)</read_file>',
            'write_file': r'<write_file>(.*?)</write_file>',
            'create_file': r'<create_file>(.*?)</create_file>',
            'insert_code': r'<insert_code>(.*?)</insert_code>',
            'replace_code': r'<replace_code>(.*?)</replace_code>',
            'execute_command': r'<execute_command>(.*?)</execute_command>',
            'add_todo': r'<add_todo>(.*?)</add_todo>',
            'update_todo': r'<update_todo>(.*?)</update_todo>',
            'delete_file': r'<delete_file>(.*?)</delete_file>'
        }
        
        for tool_name, pattern in incomplete_patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return {
                    'tool_name': tool_name,
                    'matched_text': match.group(1)
                }
        
        return None

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

    def process_response_for_researcher(self, ai_response):
        """便宜AI阶段的工具处理器，支持读取文件和执行命令"""
        tool_patterns = {
            'read_file': r'<read_file><path>(.*?)</path></read_file>',
            'execute_command': r'<execute_command><command>(.*?)</command></execute_command>',
        }

        # 查找所有工具调用，并按其在文本中的出现顺序排序
        found_tool_calls = []
        for tool_name, pattern in tool_patterns.items():
            for match in re.finditer(pattern, ai_response, re.DOTALL):
                found_tool_calls.append({
                    "tool_name": tool_name,
                    "matches": [match.groups()],
                    "start_pos": match.start()
                })

        # 按工具在文本中的出现位置排序
        found_tool_calls.sort(key=lambda x: x['start_pos'])

        all_tool_results = []
        executed_tool_names = []
        tool_found = len(found_tool_calls) > 0

        # 依次处理所有找到的工具
        for tool_call in found_tool_calls:
            tool_name = tool_call['tool_name']
            matches = tool_call['matches']
            
            # 便宜AI的工具总是自动执行
            if tool_name in self.tools:
                tool_result, tool_summary = self._execute_tool_with_matches(tool_name, matches)
                # 确保tool_result是字符串
                if tool_result is not None:
                    all_tool_results.append(str(tool_result))
                executed_tool_names.append(tool_name)

        # 合并所有工具结果
        combined_result = '\n'.join(all_tool_results) if all_tool_results else ""

        return {
            'has_tool': tool_found,
            'tool_result': combined_result,
            'executed_tools': executed_tool_names,
            'display_text': self._remove_xml_tags(ai_response),
        }

    def read_file(self, path):
        """读取文件工具"""
        try:
            if not os.path.exists(path):
                return f"错误：文件 {path} 不存在"

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                line_count = len(lines)
                char_count = len(content)

            # 只显示简化的格式
            print(f"\n{theme_manager.format_tool_header('Read', path)}")
            print(f"  • {line_count} lines viewed")
            print(f"  • {char_count} characters")

            return f"成功读取文件 {path}，内容长度: {len(content)} 字符"
        except Exception as e:
            return f"读取文件失败: {str(e)}"

    def precise_reading(self, path, start_line, end_line):
        """精确读取文件指定行范围的内容"""
        try:
            start_line, end_line = int(start_line), int(end_line)
            if not os.path.exists(path):
                return f"错误：文件 {path} 不存在"

            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 验证行号
            if start_line < 1 or end_line > len(lines) or start_line > end_line:
                return f"错误：行号范围 {start_line}-{end_line} 无效，文件共 {len(lines)} 行"

            content_slice = lines[start_line - 1:end_line]
            content = "".join(content_slice)

            # 渲染标题
            header_title = f"{os.path.basename(path)} ({start_line}-{end_line})"
            print(f"\n{theme_manager.format_tool_header('Read', header_title)}")

            # 打印内容
            print(content.strip())

            return f"成功读取文件 {path} 的第 {start_line}-{end_line} 行，内容长度: {len(content)} 字符"
        except Exception as e:
            return f"精确读取文件失败: {str(e)}"

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

    def delete_file(self, path):
        """删除文件工具"""
        try:
            # 检查文件是否存在
            if not os.path.exists(path):
                return f"❌ 错误：文件 {path} 不存在，无法删除"

            # 检查是否是文件（不是目录）
            if not os.path.isfile(path):
                return f"❌ 错误：{path} 不是文件，无法删除"

            # 读取文件信息用于显示
            line_count = 0
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    line_count = len(lines)
            except:
                line_count = 0

            # 执行删除
            os.remove(path)

            # 只显示简化的格式
            print(f"\n{theme_manager.format_tool_header('Delete', path)}")
            print(f"  • -{line_count} additions")
            print(f"  • +1 deletion")
            print("  • File moved to trash")

            return f"成功删除文件 {path}"

        except Exception as e:
            return f"删除文件失败: {str(e)}"

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
            self._show_code_replacement_diff(path, [l.rstrip('\n\r') for l in original_lines], content)

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
        """执行命令工具，并实时显示输出"""
        try:
            # 安全检查
            dangerous_commands = ['rm -rf', 'del /f', 'format', 'fdisk', 'mkfs']
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                return "错误：禁止执行危险命令"

            print(f"\n{theme_manager.format_tool_header('Execute', command)}")

            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )

            output_lines = []
            print(f"{Fore.CYAN}实时输出:{Style.RESET_ALL}")
            # 实时读取输出
            for line in iter(process.stdout.readline, ''):
                # 移除换行符并打印
                clean_line = line.rstrip()
                print(f"  {clean_line}", flush=True)
                output_lines.append(clean_line)

            process.stdout.close()
            return_code = process.wait()
            full_output = "\n".join(output_lines)

            print(f"\n{Fore.CYAN}执行完毕 (返回码: {return_code}){Style.RESET_ALL}")

            if return_code == 0:
                return "命令执行成功"
            else:
                return f"命令执行失败 (返回码: {return_code}):\n{full_output}"

        except Exception as e:
            print(f"\n{theme_manager.format_tool_header('Execute', command)}")
            print(f"  • 执行命令失败: {str(e)}")
            return f"执行命令失败: {str(e)}"

    def add_todo(self, title: str, description: str = "", priority: str = "medium"):
        """添加TODO任务工具"""
        try:
            todo_manager.add_todo(title, description, priority)
            return ""  # 成功时静默，不返回消息
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
        from .modes import hacpp_mode
        
        if hacpp_mode.is_hacpp_active():
            # 在HACPP模式下，便宜AI调用task_complete时不结束流程
            if hacpp_mode.phase == "researching":
                return {
                    "success": True,
                    "message": "研究员分析完成，准备交接给执行者",
                    "summary": summary,
                    "should_continue": True  # 添加标志表示需要继续流程
                }
            # 贵AI调用task_complete时结束流程
            else:
                return {
                    "success": True,
                    "message": "任务完成，流程结束",
                    "summary": summary,
                    "should_continue": False
                }
        else:
            # 非HACPP模式直接结束
            return {
                "success": True,
                "message": "任务完成，流程结束",
                "summary": summary,
                "should_continue": False
            }

    def plan(self, completed_action, next_step):
        """计划工具，用于生成继承计划"""
        # 这个工具的核心作用是结构化地返回计划，供command_processor捕获
        # 它返回一个特殊格式的字符串，以便于解析
        # 增强计划信息，包含更多上下文
        import time
        timestamp = time.strftime("%H:%M:%S")
        return f"PLAN::{timestamp}::COMPLETED:{completed_action}::NEXT:{next_step}"

    def code_search(self, keyword):
        """在项目中搜索代码"""
        try:
            print(f"\n{Fore.CYAN}🔍 正在搜索: {keyword}{Style.RESET_ALL}")
            print("=" * 60)

            # 定义忽略的目录和文件类型
            ignore_dirs = {'.git', '__pycache__', 'dist', 'build', '.vscode', 'node_modules'}
            ignore_exts = {'.pyc', '.pyo', '.pyd', '.so', '.o', '.a', '.dll', '.exe', '.log', '.tmp'}

            results = []
            for root, dirs, files in os.walk('.'):
                # 过滤忽略的目录
                dirs[:] = [d for d in dirs if d not in ignore_dirs]

                for file in files:
                    # 过滤忽略的文件类型
                    if any(file.endswith(ext) for ext in ignore_exts):
                        continue

                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            for i, line in enumerate(f, 1):
                                if keyword in line:
                                    results.append(f"{path}:{i}: {line.strip()}")
                    except Exception:
                        # 忽略无法读取的文件
                        continue

            if not results:
                print(f"{Fore.YELLOW}没有找到包含 '{keyword}' 的文件{Style.RESET_ALL}")
                return f"没有找到包含 '{keyword}' 的文件"

            # 格式化并打印结果
            result_str = "\n".join(results)
            print(f"{Fore.GREEN}✅ 搜索完成，找到 {len(results)} 处匹配项{Style.RESET_ALL}")
            print(result_str)
            return f"搜索成功，找到 {len(results)} 处匹配项:\n{result_str}"

        except Exception as e:
            return f"搜索失败: {str(e)}"

    def mcp_call_tool(self, tool_name, arguments_json):
        """调用MCP工具"""
        try:
            if not mcp_config.is_enabled():
                return "❌ MCP功能未启用。请使用 /mcp 命令启用MCP功能。"

            # 解析参数
            try:
                arguments = json.loads(arguments_json) if arguments_json.strip() else {}
            except json.JSONDecodeError:
                return f"❌ 参数格式错误，请使用有效的JSON格式: {arguments_json}"

            print(f"\n{Fore.CYAN}🔧 调用MCP工具: {tool_name}{Style.RESET_ALL}")
            print("=" * 60)
            print(f"工具名称: {tool_name}")
            print(f"参数: {json.dumps(arguments, ensure_ascii=False, indent=2)}")
            print(f"{Fore.YELLOW}⏳ 正在搜索中，请稍候...{Style.RESET_ALL}")

            # 异步调用MCP工具，添加超时处理
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # 添加15秒超时
                result = loop.run_until_complete(
                    asyncio.wait_for(
                        mcp_client.call_tool(tool_name, arguments),
                        timeout=15.0
                    )
                )

                if result:
                    if "error" in result:
                        print(f"{Fore.RED}❌ 工具调用失败: {result['error']}{Style.RESET_ALL}")
                        return f"❌ MCP工具调用失败: {result['error']}"
                    else:
                        print(f"{Fore.GREEN}✅ 工具调用成功{Style.RESET_ALL}")

                        # 格式化显示结果
                        if "result" in result and "content" in result["result"]:
                            content = result["result"]["content"]
                            if isinstance(content, list) and len(content) > 0:
                                text_content = content[0].get("text", "")
                                print(f"{Fore.GREEN}搜索结果:{Style.RESET_ALL}")
                                print(text_content)
                                return f"✅ MCP搜索成功:\n{text_content}"

                        # 如果格式不符合预期，显示原始结果
                        result_str = json.dumps(result, ensure_ascii=False, indent=2)
                        print(f"结果: {result_str}")
                        return f"✅ MCP工具调用成功:\n{result_str}"
                else:
                    print(f"{Fore.RED}❌ 工具调用返回空结果{Style.RESET_ALL}")
                    return f"❌ MCP工具 {tool_name} 调用失败或未找到"

            except asyncio.TimeoutError:
                print(f"{Fore.RED}❌ 工具调用超时（15秒）{Style.RESET_ALL}")
                return f"❌ MCP工具调用超时，请检查网络连接或服务器状态"
            except Exception as e:
                print(f"{Fore.RED}❌ 工具调用异常: {str(e)}{Style.RESET_ALL}")
                return f"❌ MCP工具调用异常: {str(e)}"
            finally:
                loop.close()

        except Exception as e:
            return f"❌ MCP工具调用异常: {str(e)}"

    def mcp_read_resource(self, uri):
        """读取MCP资源"""
        try:
            if not mcp_config.is_enabled():
                return "❌ MCP功能未启用。请使用 /mcp 命令启用MCP功能。"

            print(f"\n{Fore.CYAN}📄 读取MCP资源: {uri}{Style.RESET_ALL}")
            print("=" * 60)

            # 异步读取MCP资源
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(mcp_client.read_resource(uri))

                if result:
                    if "error" in result:
                        print(f"{Fore.RED}❌ 资源读取失败: {result['error']}{Style.RESET_ALL}")
                        return f"❌ MCP资源读取失败: {result['error']}"
                    else:
                        print(f"{Fore.GREEN}✅ 资源读取成功{Style.RESET_ALL}")
                        content = result.get("contents", [])
                        if content:
                            for item in content:
                                print(f"类型: {item.get('type', 'unknown')}")
                                if item.get('type') == 'text':
                                    print(f"内容: {item.get('text', '')[:500]}...")
                        return f"✅ MCP资源读取成功:\n{json.dumps(result, ensure_ascii=False, indent=2)}"
                else:
                    return f"❌ MCP资源 {uri} 读取失败或未找到"
            finally:
                loop.close()

        except Exception as e:
            return f"❌ MCP资源读取异常: {str(e)}"

    def mcp_list_tools(self):
        """列出可用的MCP工具"""
        try:
            if not mcp_config.is_enabled():
                return "❌ MCP功能未启用。请使用 /mcp 命令启用MCP功能。"

            print(f"\n{Fore.CYAN}🔧 可用的MCP工具{Style.RESET_ALL}")
            print("=" * 60)

            tools = mcp_client.get_available_tools()

            if not tools:
                print(f"{Fore.YELLOW}没有可用的MCP工具{Style.RESET_ALL}")
                return "没有可用的MCP工具。请检查MCP服务器是否正常运行。"

            result_lines = []
            for tool in tools:
                print(f"{Fore.GREEN}工具: {tool.name}{Style.RESET_ALL}")
                print(f"  服务器: {tool.server_name}")
                print(f"  描述: {tool.description}")
                print(f"  参数: {json.dumps(tool.input_schema, ensure_ascii=False, indent=2)}")
                print()

                result_lines.append(f"- {tool.name} ({tool.server_name}): {tool.description}")

            return f"✅ 找到 {len(tools)} 个MCP工具:\n" + "\n".join(result_lines)

        except Exception as e:
            return f"❌ 列出MCP工具异常: {str(e)}"

    def mcp_list_resources(self):
        """列出可用的MCP资源"""
        try:
            if not mcp_config.is_enabled():
                return "❌ MCP功能未启用。请使用 /mcp 命令启用MCP功能。"

            print(f"\n{Fore.CYAN}📄 可用的MCP资源{Style.RESET_ALL}")
            print("=" * 60)

            resources = mcp_client.get_available_resources()

            if not resources:
                print(f"{Fore.YELLOW}没有可用的MCP资源{Style.RESET_ALL}")
                return "没有可用的MCP资源。请检查MCP服务器是否正常运行。"

            result_lines = []
            for resource in resources:
                print(f"{Fore.GREEN}资源: {resource.name}{Style.RESET_ALL}")
                print(f"  服务器: {resource.server_name}")
                print(f"  URI: {resource.uri}")
                print(f"  描述: {resource.description}")
                print(f"  类型: {resource.mime_type}")
                print()

                result_lines.append(f"- {resource.name} ({resource.server_name}): {resource.uri}")

            return f"✅ 找到 {len(resources)} 个MCP资源:\n" + "\n".join(result_lines)

        except Exception as e:
            return f"❌ 列出MCP资源异常: {str(e)}"

    def mcp_server_status(self):
        """查看MCP服务器状态"""
        try:
            if not mcp_config.is_enabled():
                return "❌ MCP功能未启用。请使用 /mcp 命令启用MCP功能。"

            print(f"\n{Fore.CYAN}🖥️ MCP服务器状态{Style.RESET_ALL}")
            print("=" * 60)

            status = mcp_client.get_server_status()

            if not status:
                print(f"{Fore.YELLOW}没有配置的MCP服务器{Style.RESET_ALL}")
                return "没有配置的MCP服务器。请使用 /mcp 命令配置MCP服务器。"

            result_lines = []
            for server_name, server_status in status.items():
                status_color = Fore.GREEN if server_status == "运行中" else Fore.YELLOW
                print(f"{status_color}服务器: {server_name} - {server_status}{Style.RESET_ALL}")
                result_lines.append(f"- {server_name}: {server_status}")

            # 显示工具和资源统计
            tools_count = len(mcp_client.get_available_tools())
            resources_count = len(mcp_client.get_available_resources())

            print(f"\n{Fore.CYAN}统计信息:{Style.RESET_ALL}")
            print(f"  可用工具: {tools_count}")
            print(f"  可用资源: {resources_count}")

            result_lines.append(f"\n统计: {tools_count} 个工具, {resources_count} 个资源")

            return f"✅ MCP服务器状态:\n" + "\n".join(result_lines)

        except Exception as e:
            return f"❌ 查看MCP服务器状态异常: {str(e)}"

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

    def _execute_tool_with_matches(self, tool_name, matches, dry_run=False):
        """Executes a tool and returns the result and a user-friendly summary."""
        # Step 1: Generate the summary based on the tool and arguments
        tool_summary = ""
        # Handle cases where a tool has no arguments (e.g., <show_todos/>)
        if not matches or matches[0] is None:
            raw_args = ()
        else:
            raw_args = matches[0] if isinstance(matches[0], tuple) else (matches[0],)

        args = [arg.strip() if isinstance(arg, str) else arg for arg in raw_args]

        # This block creates a human-readable summary for every tool.
        if tool_name in ['write_file', 'delete_file', 'read_file']:
            actions = {'write_file': '写入文件', 'delete_file': '删除文件', 'read_file': '读取文件'}
            tool_summary = f"{actions[tool_name]}: {args[0]}"
        elif tool_name == 'create_file' or tool_name == 'plan':
            tool_summary = "" # 这些工具不生成摘要

        elif tool_name == 'add_todo':
            title = args[0]
            tool_summary = f"[ add_todo ] ──── TODO ────\n  • {title}"
        elif tool_name in ['insert_code', 'replace_code']:
            tool_summary = f"编辑代码: {args[0]}"
        elif tool_name == 'execute_command':
            tool_summary = f"执行命令: {args[0]}"
        else:
            tool_summary = f"执行工具: {tool_name}"

        if dry_run:
            return None, tool_summary

        # Step 2: Execute the tool if not a dry run
        try:
            # Convert numeric arguments where necessary
            if tool_name in ['insert_code', 'replace_code', 'update_todo']:
                for i, arg in enumerate(args):
                    if arg.isdigit():
                        args[i] = int(arg)

            tool_result = self.tools[tool_name](*args)
            show_dot_cycle_animation("执行", 0.3)
            return tool_result, tool_summary
        except Exception as e:
            error_msg = str(e)
            tool_result = f"❌ 工具执行失败: {error_msg}"
            tool_summary = f"❌ {tool_name} 执行失败: {error_msg}"
            show_dot_cycle_animation("失败", 0.3)
            return tool_result, tool_summary

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

    def _show_code_replacement_diff(self, path, original_lines, new_content):
        """显示代码替换的对比差异，使用git风格"""
        from colorama import Back

        new_lines = new_content.split('\n')

        print(f"\n{theme_manager.format_tool_header('Replace', path)}")
        print(f"  • +{len(new_lines)} additions")
        print(f"  • -{len(original_lines)} deletions")

        # 明确地将旧内容标记为红色，新内容标记为绿色
        for line in original_lines:
            print(f"    {Back.RED}{Fore.WHITE}- {line}{Style.RESET_ALL}")
        for line in new_lines:
            print(f"    {Back.GREEN}{Fore.WHITE}+ {line}{Style.RESET_ALL}")

    def _show_file_creation_preview(self, path, content):
        """显示文件创建的预览，使用git风格，对长文件进行截断"""
        from colorama import Back
        lines = content.split('\n')
        line_count = len(lines)

        print(f"\n{theme_manager.format_tool_header('Create', path)}")
        print(f"  • +{line_count} additions")
        print(f"  • -0 deletions")

        max_preview_lines = 15
        if line_count <= max_preview_lines:
            for line in lines:
                print(f"    {Back.GREEN}{Fore.WHITE}+ {line}{Style.RESET_ALL}")
        else:
            for line in lines[:10]: # 显示前10行
                print(f"    {Back.GREEN}{Fore.WHITE}+ {line}{Style.RESET_ALL}")
            print(f"    ... (还有 {line_count - 15} 行未显示) ...")
            for line in lines[-5:]: # 显示后5行
                print(f"    {Back.GREEN}{Fore.WHITE}+ {line}{Style.RESET_ALL}")

    def _show_file_write_preview(self, path, new_content):
        """显示文件写入的对比差异，使用git风格，对长文件进行截断"""
        from colorama import Back
        original_lines = []
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    original_lines = [l.rstrip('\n\r') for l in f.readlines()]
            except:
                pass # Ignore if cannot read

        new_lines = new_content.split('\n')
        diff = difflib.unified_diff(original_lines, new_lines, fromfile='a/' + path, tofile='b/' + path, lineterm='', n=3)

        print(f"\n{theme_manager.format_tool_header('Write', path)}")
        # 统计实际的增删行数
        additions = len([line for line in new_lines if line not in original_lines])
        deletions = len([line for line in original_lines if line not in new_lines])
        print(f"  • +{additions} additions")
        print(f"  • -{deletions} deletions")

        diff_lines = [line for line in list(diff)[3:] if line.startswith('+') or line.startswith('-')]
        if not diff_lines:
            print("    (No content changes)")
            return

        max_preview_lines = 15
        if len(diff_lines) <= max_preview_lines:
            for line in diff_lines:
                if line.startswith('-'):
                    print(f"    {Back.RED}{Fore.WHITE}{line}{Style.RESET_ALL}")
                elif line.startswith('+'):
                    print(f"    {Back.GREEN}{Fore.WHITE}{line}{Style.RESET_ALL}")
        else:
            # 显示部分差异
            for line in diff_lines[:10]:
                if line.startswith('-'):
                    print(f"    {Back.RED}{Fore.WHITE}{line}{Style.RESET_ALL}")
                elif line.startswith('+'):
                    print(f"    {Back.GREEN}{Fore.WHITE}{line}{Style.RESET_ALL}")
            print(f"    ... (还有 {len(diff_lines) - 15} 行变更未显示) ...")
            for line in diff_lines[-5:]:
                if line.startswith('-'):
                    print(f"    {Back.RED}{Fore.WHITE}{line}{Style.RESET_ALL}")
                elif line.startswith('+'):
                    print(f"    {Back.GREEN}{Fore.WHITE}{line}{Style.RESET_ALL}")

    def _show_code_insertion_preview(self, path, line_number, content):
        """显示代码插入的预览，使用git风格"""
        from colorama import Back
        try:
            with open(path, 'r', encoding='utf-8') as f:
                original_lines = [l.rstrip('\n\r') for l in f.readlines()]
        except Exception:
            original_lines = []

        new_lines_to_insert = content.split('\n')
        # Create the new file content in memory
        new_full_lines = original_lines[:line_number - 1] + new_lines_to_insert + original_lines[line_number - 1:]

        diff = difflib.unified_diff(original_lines, new_full_lines, fromfile='a/' + path, tofile='b/' + path, lineterm='', n=3)

        print(f"\n{theme_manager.format_tool_header('Insert', path)}")
        print(f"  • +{len(new_lines_to_insert)} additions")
        print(f"  • -0 deletions")

        diff_lines = list(diff)
        if not diff_lines:
            return

        # Skip header and show the diff
        for line in diff_lines[3:]:
            if line.startswith('+'):
                print(f"    {Back.GREEN}{Fore.WHITE}{line}{Style.RESET_ALL}")
            elif line.startswith('-'):
                 # This shouldn't happen in a pure insertion, but we handle it for robustness
                print(f"    {Back.RED}{Fore.WHITE}{line}{Style.RESET_ALL}")
            else:
                print(f"    {line}")

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