"""
HACPP模式AI客户端 - 处理便宜AI和贵AI的协作
"""

import os
import json
import requests
from colorama import Fore, Style
from .config import load_config, DEFAULT_API_URL
from .ai_client import ai_client
from .modes import hacpp_mode


class HACPPAIClient:
    """HACPP模式AI客户端"""

    def __init__(self):
        self.cheap_ai_history = []  # 便宜AI的对话历史
        self.expensive_ai_history = []  # 贵AI的对话历史

    def send_to_cheap_ai(self, message, model_name=None):
        """发送消息给便宜AI进行分析"""
        if not model_name:
            model_name = hacpp_mode.cheap_model

        if not model_name:
            return "错误：未设置便宜模型"

        # 构建便宜AI的系统提示
        system_prompt = self._get_cheap_ai_system_prompt()

        # 发送请求到便宜AI
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

            # 构建消息历史
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]

            # 添加历史对话
            for msg in self.cheap_ai_history[-5:]:  # 只保留最近5条对话
                messages.insert(-1, msg)

            payload = {
                'model': model_name,
                'messages': messages,
                'temperature': 0.3,  # 便宜AI使用较低的温度，更加专注
                'max_tokens': 2000
            }

            response = requests.post(api_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']

                # 保存到历史
                self.cheap_ai_history.append({"role": "user", "content": message})
                self.cheap_ai_history.append({"role": "assistant", "content": ai_response})

                return ai_response
            else:
                return f"便宜AI请求失败: {response.status_code} - {response.text}"

        except Exception as e:
            return f"便宜AI请求异常: {str(e)}"

    def send_to_expensive_ai(self, message, files_to_modify=None):
        """发送消息给贵AI进行代码编写"""
        # 构建贵AI的系统提示
        system_prompt = self._get_expensive_ai_system_prompt(files_to_modify)

        # 使用现有的ai_client，但添加特殊的系统提示
        original_message = message
        if files_to_modify:
            message = f"[HACPP模式] 需要修改的文件: {', '.join(files_to_modify)}\n\n{message}"

        # 发送给贵AI
        return ai_client.send_message(message)

    def process_hacpp_request(self, user_request):
        """处理HACPP模式的请求"""
        print(f"{Fore.CYAN}🔄 HACPP模式处理中...{Style.RESET_ALL}")

        # 第一步：便宜AI分析需求和项目
        print(f"{Fore.YELLOW}📋 便宜AI正在分析需求和项目结构...{Style.RESET_ALL}")

        # 获取项目结构信息
        project_info = self._get_project_structure()

        analysis_prompt = f"""
用户需求: {user_request}

当前项目结构:
{project_info}

请分析这个需求，并确定需要修改哪些文件。请按照以下格式回复：

FILES_TO_MODIFY:
- 文件路径1: 修改原因
- 文件路径2: 修改原因

ANALYSIS:
详细分析用户需求，说明实现方案和步骤。

PRIORITY:
HIGH/MEDIUM/LOW - 任务优先级

IMPLEMENTATION_STEPS:
1. 步骤1
2. 步骤2
3. 步骤3
"""

        cheap_analysis = self.send_to_cheap_ai(analysis_prompt)

        if "错误" in cheap_analysis:
            print(f"{Fore.RED}便宜AI分析失败: {cheap_analysis}{Style.RESET_ALL}")
            return False

        print(f"{Fore.GREEN}📋 便宜AI分析结果:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{cheap_analysis}{Style.RESET_ALL}")

        # 解析便宜AI的分析结果
        files_to_modify = self._parse_files_from_analysis(cheap_analysis)

        if not files_to_modify:
            print(f"{Fore.YELLOW}⚠️ 便宜AI未识别出需要修改的文件，将交给贵AI处理{Style.RESET_ALL}")
            files_to_modify = []

        # 第二步：贵AI执行具体的代码修改
        print(f"\n{Fore.CYAN}💎 贵AI开始执行代码修改...{Style.RESET_ALL}")

        expensive_prompt = f"""
[HACPP模式协作]

便宜AI的分析结果:
{cheap_analysis}

用户原始需求:
{user_request}

请根据便宜AI的分析，执行具体的代码修改任务。你可以调用所有可用的工具来完成任务。
"""

        # 发送给贵AI处理
        return self.send_to_expensive_ai(expensive_prompt, files_to_modify)

    def _get_cheap_ai_system_prompt(self):
        """获取便宜AI的系统提示"""
        return """你是一个代码分析专家，专门负责分析用户需求并确定需要修改的文件。

你的任务是：
1. 理解用户的需求
2. 分析当前项目结构
3. 确定需要修改哪些文件
4. 提供实现方案的概述

请始终按照指定格式回复，确保FILES_TO_MODIFY部分清晰列出需要修改的文件路径。

你不需要编写具体代码，只需要做分析和规划工作。具体的代码实现将由更高级的AI来完成。"""

    def _get_expensive_ai_system_prompt(self, files_to_modify=None):
        """获取贵AI的系统提示"""
        base_prompt = """你是一个高级代码AI，专门负责执行具体的代码修改任务。

你正在HACPP协作模式中工作：
- 便宜AI已经完成了需求分析和文件识别
- 你的任务是执行具体的代码修改和实现

你可以使用所有可用的工具来完成任务，包括读取文件、修改文件、创建文件等。

请按照便宜AI的分析结果，高效地完成用户的需求。"""

        if files_to_modify:
            base_prompt += f"\n\n重点关注以下文件：{', '.join(files_to_modify)}"

        return base_prompt

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