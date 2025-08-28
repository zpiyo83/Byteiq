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
        self.shared_context = {
            'project_info': '',
            'analysis_history': [],
            'file_contents': {},
            'executed_commands': [],
            'findings': []
        }
        
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
        
        # 获取项目上下文并保存到共享上下文
        project_context = self._get_project_context()
        self.shared_context['project_info'] = project_context
        
        # 开始引导
        try:
            guidance = guide_ai.analyze_bug_and_start_guidance(bug_description, project_context)
            
            if not guidance or guidance.startswith("错误：") or guidance.startswith("引导者AI调用异常"):
                print(f"{Fore.RED}❌ {guidance or '引导者AI无响应'}{Style.RESET_ALL}")
                self.end_session()
                return False
        except Exception as e:
            print(f"{Fore.RED}❌ 调试会话初始化失败: {str(e)}{Style.RESET_ALL}")
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
            try:
                main_ai_response = ai_client.send_message_streaming(prompt)
                
                if not main_ai_response:
                    print(f"{Fore.RED}❌ 主AI无响应{Style.RESET_ALL}")
                    break
                
                # 检查是否是系统错误而非正常分析内容
                if main_ai_response.startswith("错误：") or main_ai_response.startswith("API调用失败"):
                    print(f"{Fore.RED}❌ 主AI响应异常: {main_ai_response}{Style.RESET_ALL}")
                    break
                    
            except Exception as e:
                print(f"{Fore.RED}❌ 主AI调用失败: {str(e)}{Style.RESET_ALL}")
                break
            
            # 处理主AI的工具调用
            try:
                tool_result = ai_tool_processor.process_response(main_ai_response)
                
                # 更新共享上下文
                self._update_shared_context_from_tools(tool_result, main_ai_response)
                
                # 检查是否调用了结束引导工具
                if tool_result.get('tool_result') and 'GUIDANCE_ENDED_START_FIXING::' in str(tool_result['tool_result']):
                    print(f"{Fore.GREEN}✅ 执行AI已完成分析，开始修复模式{Style.RESET_ALL}")
                    # 提取分析总结
                    tool_result_str = str(tool_result['tool_result'])
                    analysis_start = tool_result_str.find('分析总结: ') + len('分析总结: ')
                    analysis_end = tool_result_str.find('\n\n现在开始进入普通AI对话模式')
                    if analysis_start > len('分析总结: ') - 1 and analysis_end > analysis_start:
                        analysis_summary = tool_result_str[analysis_start:analysis_end]
                        print(f"\n{Fore.CYAN}📋 分析总结:{Style.RESET_ALL}")
                        print(analysis_summary)
                        # 保存分析总结到共享上下文
                        self.shared_context['findings'].append({
                            'type': 'final_analysis',
                            'content': analysis_summary,
                            'timestamp': self.session_step
                        })
                    
                    print(f"\n{Fore.MAGENTA}🔄 切换到普通AI对话模式，开始修复bug...{Style.RESET_ALL}")
                    # 将共享上下文传递给主AI
                    self._transfer_context_to_main_ai()
                    self.end_session()
                    return True
                
                # 收集完整的主AI回答（包括工具执行结果）
                full_main_response = main_ai_response
                if tool_result.get('has_tool') and tool_result.get('tool_result'):
                    # 格式化工具结果，确保引导者AI能看到完整内容
                    formatted_tool_result = self._format_tool_result_for_guide(tool_result['tool_result'])
                    full_main_response += f"\n\n工具执行结果:\n{formatted_tool_result}"
                    
                    # 显示工具执行状态
                    if tool_result.get('executed_tools'):
                        executed_tools_str = ', '.join(tool_result['executed_tools'])
                        print(f"{Fore.GREEN}✓ 工具执行完成: {executed_tools_str}{Style.RESET_ALL}")
                        
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ 工具处理异常: {str(e)}{Style.RESET_ALL}")
                full_main_response = main_ai_response  # 使用原始响应
            
            # 引导者AI继续引导
            print(f"\n{Fore.CYAN}🤖 引导者AI分析主AI回答...{Style.RESET_ALL}")
            try:
                # 将共享上下文传递给引导者AI
                context_enhanced_response = self._enhance_response_with_context(full_main_response)
                guidance = guide_ai.continue_guidance(context_enhanced_response)
                
                # 记录引导者的分析到共享上下文
                self.shared_context['analysis_history'].append({
                    'step': self.session_step,
                    'guidance': guidance,
                    'main_ai_response': main_ai_response
                })
                
                # 改进错误处理 - 不因为引导者AI的分析内容包含"错误"就终止会话
                if not guidance or guidance.startswith("错误：") or guidance.startswith("引导者AI调用异常"):
                    print(f"{Fore.RED}❌ 引导者AI异常: {guidance or '无响应'}{Style.RESET_ALL}")
                    break
                    
            except Exception as e:
                print(f"{Fore.RED}❌ 引导者AI调用失败: {str(e)}{Style.RESET_ALL}")
                break
            
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

    def _update_shared_context_from_tools(self, tool_result, main_ai_response):
        """从工具执行结果更新共享上下文"""
        try:
            if not tool_result.get('has_tool'):
                return
            
            executed_tools = tool_result.get('executed_tools', [])
            tool_result_content = tool_result.get('tool_result', '')
            
            # 记录执行的工具
            for tool_name in executed_tools:
                self.shared_context['executed_commands'].append({
                    'step': self.session_step,
                    'tool': tool_name,
                    'result': tool_result_content
                })
            
            # 如果是文件读取工具，保存文件内容
            if 'read_file' in executed_tools and isinstance(tool_result_content, str):
                # 尝试提取文件路径和内容
                import re
                file_match = re.search(r'<read_file><path>(.*?)</path></read_file>', main_ai_response)
                if file_match:
                    file_path = file_match.group(1)
                    self.shared_context['file_contents'][file_path] = tool_result_content
            
            # 记录重要发现
            if any(keyword in tool_result_content.lower() for keyword in ['错误', 'error', '问题', 'bug', '异常']):
                self.shared_context['findings'].append({
                    'type': 'issue_found',
                    'content': tool_result_content[:500],  # 限制长度
                    'step': self.session_step,
                    'tools_used': executed_tools
                })
                
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ 更新共享上下文失败: {str(e)}{Style.RESET_ALL}")

    def _enhance_response_with_context(self, response):
        """用共享上下文增强响应"""
        try:
            context_summary = self._get_context_summary()
            if context_summary:
                enhanced_response = f"""
{response}

=== 共享上下文信息 ===
{context_summary}
=== 上下文信息结束 ===
"""
                return enhanced_response
            return response
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ 增强上下文失败: {str(e)}{Style.RESET_ALL}")
            return response

    def _get_context_summary(self):
        """获取共享上下文摘要"""
        try:
            summary_parts = []
            
            # 项目信息
            if self.shared_context['project_info']:
                summary_parts.append(f"项目信息:\n{self.shared_context['project_info'][:300]}...")
            
            # 已读取的文件
            if self.shared_context['file_contents']:
                file_list = list(self.shared_context['file_contents'].keys())
                summary_parts.append(f"已分析文件: {', '.join(file_list[:5])}")
            
            # 执行的命令
            if self.shared_context['executed_commands']:
                recent_commands = self.shared_context['executed_commands'][-3:]
                cmd_summary = [f"{cmd['tool']}" for cmd in recent_commands]
                summary_parts.append(f"最近执行工具: {', '.join(cmd_summary)}")
            
            # 重要发现
            if self.shared_context['findings']:
                findings_count = len(self.shared_context['findings'])
                summary_parts.append(f"发现问题数量: {findings_count}")
                if findings_count > 0:
                    latest_finding = self.shared_context['findings'][-1]
                    summary_parts.append(f"最新发现: {latest_finding['content'][:200]}...")
            
            return '\n'.join(summary_parts) if summary_parts else ""
            
        except Exception as e:
            return f"上下文摘要生成失败: {str(e)}"

    def _transfer_context_to_main_ai(self):
        """将共享上下文传递给主AI"""
        try:
            from .ai_client import ai_client
            
            # 构建上下文总结
            context_message = f"""
=== 调试会话上下文传递 ===
Bug描述: {self.bug_description}
调试步骤: {self.session_step}

项目信息:
{self.shared_context['project_info']}

已分析文件:
{chr(10).join([f"- {path}: {content[:100]}..." for path, content in self.shared_context['file_contents'].items()])}

重要发现:
{chr(10).join([f"- 步骤{f['step']}: {f['content'][:200]}..." for f in self.shared_context['findings']])}

执行的工具:
{chr(10).join([f"- 步骤{cmd['step']}: {cmd['tool']}" for cmd in self.shared_context['executed_commands']])}

现在请基于以上分析开始修复bug。
=== 上下文传递结束 ===
"""
            
            # 将上下文添加到AI客户端的上下文中
            ai_client.add_context_message("调试会话上下文", context_message)
            
            print(f"{Fore.GREEN}✓ 共享上下文已传递给主AI{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ 上下文传递失败: {str(e)}{Style.RESET_ALL}")

# 全局调试会话实例
debug_session = DebugSession()
