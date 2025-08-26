"""
AI辅助调试会话管理器
"""

from colorama import Fore, Style
from .guide_ai import guide_ai
from .ai_client import ai_client
from .ai_tools import ai_tool_processor

class DebugSession:
    """AI辅助调试会话管理器"""
    
    def __init__(self):
        self.is_active = False
        self.bug_description = ""
        self.guide_model = None
        self.session_step = 0
        self.max_steps = 20
        
    def start_session(self, bug_description, guide_model_name):
        """开始调试会话"""
        self.is_active = True
        self.bug_description = bug_description
        self.guide_model = guide_model_name
        self.session_step = 0
        
        # 设置引导者AI模型
        guide_ai.set_guide_model(guide_model_name)
        
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🔧 AI辅助调试会话启动{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Bug描述: {bug_description[:50]}...{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}引导者AI: {guide_model_name}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        
        # 获取项目上下文
        project_context = self._get_project_context()
        
        # 开始引导
        guidance = guide_ai.analyze_bug_and_start_guidance(bug_description, project_context)
        
        if "错误" in guidance:
            print(f"{Fore.RED}❌ {guidance}{Style.RESET_ALL}")
            self.end_session()
            return False
            
        print(f"\n{Fore.CYAN}🤖 引导者AI:{Style.RESET_ALL}")
        print(guidance)
        
        # 将引导转换为主AI可理解的格式
        main_ai_prompt = guide_ai.format_guidance_for_main_ai(guidance)
        
        return self._continue_debug_loop(main_ai_prompt)
    
    def _continue_debug_loop(self, prompt):
        """继续调试循环"""
        while self.is_active and self.session_step < self.max_steps:
            self.session_step += 1
            
            print(f"\n{Fore.YELLOW}📍 调试步骤 {self.session_step}/{self.max_steps}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}主AI正在分析...{Style.RESET_ALL}")
            
            # 主AI响应
            main_ai_response = ai_client.send_message_streaming(prompt)
            
            if not main_ai_response or "错误" in main_ai_response:
                print(f"{Fore.RED}❌ 主AI响应异常: {main_ai_response}{Style.RESET_ALL}")
                break
            
            # 处理主AI的工具调用
            tool_result = ai_tool_processor.process_response(main_ai_response)
            
            # 收集完整的主AI回答（包括工具执行结果）
            full_main_response = main_ai_response
            if tool_result.get('has_tool') and tool_result.get('tool_result'):
                # 格式化工具结果，确保引导者AI能看到完整内容
                formatted_tool_result = self._format_tool_result_for_guide(tool_result['tool_result'])
                full_main_response += f"\n\n工具执行结果:\n{formatted_tool_result}"
            
            # 引导者AI继续引导
            print(f"\n{Fore.CYAN}🤖 引导者AI分析主AI回答...{Style.RESET_ALL}")
            guidance = guide_ai.continue_guidance(full_main_response)
            
            # 改进错误处理 - 不因为引导者AI的分析内容包含"错误"就终止会话
            if guidance.startswith("错误：") or guidance.startswith("引导者AI调用异常"):
                print(f"{Fore.RED}❌ 引导者AI异常: {guidance}{Style.RESET_ALL}")
                break
            
            print(f"\n{Fore.CYAN}🤖 引导者AI:{Style.RESET_ALL}")
            print(guidance)
            
            # 检查是否调试完成
            if guide_ai.is_debugging_complete(guidance):
                print(f"\n{Fore.GREEN}✅ 调试完成！{Style.RESET_ALL}")
                self.end_session()
                return True
            
            # 准备下一轮对话
            prompt = guide_ai.format_guidance_for_main_ai(guidance)
        
        if self.session_step >= self.max_steps:
            print(f"\n{Fore.YELLOW}⚠️ 已达到最大调试步骤数，会话结束{Style.RESET_ALL}")
        
        self.end_session()
        return False
    
    def _get_project_context(self):
        """获取项目上下文信息"""
        try:
            import os
            context = f"当前工作目录: {os.getcwd()}\n"
            
            # 获取项目结构
            structure = ai_client.get_project_structure(max_depth=2)
            if structure:
                context += f"项目结构:\n{structure}"
            
            return context
        except Exception as e:
            return f"无法获取项目上下文: {str(e)}"
    
    def end_session(self):
        """结束调试会话"""
        if self.is_active:
            self.is_active = False
            guide_ai.clear_session()
            print(f"\n{Fore.MAGENTA}🔧 AI辅助调试会话已结束{Style.RESET_ALL}")
    
    def get_session_status(self):
        """获取会话状态"""
        if not self.is_active:
            return "无活动调试会话"
        
        return f"""
当前调试会话状态:
- Bug描述: {self.bug_description[:50]}...
- 引导者AI: {self.guide_model}
- 当前步骤: {self.session_step}/{self.max_steps}
- 会话状态: 活动中
"""

    def _format_tool_result_for_guide(self, tool_result):
        """格式化工具结果，确保引导者AI能获取完整信息"""
        import json
        
        # 如果工具结果是字典（包含详细信息），提取完整内容
        if isinstance(tool_result, dict):
            if tool_result.get('status') == 'success' and 'content' in tool_result:
                # 对于文件读取结果，包含完整文件内容
                formatted_result = f"""
文件路径: {tool_result.get('file_path', '未知')}
行数: {tool_result.get('line_count', 0)}
字符数: {tool_result.get('char_count', 0)}
文件内容:
{tool_result['content']}
"""
                return formatted_result
            else:
                # 其他字典结果，转换为JSON格式
                return json.dumps(tool_result, ensure_ascii=False, indent=2)
        
        # 如果是字符串，直接返回
        return str(tool_result)

# 全局调试会话实例
debug_session = DebugSession()
