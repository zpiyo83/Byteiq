"""
MCP配置管理模块
管理MCP服务器配置和预设
"""

import os
import json
from typing import Dict, List, Any, Optional
from colorama import Fore, Style

class MCPConfig:
    """MCP配置管理器"""

    def __init__(self, config_file: str = None):
        # 使用主配置文件而不是单独的MCP配置文件
        self.config_file = config_file or os.path.join(
            os.path.expanduser("~"),
            ".byteiq_config.json"
        )
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载MCP配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    full_config = json.load(f)
                    # 从主配置文件中提取MCP配置
                    mcp_config = full_config.get("mcpServers", {})

                    # 转换格式以兼容我们的MCP配置结构
                    if mcp_config:
                        return self.convert_mcp_config(mcp_config)
                    else:
                        return self.get_default_config()
            except Exception as e:
                print(f"{Fore.YELLOW}加载MCP配置失败: {e}{Style.RESET_ALL}")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def save_config(self) -> bool:
        """保存MCP配置到主配置文件"""
        try:
            # 读取完整的主配置文件
            full_config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    full_config = json.load(f)

            # 转换我们的MCP配置格式回原始格式
            mcp_servers = self.convert_to_original_format()
            full_config["mcpServers"] = mcp_servers

            # 保存完整配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"{Fore.RED}保存MCP配置失败: {e}{Style.RESET_ALL}")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认MCP配置"""
        return {
            "enabled": False,
            "auto_start": [],
            "servers": {
                "filesystem": {
                    "name": "filesystem",
                    "description": "文件系统操作服务",
                    "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
                    "args": ["."],
                    "env": {},
                    "enabled": False
                },
                "brave-search": {
                    "name": "brave-search",
                    "description": "Brave搜索服务",
                    "command": ["npx", "-y", "@modelcontextprotocol/server-brave-search"],
                    "args": [],
                    "env": {
                        "BRAVE_API_KEY": ""
                    },
                    "enabled": False
                },
                "github": {
                    "name": "github",
                    "description": "GitHub API服务",
                    "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
                    "args": [],
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": ""
                    },
                    "enabled": False
                },
                "postgres": {
                    "name": "postgres",
                    "description": "PostgreSQL数据库服务",
                    "command": ["npx", "-y", "@modelcontextprotocol/server-postgres"],
                    "args": [],
                    "env": {
                        "POSTGRES_CONNECTION_STRING": ""
                    },
                    "enabled": False
                },
                "sqlite": {
                    "name": "sqlite",
                    "description": "SQLite数据库服务",
                    "command": ["npx", "-y", "@modelcontextprotocol/server-sqlite"],
                    "args": [],
                    "env": {},
                    "enabled": False
                },
                "puppeteer": {
                    "name": "puppeteer",
                    "description": "网页自动化服务",
                    "command": ["npx", "-y", "@modelcontextprotocol/server-puppeteer"],
                    "args": [],
                    "env": {},
                    "enabled": False
                },
                "memory": {
                    "name": "memory",
                    "description": "内存存储服务",
                    "command": ["npx", "-y", "@modelcontextprotocol/server-memory"],
                    "args": [],
                    "env": {},
                    "enabled": False
                }
            }
        }
    
    def is_enabled(self) -> bool:
        """检查MCP是否启用"""
        return self.config.get("enabled", False)
    
    def enable_mcp(self, enabled: bool = True):
        """启用或禁用MCP"""
        self.config["enabled"] = enabled
        self.save_config()
    
    def get_enabled_servers(self) -> List[str]:
        """获取启用的服务器列表"""
        enabled_servers = []
        for server_name, server_config in self.config.get("servers", {}).items():
            if server_config.get("enabled", False):
                enabled_servers.append(server_name)
        return enabled_servers
    
    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """获取服务器配置"""
        return self.config.get("servers", {}).get(server_name)
    
    def enable_server(self, server_name: str, enabled: bool = True):
        """启用或禁用服务器"""
        if server_name in self.config.get("servers", {}):
            self.config["servers"][server_name]["enabled"] = enabled
            self.save_config()
            return True
        return False
    
    def set_server_env(self, server_name: str, env_key: str, env_value: str):
        """设置服务器环境变量"""
        if server_name in self.config.get("servers", {}):
            if "env" not in self.config["servers"][server_name]:
                self.config["servers"][server_name]["env"] = {}
            self.config["servers"][server_name]["env"][env_key] = env_value
            self.save_config()
            return True
        return False
    
    def add_custom_server(self, name: str, command: List[str], args: List[str] = None, 
                         env: Dict[str, str] = None, description: str = ""):
        """添加自定义服务器"""
        self.config["servers"][name] = {
            "name": name,
            "description": description,
            "command": command,
            "args": args or [],
            "env": env or {},
            "enabled": False
        }
        self.save_config()
    
    def remove_server(self, server_name: str):
        """移除服务器配置"""
        if server_name in self.config.get("servers", {}):
            del self.config["servers"][server_name]
            self.save_config()
            return True
        return False
    
    def get_auto_start_servers(self) -> List[str]:
        """获取自动启动的服务器列表"""
        return self.config.get("auto_start", [])
    
    def set_auto_start(self, server_names: List[str]):
        """设置自动启动的服务器"""
        self.config["auto_start"] = server_names
        self.save_config()
    
    def show_config_summary(self):
        """显示配置摘要"""
        print(f"\n{Fore.CYAN}MCP配置摘要{Style.RESET_ALL}")
        print("=" * 50)
        print(f"MCP状态: {'启用' if self.is_enabled() else '禁用'}")
        print(f"配置文件: {self.config_file}")
        
        enabled_servers = self.get_enabled_servers()
        print(f"启用的服务器: {len(enabled_servers)}")
        
        if enabled_servers:
            for server_name in enabled_servers:
                server_config = self.get_server_config(server_name)
                print(f"  - {server_name}: {server_config.get('description', '')}")
        
        auto_start = self.get_auto_start_servers()
        if auto_start:
            print(f"自动启动: {', '.join(auto_start)}")
    
    def interactive_setup(self):
        """交互式MCP设置"""
        print(f"\n{Fore.CYAN}MCP (Model Context Protocol) 设置{Style.RESET_ALL}")
        print("=" * 60)
        
        # 启用/禁用MCP
        current_status = "启用" if self.is_enabled() else "禁用"
        print(f"当前状态: {current_status}")
        
        enable_choice = input(f"\n是否启用MCP功能? (y/n, 当前: {'y' if self.is_enabled() else 'n'}): ").strip().lower()
        if enable_choice in ['y', 'yes']:
            self.enable_mcp(True)
            print(f"{Fore.GREEN}✓ MCP已启用{Style.RESET_ALL}")
        elif enable_choice in ['n', 'no']:
            self.enable_mcp(False)
            print(f"{Fore.YELLOW}MCP已禁用{Style.RESET_ALL}")
            return
        
        # 配置服务器
        print(f"\n{Fore.CYAN}可用的MCP服务器:{Style.RESET_ALL}")
        servers = self.config.get("servers", {})
        
        for i, (name, config) in enumerate(servers.items(), 1):
            status = "启用" if config.get("enabled", False) else "禁用"
            print(f"  {i}. {name} - {config.get('description', '')} ({status})")
        
        print(f"\n{Fore.CYAN}服务器配置选项:{Style.RESET_ALL}")
        print("  a - 启用/禁用服务器")
        print("  b - 设置环境变量")
        print("  c - 设置自动启动")
        print("  d - 添加自定义服务器")
        print("  q - 完成设置")
        
        while True:
            choice = input(f"\n{Fore.WHITE}请选择操作 > {Style.RESET_ALL}").strip().lower()
            
            if choice == 'a':
                self._configure_server_enable()
            elif choice == 'b':
                self._configure_server_env()
            elif choice == 'c':
                self._configure_auto_start()
            elif choice == 'd':
                self._add_custom_server()
            elif choice == 'q':
                break
            else:
                print(f"{Fore.YELLOW}无效选择{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}✓ MCP配置完成{Style.RESET_ALL}")
        self.show_config_summary()
    
    def _configure_server_enable(self):
        """配置服务器启用状态"""
        servers = list(self.config.get("servers", {}).keys())
        print(f"\n{Fore.CYAN}选择要配置的服务器:{Style.RESET_ALL}")
        
        for i, name in enumerate(servers, 1):
            config = self.config["servers"][name]
            status = "启用" if config.get("enabled", False) else "禁用"
            print(f"  {i}. {name} ({status})")
        
        try:
            choice = int(input("请输入服务器编号: ")) - 1
            if 0 <= choice < len(servers):
                server_name = servers[choice]
                current_status = self.config["servers"][server_name].get("enabled", False)
                new_status = not current_status
                
                self.enable_server(server_name, new_status)
                status_text = "启用" if new_status else "禁用"
                print(f"{Fore.GREEN}✓ {server_name} 已{status_text}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}无效的服务器编号{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.YELLOW}请输入有效的数字{Style.RESET_ALL}")
    
    def _configure_server_env(self):
        """配置服务器环境变量"""
        enabled_servers = self.get_enabled_servers()
        if not enabled_servers:
            print(f"{Fore.YELLOW}没有启用的服务器{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}选择要配置环境变量的服务器:{Style.RESET_ALL}")
        for i, name in enumerate(enabled_servers, 1):
            print(f"  {i}. {name}")
        
        try:
            choice = int(input("请输入服务器编号: ")) - 1
            if 0 <= choice < len(enabled_servers):
                server_name = enabled_servers[choice]
                server_config = self.get_server_config(server_name)
                
                print(f"\n{server_name} 的环境变量:")
                env_vars = server_config.get("env", {})
                for key, value in env_vars.items():
                    display_value = "***" if "key" in key.lower() or "token" in key.lower() else value
                    print(f"  {key}: {display_value}")
                
                env_key = input(f"\n请输入环境变量名 (如 API_KEY): ").strip()
                if env_key:
                    env_value = input(f"请输入 {env_key} 的值: ").strip()
                    self.set_server_env(server_name, env_key, env_value)
                    print(f"{Fore.GREEN}✓ 环境变量已设置{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}无效的服务器编号{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.YELLOW}请输入有效的数字{Style.RESET_ALL}")
    
    def _configure_auto_start(self):
        """配置自动启动服务器"""
        enabled_servers = self.get_enabled_servers()
        if not enabled_servers:
            print(f"{Fore.YELLOW}没有启用的服务器{Style.RESET_ALL}")
            return
        
        current_auto_start = self.get_auto_start_servers()
        print(f"\n{Fore.CYAN}当前自动启动: {', '.join(current_auto_start) if current_auto_start else '无'}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}启用的服务器:{Style.RESET_ALL}")
        for i, name in enumerate(enabled_servers, 1):
            auto_mark = " (自动启动)" if name in current_auto_start else ""
            print(f"  {i}. {name}{auto_mark}")
        
        choice = input(f"\n请输入要自动启动的服务器编号 (多个用逗号分隔，留空清除): ").strip()
        
        if not choice:
            self.set_auto_start([])
            print(f"{Fore.GREEN}✓ 已清除自动启动设置{Style.RESET_ALL}")
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                auto_start_servers = []
                
                for idx in indices:
                    if 0 <= idx < len(enabled_servers):
                        auto_start_servers.append(enabled_servers[idx])
                
                self.set_auto_start(auto_start_servers)
                print(f"{Fore.GREEN}✓ 自动启动设置: {', '.join(auto_start_servers)}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.YELLOW}请输入有效的数字{Style.RESET_ALL}")
    
    def _add_custom_server(self):
        """添加自定义服务器"""
        print(f"\n{Fore.CYAN}添加自定义MCP服务器{Style.RESET_ALL}")
        
        name = input("服务器名称: ").strip()
        if not name:
            print(f"{Fore.YELLOW}服务器名称不能为空{Style.RESET_ALL}")
            return
        
        description = input("服务器描述: ").strip()
        command_str = input("启动命令 (如: python server.py): ").strip()
        
        if not command_str:
            print(f"{Fore.YELLOW}启动命令不能为空{Style.RESET_ALL}")
            return
        
        command = command_str.split()
        args_str = input("命令参数 (可选): ").strip()
        args = args_str.split() if args_str else []
        
        self.add_custom_server(name, command, args, {}, description)
        print(f"{Fore.GREEN}✓ 自定义服务器 {name} 已添加{Style.RESET_ALL}")

    def convert_mcp_config(self, mcp_servers: Dict[str, Any]) -> Dict[str, Any]:
        """将原始MCP配置转换为我们的内部格式"""
        converted_config = {
            "enabled": True,
            "auto_start": [],
            "servers": {}
        }

        for server_name, server_config in mcp_servers.items():
            # 转换服务器配置
            converted_server = {
                "name": server_name,
                "description": f"{server_name} MCP服务器",
                "enabled": True
            }

            if server_config.get("type") == "sse":
                # SSE类型服务器
                converted_server.update({
                    "type": "sse",
                    "url": server_config.get("url", ""),
                    "command": [],
                    "args": [],
                    "env": {}
                })
            else:
                # 进程类型服务器（默认）
                converted_server.update({
                    "type": "process",
                    "command": server_config.get("command", []),
                    "args": server_config.get("args", []),
                    "env": server_config.get("env", {})
                })

            converted_config["servers"][server_name] = converted_server
            converted_config["auto_start"].append(server_name)

        return converted_config

    def convert_to_original_format(self) -> Dict[str, Any]:
        """将我们的内部格式转换回原始MCP配置格式"""
        original_format = {}

        for server_name, server_config in self.config.get("servers", {}).items():
            if not server_config.get("enabled", False):
                continue

            original_server = {}

            if server_config.get("type") == "sse":
                # SSE类型服务器
                original_server = {
                    "type": "sse",
                    "url": server_config.get("url", "")
                }
            else:
                # 进程类型服务器
                original_server = {
                    "command": server_config.get("command", []),
                    "args": server_config.get("args", []),
                    "env": server_config.get("env", {})
                }

            original_format[server_name] = original_server

        return original_format

# 全局MCP配置实例
mcp_config = MCPConfig()
