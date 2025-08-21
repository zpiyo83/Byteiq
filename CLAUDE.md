# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Core Architecture

Forge AI Code is a CLI-based AI programming assistant that enables AI to interact with the file system and execute commands. The system is built around several key components:

### Main Entry Point
- `forgeai.py` - The main application entry point that handles user interaction, AI communication, and tool processing

### Core Modules
- `src/ai_client.py` - Handles communication with AI APIs, including conversation history and request/response processing
- `src/ai_tools.py` - Processes AI tool calls and executes file operations, command execution, and task management
- `src/modes.py` - Manages working modes (Ask, mostly accepted, sprint) with different permission levels
- `src/config.py` - Handles configuration management for API keys, models, and settings
- `src/prompt_templates.py` - Manages different prompt strengths for various AI models
- `src/todo_manager.py` - Manages TODO tasks with status tracking and persistence
- `src/mcp_client.py` - Integrates with Model Context Protocol for extended capabilities

## 🛠️ Development Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python forgeai.py
```

### Building Distribution
```bash
python setup.py sdist bdist_wheel
```

### Installing in Development Mode
```bash
pip install -e .
```

## 🎯 Key Features

### AI Tool System
The AI can execute various tools through XML tags:
- `<read_file>` - Read file contents
- `<create_file>` - Create new files
- `<write_file>` - Overwrite existing files
- `<insert_code>` - Insert code at specific line numbers
- `<replace_code>` - Replace code blocks
- `<delete_file>` - Safely delete files
- `<execute_command>` - Run system commands
- `<add_todo>` - Manage task tracking
- `<code_search>` - Search for keywords across the entire project
- `<mcp_call_tool>` - Access extended MCP tools

### Working Modes
1. **Ask Mode** - Read-only, AI can only answer questions and read files
2. **Mostly Accepted** - Read operations auto-executed, write/execute require user confirmation
3. **Sprint Mode** - Full automation, all operations executed without confirmation

### Prompt Strength System
Different prompt templates for various AI models:
- **Claude** - Full strength prompts for Claude models
- **Flash** - Reduced strength for faster models
- **Qwen** - Optimized for code-focused models
- **Mini** - Minimal prompts for lightweight models

## 📁 Project Structure
```
ForgeAI Code/
├── forgeai.py              # Main entry point
├── requirements.txt        # Dependencies
├── setup.py               # Installation configuration
├── pyproject.toml         # Modern Python packaging
├── VERSION.md             # Version history
├── src/                   # Core modules
│   ├── ai_client.py       # AI communication
│   ├── ai_tools.py        # Tool processing
│   ├── modes.py           # Working modes
│   ├── config.py          # Configuration
│   ├── prompt_templates.py # Prompt management
│   ├── todo_manager.py    # Task tracking
│   └── mcp_client.py      # MCP integration
└── todo_data.json         # Persistent task data
```

## 🔧 Tool Call Limitations

1. **Single Tool Per Response** - Each AI response can only execute one tool
2. **Failure Continuation** - Tool failures must be handled by continuing the task, not ending it
3. **Unique End Condition** - Only `task_complete` tool can end a task
4. **Maximum Iterations** - Tasks limited to 50 iterations to prevent infinite loops

## 🎨 Development Guidelines

### Code Style
- Follow existing patterns in the codebase
- Maintain consistent error handling with try/catch blocks
- Use colorama for colored terminal output
- Preserve XML tool call format strictly

### Error Handling
- All tool executions must be wrapped in try/catch
- Failures should generate detailed error information
- Never end tasks due to tool failures
- Always continue processing to allow AI to fix issues

### Security Considerations
- Dangerous commands are blocked (rm -rf, del /f, etc.)
- File operations have mode-based permission controls
- API keys are stored in user's home directory
- User confirmation required for sensitive operations in certain modes