"""
MCP (Model Context Protocol) 客户端
支持连接和使用MCP服务来扩展AI助手的能力
"""

import json
import asyncio
import subprocess
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from colorama import Fore, Style

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str

@dataclass
class MCPResource:
    """MCP资源定义"""
    uri: str
    name: str
    description: str
    mime_type: str
    server_name: str

@dataclass
class MCPServer:
    """MCP服务器配置"""
    name: str
    command: List[str]
    args: List[str] = None
    env: Dict[str, str] = None
    server_type: str = "process"  # "process" 或 "sse"
    url: str = None  # SSE服务器的URL
    process: subprocess.Popen = None
    tools: List[MCPTool] = None
    resources: List[MCPResource] = None

class MCPClient:
    """MCP客户端，管理MCP服务器连接和工具调用"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.available_tools: Dict[str, MCPTool] = {}
        self.available_resources: Dict[str, MCPResource] = {}
        self.is_initialized = False
    
    def add_server(self, name: str, command: List[str], args: List[str] = None, env: Dict[str, str] = None,
                   server_type: str = "process", url: str = None):
        """添加MCP服务器配置"""
        server = MCPServer(
            name=name,
            command=command,
            args=args or [],
            env=env or {},
            server_type=server_type,
            url=url,
            tools=[],
            resources=[]
        )
        self.servers[name] = server
        logger.info(f"添加MCP服务器: {name} (类型: {server_type})")
    
    async def start_server(self, server_name: str) -> bool:
        """启动MCP服务器"""
        if server_name not in self.servers:
            logger.error(f"未找到服务器配置: {server_name}")
            return False
        
        server = self.servers[server_name]
        try:
            if server.server_type == "sse":
                # SSE类型服务器不需要启动进程，直接初始化连接
                logger.info(f"连接SSE MCP服务器 {server_name}: {server.url}")
                await self._initialize_sse_server(server)
                return True
            else:
                # 进程类型服务器
                # 构建完整命令
                full_command = server.command + server.args

                # 启动服务器进程
                server.process = subprocess.Popen(
                    full_command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env={**server.env} if server.env else None
                )

                logger.info(f"MCP服务器 {server_name} 启动成功")

                # 初始化连接并获取能力
                await self._initialize_server(server)
                return True
            
        except Exception as e:
            logger.error(f"启动MCP服务器 {server_name} 失败: {e}")
            return False
    
    async def _initialize_server(self, server: MCPServer):
        """初始化服务器连接并获取工具和资源列表"""
        try:
            # 发送初始化请求
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "clientInfo": {
                        "name": "forge-ai-code",
                        "version": "1.2.7"
                    }
                }
            }
            
            # 发送请求并获取响应
            response = await self._send_request(server, init_request)
            
            if response and "result" in response:
                # 获取服务器能力
                capabilities = response["result"].get("capabilities", {})
                
                # 获取工具列表
                if "tools" in capabilities:
                    await self._fetch_tools(server)
                
                # 获取资源列表
                if "resources" in capabilities:
                    await self._fetch_resources(server)
                
                logger.info(f"服务器 {server.name} 初始化完成")
            
        except Exception as e:
            logger.error(f"初始化服务器 {server.name} 失败: {e}")
    
    async def _fetch_tools(self, server: MCPServer):
        """获取服务器提供的工具列表"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            response = await self._send_request(server, request)
            
            if response and "result" in response:
                tools_data = response["result"].get("tools", [])
                
                for tool_data in tools_data:
                    tool = MCPTool(
                        name=tool_data["name"],
                        description=tool_data.get("description", ""),
                        input_schema=tool_data.get("inputSchema", {}),
                        server_name=server.name
                    )
                    
                    server.tools.append(tool)
                    self.available_tools[f"{server.name}:{tool.name}"] = tool
                
                logger.info(f"从服务器 {server.name} 获取到 {len(tools_data)} 个工具")
        
        except Exception as e:
            logger.error(f"获取服务器 {server.name} 工具列表失败: {e}")
    
    async def _fetch_resources(self, server: MCPServer):
        """获取服务器提供的资源列表"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/list"
            }
            
            response = await self._send_request(server, request)
            
            if response and "result" in response:
                resources_data = response["result"].get("resources", [])
                
                for resource_data in resources_data:
                    resource = MCPResource(
                        uri=resource_data["uri"],
                        name=resource_data.get("name", ""),
                        description=resource_data.get("description", ""),
                        mime_type=resource_data.get("mimeType", ""),
                        server_name=server.name
                    )
                    
                    server.resources.append(resource)
                    self.available_resources[f"{server.name}:{resource.uri}"] = resource
                
                logger.info(f"从服务器 {server.name} 获取到 {len(resources_data)} 个资源")
        
        except Exception as e:
            logger.error(f"获取服务器 {server.name} 资源列表失败: {e}")
    
    async def _send_request(self, server: MCPServer, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """向MCP服务器发送请求"""
        try:
            if server.server_type == "sse":
                return await self._send_sse_request(server, request)
            else:
                if not server.process or server.process.poll() is not None:
                    logger.error(f"服务器 {server.name} 进程未运行")
                    return None

                # 发送JSON-RPC请求
                request_json = json.dumps(request) + "\n"
                server.process.stdin.write(request_json)
                server.process.stdin.flush()

                # 读取响应
                response_line = server.process.stdout.readline()
                if response_line:
                    return json.loads(response_line.strip())

                return None

        except Exception as e:
            logger.error(f"发送请求到服务器 {server.name} 失败: {e}")
            return None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """调用MCP工具"""
        # 首先尝试直接查找工具
        tool = None
        if tool_name in self.available_tools:
            tool = self.available_tools[tool_name]
        else:
            # 如果直接查找失败，尝试通过简单名称查找
            for full_name, available_tool in self.available_tools.items():
                if available_tool.name == tool_name:
                    tool = available_tool
                    break

        if not tool:
            logger.error(f"未找到工具: {tool_name}")
            logger.error(f"可用工具: {list(self.available_tools.keys())}")
            return None

        server = self.servers[tool.server_name]
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": tool.name,
                    "arguments": arguments
                }
            }
            
            response = await self._send_request(server, request)

            if response:
                if "result" in response:
                    # 标准JSON-RPC响应
                    return {"result": response["result"]}
                elif "error" in response:
                    logger.error(f"工具调用错误: {response['error']}")
                    return {"error": response["error"]}
                else:
                    # 直接返回响应（用于SSE等特殊格式）
                    return response

            return None
            
        except Exception as e:
            logger.error(f"调用工具 {tool_name} 失败: {e}")
            return {"error": str(e)}
    
    async def read_resource(self, resource_uri: str) -> Optional[Dict[str, Any]]:
        """读取MCP资源"""
        resource_key = None
        for key, resource in self.available_resources.items():
            if resource.uri == resource_uri:
                resource_key = key
                break
        
        if not resource_key:
            logger.error(f"未找到资源: {resource_uri}")
            return None
        
        resource = self.available_resources[resource_key]
        server = self.servers[resource.server_name]
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "resources/read",
                "params": {
                    "uri": resource_uri
                }
            }
            
            response = await self._send_request(server, request)
            
            if response and "result" in response:
                return response["result"]
            elif response and "error" in response:
                logger.error(f"资源读取错误: {response['error']}")
                return {"error": response["error"]}
            
            return None
            
        except Exception as e:
            logger.error(f"读取资源 {resource_uri} 失败: {e}")
            return {"error": str(e)}
    
    def get_available_tools(self) -> List[MCPTool]:
        """获取所有可用工具列表"""
        return list(self.available_tools.values())
    
    def get_available_resources(self) -> List[MCPResource]:
        """获取所有可用资源列表"""
        return list(self.available_resources.values())
    
    async def stop_all_servers(self):
        """停止所有MCP服务器"""
        for server_name, server in self.servers.items():
            if server.process and server.process.poll() is None:
                try:
                    server.process.terminate()
                    server.process.wait(timeout=5)
                    logger.info(f"MCP服务器 {server_name} 已停止")
                except Exception as e:
                    logger.error(f"停止MCP服务器 {server_name} 失败: {e}")
                    try:
                        server.process.kill()
                    except:
                        pass
    
    def get_server_status(self) -> Dict[str, str]:
        """获取所有服务器状态"""
        status = {}
        for name, server in self.servers.items():
            if server.server_type == "sse":
                # SSE服务器状态基于URL可访问性
                status[name] = "运行中" if server.url else "未配置"
            elif server.process is None:
                status[name] = "未启动"
            elif server.process.poll() is None:
                status[name] = "运行中"
            else:
                status[name] = "已停止"
        return status

    async def _initialize_sse_server(self, server: MCPServer):
        """初始化SSE服务器连接"""
        try:
            # 对于SSE服务器，我们模拟一些基本工具
            # 实际实现中需要通过HTTP请求获取服务器能力

            # 添加一些默认的搜索工具
            if "bing" in server.name.lower() or "search" in server.name.lower():
                search_tool = MCPTool(
                    name="search",
                    description="搜索网络信息",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "搜索查询"},
                            "count": {"type": "integer", "description": "结果数量", "default": 10}
                        },
                        "required": ["query"]
                    },
                    server_name=server.name
                )

                server.tools.append(search_tool)
                self.available_tools[f"{server.name}:search"] = search_tool

                logger.info(f"SSE服务器 {server.name} 初始化完成，添加了搜索工具")

        except Exception as e:
            logger.error(f"初始化SSE服务器 {server.name} 失败: {e}")

    async def _send_sse_request(self, server: MCPServer, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """向SSE服务器发送请求"""
        try:
            import requests

            # 对于工具调用请求，我们需要特殊处理
            if request.get("method") == "tools/call":
                tool_name = request["params"]["name"]
                arguments = request["params"]["arguments"]

                # 如果是搜索工具，尝试不同的请求方式
                if tool_name == "search":
                    query = arguments.get("query", "")
                    count = arguments.get("count", 10)

                    # 方法1: 使用正确的参数格式
                    get_methods = [
                        # 根据您提供的示例，使用正确的参数名
                        {"query": query, "num_results": count},
                        {"query": query, "count": count},
                        # 备用格式
                        {"q": query, "num_results": count},
                        {"q": query, "n": count},
                    ]

                    for i, params in enumerate(get_methods):
                        try:
                            print(f"尝试GET方法 {i+1}: {params}")

                            # 尝试不同的URL格式
                            test_urls = [
                                server.url,
                                f"{server.url}/search",
                                f"{server.url}?query={query}&count={count}",
                            ]

                            for test_url in test_urls:
                                try:
                                    response = requests.get(test_url, params=params, timeout=10)
                                    print(f"  URL: {test_url}, 状态码: {response.status_code}")

                                    if response.status_code == 200:
                                        try:
                                            result_data = response.json()
                                            print(f"  成功获取JSON数据")

                                            # 检查是否是您的MCP服务器格式
                                            if "response" in result_data and "content" in result_data["response"]:
                                                content = result_data["response"]["content"]
                                                if content and len(content) > 0 and "text" in content[0]:
                                                    # 解析嵌套的JSON搜索结果
                                                    search_results_text = content[0]["text"]
                                                    try:
                                                        search_results = json.loads(search_results_text)
                                                        # 格式化搜索结果
                                                        formatted_results = f"🔍 搜索查询: {query}\n\n📰 搜索结果:\n\n"

                                                        for i, result in enumerate(search_results, 1):
                                                            title = result.get("title", "无标题")
                                                            link = result.get("link", "")
                                                            snippet = result.get("snippet", "无描述")

                                                            formatted_results += f"{i}. **{title}**\n"
                                                            formatted_results += f"   链接: {link}\n"
                                                            formatted_results += f"   摘要: {snippet}\n\n"

                                                        return {
                                                            "result": {
                                                                "content": [
                                                                    {
                                                                        "type": "text",
                                                                        "text": formatted_results
                                                                    }
                                                                ]
                                                            }
                                                        }
                                                    except json.JSONDecodeError:
                                                        # 如果内部JSON解析失败，返回原始文本
                                                        return {
                                                            "result": {
                                                                "content": [
                                                                    {
                                                                        "type": "text",
                                                                        "text": f"🔍 搜索查询: {query}\n\n📰 搜索结果:\n{search_results_text}"
                                                                    }
                                                                ]
                                                            }
                                                        }

                                            # 如果不是预期格式，返回原始JSON
                                            return {
                                                "result": {
                                                    "content": [
                                                        {
                                                            "type": "text",
                                                            "text": json.dumps(result_data, ensure_ascii=False, indent=2)
                                                        }
                                                    ]
                                                }
                                            }
                                        except json.JSONDecodeError:
                                            # 如果不是JSON，检查是否是有用的文本
                                            text_content = response.text.strip()
                                            if text_content and len(text_content) > 10:
                                                print(f"  获取文本数据: {text_content[:100]}...")
                                                return {
                                                    "result": {
                                                        "content": [
                                                            {
                                                                "type": "text",
                                                                "text": text_content
                                                            }
                                                        ]
                                                    }
                                                }
                                except requests.exceptions.Timeout:
                                    print(f"  URL超时: {test_url}")
                                    continue
                                except Exception as e:
                                    print(f"  URL错误: {test_url}, {e}")
                                    continue

                        except Exception as e1:
                            print(f"GET方法 {i+1} 失败: {e1}")
                            continue

                    # 方法2: 快速尝试SSE流式请求（5秒超时）
                    try:
                        headers = {
                            "Accept": "text/event-stream",
                            "Cache-Control": "no-cache"
                        }

                        # 构建查询参数
                        params = {"query": query, "count": count}

                        response = requests.get(
                            server.url,
                            params=params,
                            headers=headers,
                            stream=True,
                            timeout=5
                        )

                        if response.status_code == 200:
                            # 读取SSE流（最多5秒）
                            result_text = ""
                            import time
                            start_time = time.time()

                            for line in response.iter_lines(decode_unicode=True):
                                if time.time() - start_time > 5:  # 5秒超时
                                    break

                                if line:
                                    if line.startswith('data: '):
                                        data = line[6:]  # 移除 'data: ' 前缀
                                        if data.strip() and data != '[DONE]':
                                            try:
                                                json_data = json.loads(data)
                                                result_text += json.dumps(json_data, ensure_ascii=False) + "\n"
                                            except json.JSONDecodeError:
                                                result_text += data + "\n"
                                    elif not line.startswith(':'):  # 忽略注释行
                                        result_text += line + "\n"

                            if result_text.strip():
                                return {
                                    "result": {
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": result_text.strip()
                                            }
                                        ]
                                    }
                                }
                    except Exception as e2:
                        logger.warning(f"SSE请求失败: {e2}")

                    # 所有方法都失败了，返回详细错误信息
                    error_msg = f"""❌ MCP搜索服务器连接失败

🔗 服务器URL: {server.url}
🔍 搜索查询: {query}

⚠️ 可能的原因:
1. 网络连接问题 - 请检查网络连接
2. 服务器暂时不可用 - 请稍后重试
3. 需要认证或特殊参数 - 请检查MCP服务器配置
4. 服务器URL可能已更改 - 请确认URL是否正确

💡 建议:
- 检查网络连接是否正常
- 确认MCP服务器URL是否正确
- 联系MCP服务器提供方确认服务状态"""

                    return {"error": error_msg}

            # 对于其他请求类型，使用标准的JSON-RPC over HTTP
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            response = requests.post(
                server.url,
                json=request,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"result": {"content": [{"type": "text", "text": response.text}]}}
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}

        except Exception as e:
            logger.error(f"SSE请求失败: {e}")
            return {"error": str(e)}

# 全局MCP客户端实例
mcp_client = MCPClient()
