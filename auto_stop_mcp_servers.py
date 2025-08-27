def auto_stop_mcp_servers():
    """自动停止MCP服务器（延迟加载版本）"""
    try:
        from src.lazy_loader import lazy_loader
        from colorama import Fore, Style
        
        # 使用延迟加载器获取MCP组件
        mcp_config = lazy_loader.get_mcp_config()
        mcp_client = lazy_loader.get_mcp_client()
        
        if not mcp_config or not mcp_client:
            # 回退到直接导入
            from src.mcp_config import mcp_config
            from src.mcp_client import mcp_client
        
        # 获取配置的服务器列表
        servers = mcp_config.get_configured_servers()
        
        if not servers:
            print(f"{Fore.YELLOW}没有配置MCP服务器{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}正在停止MCP服务器...{Style.RESET_ALL}")
        
        # 停止所有配置的服务器
        for server_name in servers:
            try:
                mcp_client.stop_server(server_name)
                print(f"{Fore.GREEN}✓ {server_name} 服务器已停止{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}✗ {server_name} 停止失败: {e}{Style.RESET_ALL}")
                
    except Exception as e:
        print(f"{Fore.RED}MCP服务器停止失败: {e}{Style.RESET_ALL}")
