# 🔧 MCP (Model Context Protocol) 完整配置和使用指南

## 📍 配置文件位置
您的主配置文件：`C:\Users\李昊宇\.forgeai_config.json`

## 🚀 快速配置

### 1. 在主配置文件中添加MCP配置
将以下内容添加到您的配置文件中：

```json
{
  "api_key": "ms-33a8ba2c-6baf-4a4c-9171-45fcf87b8b65",
  "language": "en-US",
  "model": "gemini-2.5-flash-lite-preview-06-17",
  "prompt_strength": "qwen",
  "mcpServers": {
    "bing-cn-mcp-server": {
      "type": "sse",
      "url": "https://mcp.api-inference.modelscope.net/fd2cb347a7b644/sse"
    }
  }
}
```

### 2. 可选：添加更多MCP服务器
```json
"mcpServers": {
  "bing-cn-mcp-server": {
    "type": "sse",
    "url": "https://mcp.api-inference.modelscope.net/fd2cb347a7b644/sse"
  },
  "filesystem": {
    "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
    "args": ["."],
    "env": {}
  },
  "brave-search": {
    "command": ["npx", "-y", "@modelcontextprotocol/server-brave-search"],
    "args": [],
    "env": {
      "BRAVE_API_KEY": "your-api-key-here"
    }
  }
}
```

## 💻 使用MCP工具

### 基本命令
```xml
<!-- 查看MCP服务器状态 -->
<mcp_server_status></mcp_server_status>

<!-- 列出所有可用工具 -->
<mcp_list_tools></mcp_list_tools>

<!-- 列出所有可用资源 -->
<mcp_list_resources></mcp_list_resources>
```

### 搜索功能
```xml
<!-- 使用Bing中文搜索 -->
<mcp_call_tool><tool>search</tool><arguments>{"query": "人工智能最新发展", "count": 5}</arguments></mcp_call_tool>

<!-- 搜索Python教程 -->
<mcp_call_tool><tool>search</tool><arguments>{"query": "Python教程 2024"}</arguments></mcp_call_tool>
```

### 文件系统操作（如果配置了filesystem服务器）
```xml
<!-- 列出当前目录 -->
<mcp_call_tool><tool>list_directory</tool><arguments>{"path": "."}</arguments></mcp_call_tool>

<!-- 读取文件 -->
<mcp_call_tool><tool>read_file</tool><arguments>{"path": "README.md"}</arguments></mcp_call_tool>
```

## 🔧 支持的MCP服务器类型

### 1. SSE类型（如您的Bing中文服务器）
```json
"server-name": {
  "type": "sse",
  "url": "https://your-sse-endpoint.com/sse"
}
```

### 2. 进程类型（传统MCP服务器）
```json
"server-name": {
  "command": ["npx", "-y", "@modelcontextprotocol/server-name"],
  "args": ["arg1", "arg2"],
  "env": {
    "API_KEY": "your-key"
  }
}
```

## 🎯 常用MCP服务器

### 文件系统操作
```json
"filesystem": {
  "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
  "args": ["."],
  "env": {}
}
```

### Brave搜索（需要API密钥）
```json
"brave-search": {
  "command": ["npx", "-y", "@modelcontextprotocol/server-brave-search"],
  "args": [],
  "env": {
    "BRAVE_API_KEY": "your-brave-api-key"
  }
}
```

### GitHub集成（需要Token）
```json
"github": {
  "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
  "args": [],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "your-github-token"
  }
}
```

### SQLite数据库
```json
"sqlite": {
  "command": ["npx", "-y", "@modelcontextprotocol/server-sqlite"],
  "args": ["path/to/database.db"],
  "env": {}
}
```

## 🔍 故障排除

### 问题1：MCP服务器未启动
**解决方案：**
1. 检查JSON格式是否正确
2. 确认URL是否可访问（SSE类型）
3. 确保Node.js已安装（进程类型）
4. 重启Forge AI Code

### 问题2：工具调用失败
**解决方案：**
1. 使用 `<mcp_list_tools></mcp_list_tools>` 查看可用工具
2. 检查工具名称和参数格式
3. 确认服务器正在运行

### 问题3：搜索无结果
**解决方案：**
1. 检查网络连接
2. 确认搜索查询格式正确
3. 尝试不同的搜索关键词

## 📋 配置模板

### 最小配置（仅Bing中文搜索）
```json
{
  "api_key": "your-api-key",
  "language": "en-US",
  "model": "your-model",
  "prompt_strength": "qwen",
  "mcpServers": {
    "bing-cn-mcp-server": {
      "type": "sse",
      "url": "https://mcp.api-inference.modelscope.net/fd2cb347a7b644/sse"
    }
  }
}
```

### 完整配置（多个服务器）
```json
{
  "api_key": "your-api-key",
  "language": "en-US",
  "model": "your-model",
  "prompt_strength": "qwen",
  "mcpServers": {
    "bing-cn-mcp-server": {
      "type": "sse",
      "url": "https://mcp.api-inference.modelscope.net/fd2cb347a7b644/sse"
    },
    "filesystem": {
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
      "args": ["."],
      "env": {}
    },
    "brave-search": {
      "command": ["npx", "-y", "@modelcontextprotocol/server-brave-search"],
      "args": [],
      "env": {
        "BRAVE_API_KEY": "your-brave-api-key"
      }
    }
  }
}
```

## 🚀 使用流程

1. **配置**：在主配置文件中添加 `mcpServers` 部分
2. **启动**：运行 `forge-ai-code`
3. **验证**：使用 `<mcp_server_status></mcp_server_status>` 检查状态
4. **使用**：通过XML工具调用MCP功能

## 🎯 实际应用示例

### 搜索最新技术信息
```xml
<mcp_call_tool><tool>search</tool><arguments>{"query": "ChatGPT最新更新 2024"}</arguments></mcp_call_tool>
```

### 搜索编程教程
```xml
<mcp_call_tool><tool>search</tool><arguments>{"query": "React Hooks教程"}</arguments></mcp_call_tool>
```

### 搜索新闻资讯
```xml
<mcp_call_tool><tool>search</tool><arguments>{"query": "人工智能发展趋势"}</arguments></mcp_call_tool>
```

---

**配置完成后，您就可以在Forge AI Code中使用强大的MCP功能，包括您的Bing中文搜索服务器！** 🎉

**记住：所有配置都在一个文件中管理，使用XML格式的工具来调用MCP服务。**
