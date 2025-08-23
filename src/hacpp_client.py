"""
HACPP模式AI客户端 - 处理便宜AI和贵AI的协作
"""

import os
import json
import re
import asyncio
import aiohttp
from colorama import Fore, Style
from .config import load_config, DEFAULT_API_URL

from .modes import hacpp_mode
from .thinking_animation import show_dot_cycle_animation_async


from .ai_tools import AIToolProcessor

class HACPPAIClient:
    """HACPP模式AI客户端"""

    def __init__(self):
        self.cheap_ai_history = []
        self.expensive_ai_history = []
        # 为便宜AI创建一个独立的、权限受限的工具处理器
        self.researcher_tool_processor = AIToolProcessor()
        # 关键：限制可用工具为只读
        self.researcher_tool_processor.tools = {
            'read_file': self.researcher_tool_processor.read_file,
            'code_search': self.researcher_tool_processor.code_search,
            'task_complete': self.researcher_tool_processor.task_complete
        }

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

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            for msg in self.cheap_ai_history[-5:]:
                messages.insert(-1, msg)

            payload = {
                'model': model_name,
                'messages': messages,
                'temperature': 0.3,
                'max_tokens': 2000
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=payload, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result['choices'][0]['message']['content']
                        self.cheap_ai_history.append({"role": "user", "content": message})
                        self.cheap_ai_history.append({"role": "assistant", "content": ai_response})
                        return ai_response
                    else:
                        error_text = await response.text()
                        return f"便宜AI请求失败: {response.status} - {error_text}"

        except Exception as e:
            return f"便宜AI请求异常: {str(e)}"



    def process_hacpp_request(self, user_request):
        """处理HACPP模式的请求，返回一个用于主循环的初始prompt"""
        print(f"{Fore.CYAN}🔄 HACPP模式启动 - 研究员（便宜AI）开始分析...{Style.RESET_ALL}")

        project_info = self._get_project_structure()
        current_message = f"""
用户需求: {user_request}

当前项目结构:
{project_info}

请分析此需求，并制定一个详细的计划。你可以使用 `read_file` 和 `code_search` 工具来收集更多信息。当你完成所有信息收集和规划后，请使用 `task_complete` 工具来结束你的任务，并在summary中总结你的最终计划。
"""

        max_iterations = 50
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

            # 关键：直接检查task_complete并提取总结
            task_complete_match = re.search(r'<task_complete><summary>(.*?)</summary></task_complete>', ai_response, re.DOTALL)
            if task_complete_match:
                summary = task_complete_match.group(1).strip()
                print(f"{Fore.GREEN}✅ 研究员（便宜AI）完成分析。{Style.RESET_ALL}")
                final_prompt = f"""
[HACPP模式协作]

便宜AI的研究总结和规划:
{summary}

原始用户需求:
{user_request}

现在，请作为执行者，根据以上规划开始实施任务。
"""
                return final_prompt # 成功交接

            # 处理其他只读工具
            result = self.researcher_tool_processor.process_response(ai_response)
            if result['has_tool'] and result['tool_result']:
                print(f"{Fore.YELLOW}便宜AI工具执行结果: {result['tool_result'][:200]}...{Style.RESET_ALL}")
                current_message = f"工具执行结果: {result['tool_result']}"
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
        return """你是代码分析专家（研究员）。你的唯一目标是为另一个AI（执行者）制定一个清晰、可操作的计划。

# 你的工作流程（必须严格遵守）
1.  **分析需求**：深入理解用户的最终目标。
2.  **收集信息**：你可以，且仅可以，使用以下只读工具来探索项目、阅读文件，并收集所有必要的信息：
    *   `<read_file><path>...</path></read_file>`
    *   `<code_search><keyword>...</keyword></code_search>`
3.  **循环迭代**：你可以多次调用这些工具来逐步完善你的理解和计划。
4.  **完成并移交**：当你收集到足够的信息并制定了完整的计划后，**你必须通过调用 `<task_complete><summary>...</summary></task_complete>` 工具来结束你的工作**。这是你唯一的结束方式，也是将计划移交给执行者的信号。

# `task_complete` 的 `summary` 规范（必须严格遵守）
在 `summary` 中，你必须提供一个清晰、简洁、完整的最终计划，这个计划将直接交给执行者AI。你的总结必须包含所有必要的文件路径和需要进行的修改。

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
        """获取项目结构信息"""
        project_info = []

        try:
            # 获取当前目录
            current_dir = os.getcwd()
            project_info.append(f"项目根目录: {current_dir}")

            # 列出主要文件和目录
            items = []
            for item in os.listdir('.'):
                if os.path.isdir(item):
                    # 目录
                    if not item.startswith('.') and item not in ['__pycache__', 'node_modules']:
                        items.append(f"📁 {item}/")
                        # 列出目录中的主要文件
                        try:
                            sub_items = os.listdir(item)[:5]  # 只列出前5个文件
                            for sub_item in sub_items:
                                if not sub_item.startswith('.') and not sub_item.startswith('__'):
                                    items.append(f"   📄 {item}/{sub_item}")
                        except:
                            pass
                else:
                    # 文件
                    if not item.startswith('.') and item.endswith(('.py', '.js', '.html', '.css', '.md', '.txt', '.json', '.yml', '.yaml')):
                        items.append(f"📄 {item}")

            if items:
                project_info.append("\n主要文件和目录:")
                project_info.extend(items[:20])  # 限制显示数量

            # 检查是否有特殊配置文件
            config_files = ['requirements.txt', 'package.json', 'pyproject.toml', 'setup.py', 'Dockerfile', 'README.md']
            found_configs = []
            for config in config_files:
                if os.path.exists(config):
                    found_configs.append(config)

            if found_configs:
                project_info.append(f"\n配置文件: {', '.join(found_configs)}")

        except Exception as e:
            project_info.append(f"获取项目结构时出错: {str(e)}")

        return '\n'.join(project_info)

    def clear_history(self):
        """清除对话历史"""
        self.cheap_ai_history = []
        self.expensive_ai_history = []


# 全局HACPP客户端实例
hacpp_client = HACPPAIClient()