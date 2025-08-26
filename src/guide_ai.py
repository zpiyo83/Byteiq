"""
AI引导者模块 - 用于引导主AI进行问题诊断和修复
"""

import requests
import json
import re
import os
import subprocess
from colorama import Fore, Style
from .ai_tools import ai_tool_processor
from .config import load_config, DEFAULT_API_URL
from .ai_client import ai_client

class GuideAI:
    """AI引导者类，负责引导主AI进行问题诊断"""
    
    def __init__(self):
        self.config = load_config()
        self.api_url = DEFAULT_API_URL
        self.guide_model = None
        self.conversation_history = []
        self.main_ai_responses = []
        
    def set_guide_model(self, model_name):
        """设置引导者AI模型"""
        self.guide_model = model_name
        print(f"{Fore.GREEN}✓ 引导者AI模型已设置: {model_name}{Style.RESET_ALL}")
        
    def get_guide_system_prompt(self):
        """获取引导者AI的系统提示词"""
        return """你是一个专业的AI调试引导者。你的任务是帮助另一个AI（主AI）诊断和修复问题。

# 你的角色和职责
1. **问题分析师**: 深入分析用户报告的bug，理解问题的本质
2. **引导专家**: 设计一系列有针对性的问题来引导主AI找到问题根源
3. **调试顾问**: 提供系统性的调试思路和方法
4. **独立分析师**: 你可以独立读取和分析文件，与主AI的上下文完全独立

# 可用工具
你可以使用以下工具来独立分析问题：
- <read_file><path>文件路径</path></read_file> - 读取文件内容
- <execute_command><command>命令</command></execute_command> - 执行系统命令
- <code_search><keyword>关键词</keyword></code_search> - 搜索代码

# 工作流程
1. 首先分析用户描述的bug
2. 使用工具独立调查和分析相关文件
3. 制定调试策略和问题清单
4. 逐步向主AI提出引导性问题
5. 根据主AI的回答调整后续问题
6. 最终帮助主AI找到并修复问题

# 引导原则
- 问题要具体、有针对性
- 从宏观到微观，从简单到复杂
- 每次只问1-2个关键问题
- 根据回答动态调整策略
- 鼓励主AI主动思考和探索
- 可以独立分析文件来更好地理解问题

# 输出格式
每次回复请使用以下格式：
```
[分析] 当前情况分析（可包含你独立分析的结果）
[问题] 向主AI提出的具体问题
[期望] 希望主AI提供什么信息
```

如果需要分析文件，请直接使用工具调用，然后基于分析结果提供引导。

现在开始你的引导工作！"""

    def analyze_bug_and_start_guidance(self, bug_description, project_context=""):
        """分析bug并开始引导过程"""
        if not self.guide_model:
            return "错误：请先设置引导者AI模型"
            
        # 构建初始分析请求
        initial_prompt = f"""
用户报告了以下bug：
{bug_description}

项目上下文：
{project_context}

请分析这个bug，并制定引导主AI进行调试的策略。开始第一轮引导。
"""
        
        return self._send_to_guide_ai(initial_prompt)
    
    def continue_guidance(self, main_ai_response):
        """根据主AI的回答继续引导"""
        if not self.guide_model:
            return "错误：请先设置引导者AI模型"
            
        # 记录主AI的回答
        self.main_ai_responses.append(main_ai_response)
        
        guidance_prompt = f"""
主AI刚才的回答：
{main_ai_response}

请根据这个回答，继续你的引导策略。如果问题已经找到并修复，请说明"调试完成"。
"""
        
        return self._send_to_guide_ai(guidance_prompt)
    
    def process_guide_tools(self, response_text):
        """处理引导AI的工具调用"""
        if not response_text:
            return response_text
            
        # 检查是否包含工具调用
        tool_patterns = [
            r'<read_file><path>(.*?)</path></read_file>',
            r'<execute_command><command>(.*?)</command></execute_command>',
            r'<code_search><keyword>(.*?)</keyword></code_search>'
        ]
        
        processed_response = response_text
        
        for pattern in tool_patterns:
            matches = re.findall(pattern, processed_response, re.DOTALL)
            for match in matches:
                tool_result = ""
                
                if 'read_file' in pattern:
                    # 读取文件 - 改进路径解析
                    try:
                        file_path = match.strip()
                        # 尝试多种路径解析方式
                        possible_paths = [
                            file_path,
                            os.path.join(os.getcwd(), file_path),
                            file_path.replace('F:\\项目\\测试\\', ''),
                            file_path.replace('F:/项目/测试/', ''),
                            os.path.basename(file_path)
                        ]
                        
                        content_found = False
                        for path in possible_paths:
                            if os.path.exists(path):
                                with open(path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    tool_result = f"\n[文件内容: {path}]\n{content}\n[文件结束]\n"
                                    content_found = True
                                    break
                        
                        if not content_found:
                            # 列出当前目录文件帮助调试
                            current_files = os.listdir('.')
                            tool_result = f"\n[错误: 文件 {file_path} 不存在]\n[当前目录文件: {', '.join(current_files[:10])}]\n"
                            
                    except Exception as e:
                        tool_result = f"\n[读取文件错误: {str(e)}]\n"
                        
                elif 'execute_command' in pattern:
                    # 执行命令
                    try:
                        command = match.strip()
                        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                        tool_result = f"\n[命令执行结果: {command}]\n{result.stdout}\n{result.stderr}\n[命令结束]\n"
                    except Exception as e:
                        tool_result = f"\n[命令执行错误: {str(e)}]\n"
                        
                elif 'code_search' in pattern:
                    # 代码搜索
                    try:
                        keyword = match.strip()
                        # 这里可以实现简单的文件搜索
                        tool_result = f"\n[代码搜索: {keyword}]\n搜索功能待实现\n[搜索结束]\n"
                    except Exception as e:
                        tool_result = f"\n[搜索错误: {str(e)}]\n"
                
                # 替换工具调用为结果
                original_call = re.search(pattern, processed_response).group(0)
                processed_response = processed_response.replace(original_call, tool_result)
        
        return processed_response

    def _send_to_guide_ai(self, prompt):
        """向引导者AI发送请求"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.config.get("api_key", "")}'
            }
            
            data = {
                "model": self.guide_model,
                "messages": [
                    {"role": "system", "content": self.get_guide_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # 处理工具调用
            processed_response = self.process_guide_tools(ai_response)
            
            # 保存对话历史
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": processed_response})
                
            # 限制历史长度
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return processed_response
                
        except Exception as e:
            return f"引导者AI调用异常: {str(e)}"
    
    def format_guidance_for_main_ai(self, guidance_text):
        """将引导者的指导格式化为主AI可理解的格式"""
        formatted_prompt = f"""
[AI调试引导模式]

引导者AI的指导：
{guidance_text}

请仔细阅读引导者的分析和问题，然后：
1. 回答引导者提出的具体问题
2. 提供引导者期望的信息
3. 如果需要检查代码或执行命令，请使用相应的工具
4. 保持专业和详细的回答

请开始回答引导者的问题。
"""
        return formatted_prompt
    
    def is_debugging_complete(self, guidance_text):
        """检查调试是否完成"""
        completion_keywords = ["调试完成", "问题已修复", "修复完成", "debugging complete", "fixed"]
        return any(keyword in guidance_text.lower() for keyword in completion_keywords)
    
    def clear_session(self):
        """清除当前调试会话"""
        self.conversation_history = []
        self.main_ai_responses = []
        print(f"{Fore.YELLOW}调试会话已清除{Style.RESET_ALL}")

# 全局引导者AI实例
guide_ai = GuideAI()
