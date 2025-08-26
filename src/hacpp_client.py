"""
HACPP模式AI客户端 - 处理便宜AI和贵AI的协作
"""

import os
import sys
import json
import re
import asyncio
import aiohttp
from colorama import Fore, Style
from .config import load_config, DEFAULT_API_URL
from .modes import hacpp_mode
from .thinking_animation import show_dot_cycle_animation_async
from .ai_tools import AIToolProcessor
from .file_utils import get_directory_structure

class HACPPAIClient:
    """HACPP模式AI客户端"""

    def __init__(self):
        self.cheap_ai_history = []
        self.expensive_ai_history = []
        self.max_history_messages = 20  # 最大历史消息数
        # 文件读取缓存，避免重复读取
        self.file_cache = {}
        self.read_history = set()  # 记录已读取的文件路径
        # 为便宜AI创建一个独立的、权限受限的工具处理器
        self.researcher_tool_processor = AIToolProcessor()
        # 给便宜AI更多工具权限，包括执行命令
        self.researcher_tool_processor.tools = {
            'read_file': self._cached_read_file,  # 使用缓存版本
            'execute_command': self.researcher_tool_processor.execute_command,  # 添加执行命令权限
            'task_complete': self.researcher_tool_processor.task_complete
        }

    def _add_to_history(self, history_list, role, content):
        """添加消息到历史记录，并限制最大数量"""
        history_list.append({"role": role, "content": content})
        # 保留最近的max_history_messages条消息
        if len(history_list) > self.max_history_messages:
            # 如果超过限制，移除最旧的消息，但保留系统消息
            history_list = [msg for msg in history_list if msg.get("role") == "system"][-1:] + \
                          [msg for msg in history_list if msg.get("role") != "system"][-(self.max_history_messages-1):]
        return history_list

    def _summarize_history(self, history_list):
        """生成历史记录的摘要"""
        if not history_list:
            return ""
            
        # 只保留用户和助手的消息进行摘要
        conversation = [f"{msg['role']}: {msg['content']}" for msg in history_list 
                       if msg.get("role") in ["user", "assistant"]]
        
        # 如果消息不多，直接返回完整历史
        if len(conversation) <= 10:
            return "\n".join(conversation)
            
        # 对长对话进行摘要
        summary = "\n".join(conversation[:3])  # 前几条消息
        summary += "\n... [之前的对话已省略] ...\n"
        summary += "\n".join(conversation[-7:])  # 后几条消息
        
        return summary

    def get_cheap_ai_history_summary(self):
        """获取便宜AI历史记录的摘要"""
        return self._summarize_history(self.cheap_ai_history)

    def get_expensive_ai_history_summary(self):
        """获取贵AI历史记录的摘要"""
        return self._summarize_history(self.expensive_ai_history)

    def clear_cache(self):
        """清空缓存，用于新的分析任务"""
        self.file_cache.clear()
        self.read_history.clear()
        self.cheap_ai_history = []
        self.expensive_ai_history = []

    def _cached_read_file(self, path):
        """带缓存的文件读取方法，避免重复读取"""
        # 检查是否已经读取过这个文件
        if path in self.read_history:
            return f"文件 {path} 已在本次分析中读取过，内容已缓存。如需重新查看，请使用 code_search 工具搜索特定内容。"
        
        try:
            # 如果没有读取过，则调用原始的读取方法
            result = self.researcher_tool_processor.read_file(path)
            
            # 如果读取成功，记录到历史中
            if "成功读取文件" in result or "文件内容:" in result:
                self.read_history.add(path)
            return result
        except FileNotFoundError:
            return f"错误：文件 {path} 不存在"
        except Exception as e:
            return f"读取文件时发生错误: {str(e)}"

    async def send_to_cheap_ai(self, message, model_name=None):
        """异步发送消息给便宜AI进行分析"""
        if not model_name:
            model_name = hacpp_mode.cheap_model

        if not model_name:
            return "错误：未设置便宜模型"

        system_prompt = self._get_cheap_ai_system_prompt()

        try:
            config = load_config()
            api_key = config.get('api_key')
            api_url = config.get('api_url', DEFAULT_API_URL)

            if not api_key:
                return "错误：未配置API密钥"

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }

            # 构建消息历史，确保不超过token限制
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加上下文摘要
            context_summary = self.get_cheap_ai_history_summary()
            if context_summary:
                messages.append({"role": "system", "name": "context_summary", 
                               "content": f"以下是之前的对话摘要：\n{context_summary}"})
            
            # 添加当前消息
            messages.append({"role": "user", "content": message})
            
            # 添加最近的几条完整对话
            recent_messages = self.cheap_ai_history[-4:]  # 保留最近的2轮对话
            for msg in recent_messages:
                messages.append(msg)

            payload = {
                'model': model_name,
                'messages': messages,
                'temperature': 0.3,
                'max_tokens': 6000
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=payload, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result['choices'][0]['message']['content']
                        # 使用新的方法添加历史记录
                        self.cheap_ai_history = self._add_to_history(
                            self.cheap_ai_history, "user", message)
                        self.cheap_ai_history = self._add_to_history(
                            self.cheap_ai_history, "assistant", ai_response)
                        return ai_response
                    else:
                        error_text = await response.text()
                        return f"便宜AI请求失败: {response.status} - {error_text}"

        except Exception as e:
            return f"便宜AI请求异常: {str(e)}"

    def process_hacpp_request(self, user_request):
        """处理HACPP模式的请求，返回一个用于主循环的初始prompt"""
        print(f"{Fore.CYAN}🔄 HACPP模式启动 - 研究员（便宜AI）开始分析...{Style.RESET_ALL}")
        
        # 清空缓存，开始新的分析任务
        self.clear_cache()

        project_info = self._get_project_structure()
        current_message = f"""
用户需求: {user_request}

当前项目结构:
{project_info}

请分析此需求，并制定一个详细的计划。在开始分析前，你必须首先使用TODO工具管理任务。在分析过程中，你需要及时更新TODO任务的状态和进度。你可以使用 `read_file` 和 `code_search` 工具来收集更多信息。当你完成所有信息收集和规划后，请使用 `task_complete` 工具来结束你的任务，并在summary中总结你的最终计划。
"""

        max_iterations = 200
        i = 0
        while i < max_iterations:
            i += 1
            # 异步调用便宜AI并显示动画
            ai_response = asyncio.run(self._get_response_with_animation(current_message, i, max_iterations))

            if "错误" in ai_response:
                print(f"{Fore.RED}便宜AI请求失败: {ai_response}{Style.RESET_ALL}")
                return None

            # 显示便宜AI的思考过程
            display_text = self.researcher_tool_processor._remove_xml_tags(ai_response)
            if display_text.strip():
                print(f"{Fore.GREEN}便宜AI: {display_text}{Style.RESET_ALL}")

            # 处理其他只读工具
            result = self.researcher_tool_processor.process_response(ai_response)
            if result.get('has_tool', False) and result.get('tool_result'):
                # 不再显示"便宜AI工具执行结果:"提示
                current_message = f"工具执行结果: {result['tool_result']}"
                
                # 检查是否是task_complete且需要继续
                if result.get('tool_name') == 'task_complete' and result.get('should_continue', False):
                    summary = result.get('summary', '')
                    if summary:
                        print(f"{Fore.GREEN}✅ 研究员（便宜AI）完成分析。{Style.RESET_ALL}")
                        final_prompt = f"""
[HACPP模式协作]

便宜AI的研究总结和规划:
{summary}

原始用户需求:
{user_request}

现在，请作为执行者，根据以上规划开始实施任务。
"""
                        return final_prompt  # 成功交接
            else:
                current_message = display_text

        print(f"{Fore.RED}便宜AI分析达到最大迭代次数，流程终止。{Style.RESET_ALL}")
        return None

    async def _get_response_with_animation(self, message, step, max_steps):
        """异步获取便宜AI的响应，并显示等待动画"""
        analysis_task = asyncio.create_task(self.send_to_cheap_ai(message))
        animation_task = asyncio.create_task(show_dot_cycle_animation_async(f"便宜AI分析中 (步骤 {step}/{max_steps})", duration=60))

        _, pending = await asyncio.wait([analysis_task, animation_task], return_when=asyncio.FIRST_COMPLETED)

        for task in pending:
            task.cancel()

        return await analysis_task

    def _get_cheap_ai_system_prompt(self):
        """获取便宜AI的系统提示"""
        return """你是代码分析专家（研究员）。你的目标是分析用户需求并为另一个AI（执行者）制定清晰、可操作的计划。

# 你的工作流程
1.  **分析需求**：深入理解用户的最终目标。
2.  **收集信息**：你可以使用以下只读工具来探索项目、阅读文件，并收集所有必要的信息：
    *   `<read_file><path>...</path></read_file>` - 注意：每个文件只能读取一次，重复读取会被阻止
3.  **循环迭代**：你可以多次调用这些工具来逐步完善你的理解和计划。
4.  **完成并移交**：当你收集到足够的信息并制定了完整的计划后，通过调用 `<task_complete><summary>...</summary></task_complete>` 工具来结束你的工作。这是将计划移交给执行者的信号。

# `task_complete` 的 `summary` 规范
在 `summary` 中，你需要提供一个清晰、简洁、完整的最终计划，这个计划将直接交给执行者AI。你的总结应该包含所有必要的文件路径和需要进行的修改。

# 绝对禁止的行为
你绝对不能调用任何写入、修改或删除文件的工具 (`write_file`, `create_file`, `delete_file`, `insert_code`, `replace_code`) 或 `execute_command`。你的职责是研究和规划，而不是执行。**任何试图执行修改操作的行为都是严重错误。**"""

    def _parse_files_from_analysis(self, analysis):
        """从便宜AI的分析结果中解析出需要修改的文件"""
        files = []
        lines = analysis.split('\n')
        in_files_section = False

        for line in lines:
            line = line.strip()
            if line.startswith('FILES_TO_MODIFY:'):
                in_files_section = True
                continue
            elif line.startswith('ANALYSIS:') or line.startswith('PRIORITY:'):
                in_files_section = False
                continue

            if in_files_section and line.startswith('- '):
                # 提取文件路径
                file_info = line[2:].split(':')[0].strip()
                if file_info:
                    files.append(file_info)

        return files


    def _get_project_structure(self):
        """获取当前项目结构的树状表示"""
        # 获取当前工作目录
        cwd = os.getcwd()
        # 获取目录结构
        structure = get_directory_structure(cwd)
        # 过滤掉不存在的文件和目录
        filtered_structure = []
        for item in structure.split('\n'):
            # 提取路径（假设每行以'- '开头）
            if item.startswith('- '):
                # 构建绝对路径
                abs_path = os.path.join(cwd, item[2:])
                if not os.path.exists(abs_path):
                    continue
            filtered_structure.append(item)
        return '\n'.join(filtered_structure)

    def clear_history(self):
        """清除对话历史"""
        self.cheap_ai_history = []
        self.expensive_ai_history = []


# 全局HACPP客户端实例
hacpp_client = HACPPAIClient()