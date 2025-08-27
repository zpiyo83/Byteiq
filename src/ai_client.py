"""
AI客户端模块 - 处理与AI API的交互
"""

import os
import json
import requests
import threading
import time
import queue
import sys
from concurrent.futures import ThreadPoolExecutor, Future
from .thinking_animation import start_thinking, stop_thinking
from .keyboard_handler import (
    start_task_monitoring, stop_task_monitoring,
    is_task_interrupted, reset_interrupt_flag,
    interrupt_current_task
)
from .output_monitor import start_output_monitoring, stop_output_monitoring, enable_print_monitoring
from .config import load_config, DEFAULT_API_URL
from .debug_config import is_raw_output_enabled
from colorama import Fore, Style

def format_ai_response(raw_response, api_result=None):
    """
    根据调试配置格式化AI响应

    Args:
        raw_response (str): AI的原始响应内容
        api_result (dict, optional): 完整的API响应结果

    Returns:
        str: 格式化后的响应内容
    """
    if is_raw_output_enabled():
        # 原始输出模式：显示完整的未经处理的数据
        output_lines = []
        output_lines.append("=" * 80)
        output_lines.append("🔧 原始输出模式 - 调试信息")
        output_lines.append("=" * 80)

        if api_result:
            output_lines.append("\n📡 完整API响应:")
            output_lines.append("-" * 40)
            import json
            try:
                formatted_json = json.dumps(api_result, indent=2, ensure_ascii=False)
                output_lines.append(formatted_json)
            except:
                output_lines.append(str(api_result))

        output_lines.append("\n💬 AI原始响应内容:")
        output_lines.append("-" * 40)
        output_lines.append(raw_response)

        output_lines.append("\n" + "=" * 80)
        output_lines.append("🔧 原始输出模式结束")
        output_lines.append("=" * 80)

        return "\n".join(output_lines)
    else:
        # 正常模式：返回渲染后的用户友好内容
        return raw_response

def timeout_protection(timeout_seconds=200):
    """超时保护装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            thread.join(timeout=timeout_seconds)

            if thread.is_alive():
                # 超时了，强制清理
                try:
                    stop_thinking()
                    stop_task_monitoring()
                except:
                    pass
                return "请求超时，已强制停止。请检查网络连接或稍后重试。"

            if exception[0]:
                raise exception[0]

            return result[0]
        return wrapper
    return decorator

class AsyncNetworkManager:
    """异步网络请求管理器"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.current_request = None

    def submit_request(self, func, *args, **kwargs):
        """提交异步请求"""
        if self.current_request and not self.current_request.done():
            # 取消之前的请求
            self.current_request.cancel()

        self.current_request = self.executor.submit(func, *args, **kwargs)
        return self.current_request

    def check_result(self, timeout=0.1):
        """非阻塞检查结果"""
        if self.current_request is None:
            return None, False

        try:
            result = self.current_request.result(timeout=timeout)
            return result, True
        except Exception as e:
            if self.current_request.done():
                return str(e), True
            return None, False

    def cancel_current_request(self):
        """取消当前请求"""
        if self.current_request and not self.current_request.done():
            self.current_request.cancel()
            return True
        return False

    def shutdown(self):
        """关闭线程池"""
        self.executor.shutdown(wait=False)

class AIClient:
    """AI客户端类"""

    def __init__(self):
        self.config = load_config()
        self.api_url = DEFAULT_API_URL
        self.conversation_history = []
        self.is_loading = False
        self.loading_thread = None
        self.network_manager = AsyncNetworkManager()
        
        # 集成智能上下文管理器
        from .context_manager import context_manager
        self.context_manager = context_manager
        
        # 集成代理式编程增强器
        from .agent_enhancer import agent_enhancer
        self.agent_enhancer = agent_enhancer

    def get_system_prompt(self):
        """获取系统提示词"""
        # 检查当前模式和提示词强度
        from .modes import mode_manager
        from .config import load_config
        from .byteiq_config import byteiq_config_manager

        current_mode = mode_manager.get_current_mode()
        config = load_config()
        prompt_strength = config.get('prompt_strength', 'claude')  # 默认使用claude强度

        # 导入提示词模板系统
        from .prompt_templates import get_prompt_template

        base_prompt = get_prompt_template(current_mode, prompt_strength)
        
        # 使用BYTEIQ.md配置增强提示词
        enhanced_prompt = byteiq_config_manager.get_enhanced_system_prompt(base_prompt)
        
        return enhanced_prompt





    def get_project_structure(self, path=".", max_depth=3, current_depth=0):
        """获取项目结构"""
        if current_depth >= max_depth:
            return ""

        structure = ""
        try:
            items = sorted(os.listdir(path))
            for item in items:
                if item.startswith('.'):
                    continue

                item_path = os.path.join(path, item)
                indent = "  " * current_depth

                if os.path.isdir(item_path):
                    structure += f"{indent}{item}/\n"
                    structure += self.get_project_structure(item_path, max_depth, current_depth + 1)
                else:
                    structure += f"{indent}{item}\n"
        except PermissionError:
            pass

        return structure

    # 旧的加载动画已移除，使用新的思考动画系统

    def _make_network_request(self, data, headers):
        """执行网络请求（在子线程中运行）"""
        try:
            response = requests.post(self.api_url, json=data, headers=headers, timeout=180)
            if response.status_code == 401:
                return {"error": "API密钥无效或未授权。请检查您的密钥。", "status_code": 401}
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {"error": f"HTTP 错误: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}

    def send_message_async(self, user_input, include_structure=True, model_override=None):
        """异步发送消息，返回Future对象"""
        config = load_config()

        if not config.get('api_key'):
            return None

        # 决定使用哪个模型
        model_to_use = model_override if model_override else config.get('model', 'gpt-3.5-turbo')

        # 构建请求数据
        data = {
            "model": model_to_use,
            "messages": [
                {"role": "system", "content": self.get_system_prompt()},
                *self.conversation_history,
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7,
            "max_tokens": 6000
        }

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        # 提交异步请求
        return self.network_manager.submit_request(self._make_network_request, data, headers)

    def send_message_streaming(self, user_input, include_structure=True, model_override=None, is_continuation=False):
        """流式发送消息给AI，实时显示响应"""
        config = load_config()

        if not config.get('api_key'):
            return "错误：请先设置API密钥"

        # 决定使用哪个模型
        model_to_use = model_override if model_override else config.get('model', 'gpt-3.5-turbo')

        # 构建请求数据
        data = {
            "model": model_to_use,
            "messages": [
                {"role": "system", "content": self.get_system_prompt()},
                *self.conversation_history,
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7,
            "max_tokens": 6000,
            "stream": True  # 启用流式输出
        }

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        # 启动任务监控
        start_task_monitoring(interrupt_current_task)

        try:
            print(f"{Fore.GREEN}AI: {Style.RESET_ALL}", end="", flush=True)
            
            # 发送流式请求
            response = requests.post(self.api_url, json=data, headers=headers, stream=True, timeout=180)
            
            if response.status_code == 401:
                return f"认证失败: API密钥无效或未授权。请检查您的密钥。"
            
            if response.status_code != 200:
                return f"API请求失败: {response.status_code} - {response.text}"

            full_response = ""
            
            # 逐行处理流式响应
            for line in response.iter_lines():
                # 检查用户中断
                if is_task_interrupted():
                    reset_interrupt_flag()
                    print(f"\n{Fore.YELLOW}[任务已被用户中断]{Style.RESET_ALL}")
                    return "任务已被用户中断"
                
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 移除 'data: ' 前缀
                        
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            chunk_data = json.loads(data_str)
                            if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                delta = chunk_data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content = delta['content']
                                    print(content, end="", flush=True)
                                    full_response += content
                        except json.JSONDecodeError:
                            continue
            
            print()  # 换行
            
            # 添加到对话历史
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": full_response})

            # 限制历史长度，但保留更多上下文（从10增加到20）
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            return full_response

        except requests.exceptions.Timeout:
            return "请求超时，请检查网络连接或稍后重试"
        except requests.exceptions.RequestException as e:
            return f"网络错误: {str(e)}"
        except Exception as e:
            return f"发生错误: {str(e)}"
        finally:
            # 确保停止监控
            try:
                stop_task_monitoring()
            except:
                pass

    def send_message_non_blocking(self, user_input, include_structure=True, model_override=None):
        """非阻塞发送消息给AI"""
        # 启动思考动画
        start_thinking()

        # 启动任务监控
        start_task_monitoring(interrupt_current_task)

        try:
            # 提交异步请求
            future = self.send_message_async(user_input, include_structure, model_override)
            if not future:
                return "错误：请先设置API密钥"

            # 非阻塞等待结果
            start_time = time.time()
            max_wait_time = 180  # 最大等待180秒

            while True:
                # 检查用户中断
                if is_task_interrupted():
                    self.network_manager.cancel_current_request()
                    reset_interrupt_flag()
                    return "任务已被用户中断"

                # 检查是否超时
                if time.time() - start_time > max_wait_time:
                    self.network_manager.cancel_current_request()
                    return "请求超时，请检查网络连接"

                # 非阻塞检查结果
                result, is_done = self.network_manager.check_result(timeout=0.1)

                if is_done:
                    if isinstance(result, dict) and "error" in result:
                        if result.get("status_code") == 401:
                            return f"认证失败: {result['error']}"
                        return f"网络错误: {result['error']}"

                    # 处理成功响应
                    if isinstance(result, dict) and "choices" in result:
                        ai_response = result["choices"][0]["message"]["content"]

                        # 添加到对话历史
                        self.conversation_history.append({"role": "user", "content": user_input})
                        self.conversation_history.append({"role": "assistant", "content": ai_response})

                        # 限制历史长度，但保留更多上下文（从10增加到20）
                        if len(self.conversation_history) > 20:
                            self.conversation_history = self.conversation_history[-20:]

                        # 根据调试配置格式化响应
                        return format_ai_response(ai_response, result)
                    else:
                        return f"API响应格式错误: {result}"

                # 短暂休眠，避免CPU占用过高
                time.sleep(0.1)

        except Exception as e:
            return f"发生错误: {str(e)}"
        finally:
            # 确保停止动画和监控
            try:
                stop_thinking()
                stop_task_monitoring()
            except:
                pass

    @timeout_protection(timeout_seconds=200)
    def send_message(self, user_input, include_structure=True):
        """发送消息给AI（保持向后兼容）"""
        try:
            # 分析用户请求并创建执行计划
            analysis = self.agent_enhancer.analyze_user_request(user_input)
            
            # 添加用户消息到上下文管理器
            self.context_manager.add_message("user", user_input, {"analysis": analysis})
            
            # 如果需要规划，创建执行计划
            if analysis["requires_planning"]:
                plan_result = self.agent_enhancer.create_execution_plan(user_input, analysis)
                self.context_manager.add_project_context("current_plan", plan_result, "high")
            
            # 构建用户消息
            user_message = user_input
            if include_structure:
                structure = self.get_project_structure()
                if structure.strip():
                    user_message += f"\n\n当前项目结构：\n```\n{structure}```"
                    # 添加项目结构到上下文
                    self.context_manager.add_project_context("project_structure", structure, "high")
                else:
                    user_message += "\n\n当前项目结构：空"

            # 获取系统提示词并根据思考模式增强
            base_prompt = self.get_system_prompt()
            thinking_mode = analysis["thinking_mode"]
            enhanced_prompt = self.agent_enhancer.enhance_prompt_with_thinking(base_prompt, thinking_mode)

            # 使用智能上下文管理器获取消息
            messages = [{"role": "system", "content": enhanced_prompt}]
            
            # 获取增强的消息历史
            enhanced_messages = self.context_manager.get_enhanced_messages()
            messages.extend(enhanced_messages)

            # 准备请求数据
            data = {
                "model": self.config.get("model", "gpt-3.5-turbo"),
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 6000
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.get('api_key', '')}"
            }

            # 启动思考动画
            start_thinking()
            
            # 启动任务监控
            start_task_monitoring(interrupt_current_task)

            try:
                # 发送请求，增加超时时间
                response = requests.post(self.api_url, json=data, headers=headers, timeout=180)
            finally:
                # 确保无论如何都停止动画和监控
                stop_thinking()
                stop_task_monitoring()

            # 检查是否被中断
            if is_task_interrupted():
                reset_interrupt_flag()
                return "任务已被用户中断"

            if response.status_code == 401:
                return f"认证失败: API密钥无效或未授权。请检查您的密钥。 - {response.text}"

            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']

                # 添加AI响应到上下文管理器
                self.context_manager.add_message("assistant", ai_response)

                # 保持向后兼容的历史记录（但现在主要由context_manager管理）
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                # 自动保存上下文
                self.context_manager.save_context()

                # 限制历史长度，但保留更多上下文（保持20条消息）
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]

                # 返回原始响应，由调用者决定如何格式化
                return ai_response
            else:
                return f"API请求失败: {response.status_code} - {response.text}"

        except requests.exceptions.Timeout:
            # 确保停止动画和监控
            try:
                stop_thinking()
                stop_task_monitoring()
            except:
                pass
            return "请求超时，请检查网络连接或稍后重试"
        except requests.exceptions.RequestException as e:
            # 确保停止动画和监控
            try:
                stop_thinking()
                stop_task_monitoring()
            except:
                pass
            return f"网络错误: {str(e)}"
        except KeyboardInterrupt:
            # 处理Ctrl+C中断
            try:
                stop_thinking()
                stop_task_monitoring()
            except:
                pass
            return "任务已被用户中断"
        except Exception as e:
            # 确保停止动画和监控
            try:
                stop_thinking()
                stop_task_monitoring()
            except:
                pass
            return f"发生错误: {str(e)}"

    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []


    def get_history(self):
        """获取当前对话历史"""
        return self.conversation_history

    def set_history(self, history):
        """设置新的对话历史"""
        self.conversation_history = history

# 全局AI客户端实例
ai_client = AIClient()
