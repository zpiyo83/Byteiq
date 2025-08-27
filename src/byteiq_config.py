"""
ByteIQ项目配置管理器 - 支持项目特定的AI配置
"""

import os
import json
from pathlib import Path
from colorama import Fore, Style

class ByteIQConfigManager:
    """ByteIQ项目配置管理器"""
    
    def __init__(self):
        self.config_file = "BYTEIQ.md"
        self.config_cache = None
        self.last_modified = None
    
    def find_byteiq_config(self, start_path="."):
        """在项目目录中查找BYTEIQ.md文件"""
        current_path = Path(start_path).resolve()
        
        # 向上查找BYTEIQ.md文件，最多5级目录
        for _ in range(5):
            byteiq_config_path = current_path / self.config_file
            if byteiq_config_path.exists():
                return str(byteiq_config_path)
            
            parent = current_path.parent
            if parent == current_path:  # 已到根目录
                break
            current_path = parent
        
        return None
    
    def load_config(self, force_reload=False):
        """加载BYTEIQ.md配置文件"""
        config_path = self.find_byteiq_config()
        
        if not config_path:
            return None
        
        try:
            # 检查文件修改时间
            current_modified = os.path.getmtime(config_path)
            
            if not force_reload and self.config_cache and self.last_modified == current_modified:
                return self.config_cache
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            config = {
                'file_path': config_path,
                'content': content,
                'rules': self._extract_rules(content),
                'tech_stack': self._extract_tech_stack(content),
                'coding_standards': self._extract_coding_standards(content),
                'project_context': self._extract_project_context(content)
            }
            
            self.config_cache = config
            self.last_modified = current_modified
            
            return config
            
        except Exception as e:
            print(f"{Fore.RED}加载BYTEIQ.md配置失败: {e}{Style.RESET_ALL}")
            return None
    
    def _extract_rules(self, content):
        """提取项目规则"""
        rules = []
        lines = content.split('\n')
        in_rules_section = False
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith('# 规则') or line.lower().startswith('# rules'):
                in_rules_section = True
                continue
            elif line.startswith('# ') and in_rules_section:
                in_rules_section = False
            elif in_rules_section and line:
                if line.startswith('-') or line.startswith('*') or line.startswith('1.'):
                    rules.append(line.lstrip('-*0123456789. '))
        
        return rules
    
    def _extract_tech_stack(self, content):
        """提取技术栈信息"""
        tech_stack = []
        lines = content.split('\n')
        in_tech_section = False
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['技术栈', 'tech stack', 'technology']):
                in_tech_section = True
                continue
            elif line.startswith('# ') and in_tech_section:
                in_tech_section = False
            elif in_tech_section and line:
                if line.startswith('-') or line.startswith('*'):
                    tech_stack.append(line.lstrip('-* '))
        
        return tech_stack
    
    def _extract_coding_standards(self, content):
        """提取编码规范"""
        standards = []
        lines = content.split('\n')
        in_standards_section = False
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['编码规范', 'coding standards', 'code style']):
                in_standards_section = True
                continue
            elif line.startswith('# ') and in_standards_section:
                in_standards_section = False
            elif in_standards_section and line:
                if line.startswith('-') or line.startswith('*'):
                    standards.append(line.lstrip('-* '))
        
        return standards
    
    def _extract_project_context(self, content):
        """提取项目上下文信息"""
        context = {}
        lines = content.split('\n')
        
        # 提取项目描述
        for i, line in enumerate(lines):
            if line.strip().startswith('# ') and i < 10:  # 前10行中的标题作为项目描述
                context['description'] = line.strip('# ').strip()
                break
        
        # 提取其他关键信息
        context['full_content'] = content
        
        return context
    
    def get_config_summary(self):
        """获取BYTEIQ.md配置的摘要信息"""
        config = self.load_config()
        
        if not config:
            return {
                "status": "not_found",
                "config_file": "BYTEIQ.md",
                "message": "未找到项目配置文件"
            }
        
        summary = {
            "status": "found",
            "config_file": config['file_path'],
            "description": config.get('project_context', {}).get('description', ""),
            "rules": config.get('rules', []),
            "tech_stack": config.get('tech_stack', []),
            "coding_standards": config.get('coding_standards', [])
        }
        
        return summary
    
    def get_enhanced_system_prompt(self, base_prompt):
        """获取增强的系统提示词"""
        config = self.load_config()
        
        if not config:
            return base_prompt
        
        # 构建增强提示词
        enhanced_sections = []
        
        # 添加项目上下文
        if config.get('project_context', {}).get('description'):
            enhanced_sections.append(f"# 项目背景\n{config['project_context']['description']}")
        
        # 添加项目规则
        if config.get('rules'):
            rules_text = '\n'.join([f"- {rule}" for rule in config['rules']])
            enhanced_sections.append(f"# 项目规则 (最高优先级)\n{rules_text}")
        
        # 添加技术栈信息
        if config.get('tech_stack'):
            tech_text = '\n'.join([f"- {tech}" for tech in config['tech_stack']])
            enhanced_sections.append(f"# 技术栈\n{tech_text}")
        
        # 添加编码规范
        if config.get('coding_standards'):
            standards_text = '\n'.join([f"- {standard}" for standard in config['coding_standards']])
            enhanced_sections.append(f"# 编码规范\n{standards_text}")
        
        if enhanced_sections:
            project_context = '\n\n'.join(enhanced_sections)
            enhanced_prompt = base_prompt + "\n\n=== 项目配置信息 (来自BYTEIQ.md) ===\n" + project_context
        
        return enhanced_prompt
    
    def create_sample_config(self, path="."):
        """创建示例BYTEIQ.md文件"""
        sample_content = """# ByteIQ AI编程助手项目

这是一个智能CLI AI编程助手项目，旨在提供高效的AI辅助编程体验。

## 规则

- 所有代码必须使用UTF-8编码
- 优先使用Python 3.8+的现代语法特性
- 遵循PEP 8编码规范
- 所有函数和类必须有完整的文档字符串
- 错误处理必须完善，避免程序崩溃
- 保持代码简洁和可读性

## 技术栈

- Python 3.8+
- colorama (终端颜色支持)
- requests (HTTP请求)
- asyncio (异步编程)
- pathlib (路径处理)

## 编码规范

- 使用4个空格缩进
- 行长度不超过88字符
- 变量名使用snake_case
- 类名使用PascalCase
- 常量使用UPPER_CASE
- 导入语句按标准库、第三方库、本地模块分组

## 项目结构

- src/ - 核心模块
- templates/ - 模板文件
- tests/ - 测试文件
- docs/ - 文档文件
"""
        
        byteiq_file = os.path.join(path, self.config_file)
        
        if os.path.exists(byteiq_file):
            print(f"{Fore.YELLOW}BYTEIQ.md文件已存在: {byteiq_file}{Style.RESET_ALL}")
            return False
        
        try:
            with open(byteiq_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            
            print(f"{Fore.GREEN}✓ 已创建示例BYTEIQ.md文件: {byteiq_file}{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}创建BYTEIQ.md文件失败: {e}{Style.RESET_ALL}")
            return False

# 全局配置管理器实例
byteiq_config_manager = ByteIQConfigManager()
