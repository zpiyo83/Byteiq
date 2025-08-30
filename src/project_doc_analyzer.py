"""
超大型项目分析模式 - 项目文档分析器
独立的AI模式，专门用于分析项目结构并生成完整的接口文档
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from colorama import Fore, Style
from .config import load_config
from .ai_client import ai_client
from .prompt_templates import get_refusal_guidelines

class ProjectDocAnalyzer:
    """项目文档分析器 - 超大型项目分析模式"""
    
    def __init__(self):
        self.config = load_config()
        self.is_active = False
        self.current_project_path = None
        self.analyzed_files = []
        self.file_docs = {}
        self.analysis_order = []
        self.total_files = 0
        self.processed_files = 0
        self.docs_folder = None  # 存储文档的文件夹路径
        self.current_task_batch = []  # 当前任务批次
        self.batch_size = 2  # 每批处理的文件数量
        
    def get_single_file_analyzer_prompt(self):
        """获取单文件分析器的专用系统提示词"""
        return f"""你是ByteIQ项目文件分析器。你的任务是分析文件并输出其函数、变量、类等核心信息。

{get_refusal_guidelines()}

# 🎯 核心职责
你专门负责分析文件，输出：
1. **函数列表** - 所有函数的名称、参数、返回值、作用
2. **类定义** - 所有类的名称、方法、属性
3. **变量定义** - 重要的全局变量、常量、配置
4. **导入依赖** - 文件的导入和依赖关系
5. **文件作用** - 文件的主要功能和用途

# ⚠️ 重要限制
- 你没有工具调用权限，不能使用任何工具
- 只能基于提供的文件内容进行分析
- 必须严格按照指定格式输出
- 不要添加任何额外的说明或解释

# 📋 输出格式要求
请严格按照以下Markdown格式输出，每个文件单独分析：

```markdown
# 文件分析: [文件名]

## 文件作用
[简要描述文件的主要功能和用途]

## 函数列表
### 函数名: function_name
- **参数**: param1 (类型), param2 (类型)
- **返回值**: 返回值类型
- **作用**: 函数的具体作用

## 类定义
### 类名: ClassName
- **作用**: 类的主要功能
- **方法**: method1(), method2()
- **属性**: attr1, attr2

## 变量定义
- **变量名**: 变量作用和值

## 导入依赖
- **导入模块**: 模块名 - 用途

---
```

如果分析多个文件，请为每个文件重复上述格式，用 `---` 分隔。
请只输出分析结果，不要添加其他说明文字。"""

        
    def _create_docs_folder(self):
        """创建文档存储文件夹"""
        project_name = os.path.basename(self.current_project_path)
        self.docs_folder = os.path.join(self.current_project_path, f"{project_name}_analysis_docs")
        
        if not os.path.exists(self.docs_folder):
            os.makedirs(self.docs_folder)
            print(f"{Fore.GREEN}✓ 创建文档文件夹: {self.docs_folder}{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}📁 使用现有文档文件夹: {self.docs_folder}{Style.RESET_ALL}")
    
    def _start_batch_analysis(self):
        """开始批次分析流程"""
        total_batches = (self.total_files + self.batch_size - 1) // self.batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, self.total_files)
            
            batch_files = self.analysis_order[start_idx:end_idx]
            
            print(f"\n{Fore.MAGENTA}📦 开始处理第 {batch_num + 1}/{total_batches} 批次 ({len(batch_files)} 个文件){Style.RESET_ALL}")
            
            # 批量分析文件
            self._analyze_batch_files(batch_files)
            self.processed_files += len(batch_files)
            
            # 显示进度
            progress = (self.processed_files / self.total_files) * 100
            print(f"{Fore.CYAN}📊 进度: {self.processed_files}/{self.total_files} ({progress:.1f}%){Style.RESET_ALL}")
            print(f"{Fore.GREEN}✅ 第 {batch_num + 1} 批次完成{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}🎉 所有文件分析完成！{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📁 分析文档保存在: {self.docs_folder}{Style.RESET_ALL}")
        self.is_active = False
    
    def _analyze_batch_files(self, batch_files: list):
        """批量分析文件"""
        try:
            print(f"{Fore.YELLOW}🔍 批量分析 {len(batch_files)} 个文件{Style.RESET_ALL}")
            
            # 构建批量分析请求
            analysis_prompt = "请分析以下文件的内容：\n\n"
            
            for i, file_path in enumerate(batch_files, 1):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                    
                    file_name = os.path.basename(file_path)
                    analysis_prompt += f"""## 文件 {i}: {file_name}
文件路径: {file_path}

文件内容:
```
{file_content}
```

"""
                except Exception as e:
                    print(f"{Fore.RED}❌ 读取文件 {file_path} 失败: {e}{Style.RESET_ALL}")
                    continue
            
            analysis_prompt += "\n请为每个文件按照指定格式输出分析结果，用 `---` 分隔不同文件的分析。"
            
            # 调用AI进行批量分析
            response = self._call_ai_for_analysis(analysis_prompt)
            
            if response:
                # 解析并保存批量分析结果
                self._save_batch_analysis_results(batch_files, response)
                print(f"{Fore.GREEN}✅ 批次分析完成{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 批次分析失败{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ 批量分析时出错: {e}{Style.RESET_ALL}")
    
    def _call_ai_for_analysis(self, prompt: str) -> str:
        """调用AI进行文件分析"""
        try:
            # 使用单文件分析的系统提示词
            system_prompt = self.get_single_file_analyzer_prompt()
            
            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # 调用AI客户端，禁用工具调用
            response = ai_client.chat_completion(messages, stream=False, tools=None)
            return response
            
        except Exception as e:
            print(f"{Fore.RED}AI分析调用失败: {e}{Style.RESET_ALL}")
            return None
    
    def _save_batch_analysis_results(self, batch_files: list, analysis_result: str):
        """保存批量分析结果到对应的md文件"""
        try:
            # 按 --- 分割分析结果
            file_analyses = analysis_result.split('---')
            
            # 为每个文件保存对应的分析结果
            for i, file_path in enumerate(batch_files):
                if i < len(file_analyses):
                    file_analysis = file_analyses[i].strip()
                    if file_analysis:
                        # 生成md文件名
                        file_name = os.path.basename(file_path)
                        name_without_ext = os.path.splitext(file_name)[0]
                        md_file_name = f"{name_without_ext}.md"
                        md_file_path = os.path.join(self.docs_folder, md_file_name)
                        
                        # 写入分析结果
                        with open(md_file_path, 'w', encoding='utf-8') as f:
                            f.write(file_analysis)
                        
                        print(f"{Fore.CYAN}💾 分析文档已保存: {md_file_name}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}⚠️ 文件 {os.path.basename(file_path)} 的分析结果为空{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️ 文件 {os.path.basename(file_path)} 缺少分析结果{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}保存批量分析结果失败: {e}{Style.RESET_ALL}")
            # 如果批量保存失败，尝试保存整个结果到一个文件
            try:
                fallback_file = os.path.join(self.docs_folder, f"batch_analysis_{int(time.time())}.md")
                with open(fallback_file, 'w', encoding='utf-8') as f:
                    f.write(analysis_result)
                print(f"{Fore.CYAN}💾 批量分析结果已保存到: {os.path.basename(fallback_file)}{Style.RESET_ALL}")
            except Exception as fallback_error:
                print(f"{Fore.RED}备用保存也失败: {fallback_error}{Style.RESET_ALL}")

    def start_analysis(self, project_path: str = None) -> bool:
        """启动项目分析模式"""
        if self.is_active:
            print(f"{Fore.YELLOW}⚠️ 项目分析模式已经在运行中{Style.RESET_ALL}")
            return False
            
        # 确定项目路径
        if not project_path:
            project_path = os.getcwd()
            
        if not os.path.exists(project_path):
            print(f"{Fore.RED}❌ 项目路径不存在: {project_path}{Style.RESET_ALL}")
            return False
            
        self.current_project_path = project_path
        self.is_active = True
        self.analyzed_files = []
        self.file_docs = {}
        
        print(f"{Fore.CYAN}🚀 启动项目文件分析模式{Style.RESET_ALL}")
        print(f"{Fore.WHITE}项目路径: {project_path}{Style.RESET_ALL}")
        
        # 创建文档存储文件夹
        self._create_docs_folder()
        
        # 扫描项目文件
        self._scan_project_files()
        
        if not self.analysis_order:
            print(f"{Fore.YELLOW}⚠️ 未找到可分析的文件{Style.RESET_ALL}")
            self.is_active = False
            return False
            
        print(f"{Fore.GREEN}✓ 发现 {self.total_files} 个文件待分析{Style.RESET_ALL}")
        
        # 计算任务批次
        total_batches = (self.total_files + self.batch_size - 1) // self.batch_size
        print(f"{Fore.CYAN}📋 将分为 {total_batches} 个批次处理，每批最多 {self.batch_size} 个文件{Style.RESET_ALL}")
        
        # 开始批次分析流程
        self._start_batch_analysis()
        
        return True
        
    def _scan_project_files(self):
        """扫描项目文件并确定分析顺序"""
        project_path = Path(self.current_project_path)
        
        # 支持的文件类型
        supported_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            '.md', '.txt', '.rst'
        }
        
        # 忽略的目录
        ignore_dirs = {
            '__pycache__', '.git', '.svn', 'node_modules', '.vscode', '.idea',
            'venv', 'env', '.env', 'build', 'dist', '.pytest_cache'
        }
        
        files_to_analyze = []
        
        for root, dirs, files in os.walk(project_path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in supported_extensions:
                    files_to_analyze.append(str(file_path))
        
        # 按优先级排序文件
        self.analysis_order = self._sort_files_by_priority(files_to_analyze)
        self.total_files = len(self.analysis_order)
        
    def _sort_files_by_priority(self, files: List[str]) -> List[str]:
        """按分析优先级对文件排序"""
        def get_priority(file_path: str) -> int:
            """获取文件分析优先级，数字越小优先级越高"""
            file_path = file_path.lower()
            
            # 配置文件优先级最高
            if any(name in file_path for name in ['config', 'setting', 'setup']):
                return 1
                
            # 主入口文件
            if any(name in file_path for name in ['main', 'app', 'index', '__init__']):
                return 2
                
            # 核心模块
            if any(name in file_path for name in ['core', 'base', 'util', 'common']):
                return 3
                
            # API和接口文件
            if any(name in file_path for name in ['api', 'interface', 'service']):
                return 4
                
            # 模型和数据文件
            if any(name in file_path for name in ['model', 'data', 'entity']):
                return 5
                
            # 控制器和处理器
            if any(name in file_path for name in ['controller', 'handler', 'processor']):
                return 6
                
            # 视图和UI文件
            if any(name in file_path for name in ['view', 'ui', 'component']):
                return 7
                
            # 测试文件优先级较低
            if 'test' in file_path:
                return 9
                
            # 其他文件
            return 8
            
        return sorted(files, key=get_priority)
        
    def _start_analysis_process(self):
        """开始文件分析流程"""
        print(f"\n{Fore.LIGHTCYAN_EX}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}开始项目文档分析 - 共 {self.total_files} 个文件{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}{'='*60}{Style.RESET_ALL}\n")
        
        for i, file_path in enumerate(self.analysis_order, 1):
            self._analyze_single_file(file_path, i)
            
        # 生成最终汇总文档
        self._generate_summary_document()
        
    def _analyze_single_file(self, file_path: str, file_index: int):
        """分析单个文件"""
        print(f"{Fore.CYAN}📄 [{file_index}/{self.total_files}] 分析文件: {file_path}{Style.RESET_ALL}")
        
        try:
            # 构造分析请求
            analysis_request = f"""请分析以下文件并按标准格式输出文档：

文件路径: {file_path}

请使用 read_file 工具读取文件内容，然后按照系统提示词中的标准格式生成完整的接口文档。"""

            # 发送给AI分析
            print(f"{Fore.YELLOW}🤖 AI正在分析文件...{Style.RESET_ALL}")
            
            # 创建分析请求消息，包含系统提示词
            full_request = f"""{self.get_analyzer_system_prompt()}

{analysis_request}"""
            
            try:
                response = ai_client.send_message_streaming(full_request)
                
                if response and response.strip():
                    # 保存分析结果
                    self.file_docs[file_path] = response
                    self.analyzed_files.append(file_path)
                    self.processed_files += 1
                    
                    print(f"{Fore.GREEN}✓ 文件分析完成{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}进度: {self.processed_files}/{self.total_files}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ 文件分析失败: 无响应{Style.RESET_ALL}")
                    
            except Exception as inner_e:
                print(f"{Fore.RED}❌ AI分析过程出错: {str(inner_e)}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ 分析文件时出错: {str(e)}{Style.RESET_ALL}")
            
        print()  # 空行分隔
        
    def _generate_summary_document(self):
        """生成最终的汇总文档"""
        print(f"{Fore.LIGHTCYAN_EX}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}生成项目文档汇总{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}{'='*60}{Style.RESET_ALL}")
        
        # 生成汇总文档内容
        summary_content = self._create_summary_content()
        
        # 保存到文件
        output_file = os.path.join(self.current_project_path, "PROJECT_DOCUMENTATION.md")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
                
            print(f"{Fore.GREEN}✓ 项目文档已生成: {output_file}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📊 分析统计:{Style.RESET_ALL}")
            print(f"  - 总文件数: {self.total_files}")
            print(f"  - 成功分析: {self.processed_files}")
            print(f"  - 失败文件: {self.total_files - self.processed_files}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ 保存文档失败: {str(e)}{Style.RESET_ALL}")
            
        # 结束分析模式
        self.stop_analysis()
        
    def _create_summary_content(self) -> str:
        """创建汇总文档内容"""
        content = f"""# 项目文档汇总

> 由ByteIQ超大型项目分析模式自动生成
> 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
> 项目路径: {self.current_project_path}

## 📊 项目概览

- **总文件数**: {self.total_files}
- **成功分析**: {self.processed_files}
- **分析完成率**: {(self.processed_files/self.total_files*100):.1f}%

## 📁 文件分析结果

"""
        
        # 添加每个文件的分析结果
        for file_path in self.analyzed_files:
            if file_path in self.file_docs:
                content += f"\n{self.file_docs[file_path]}\n"
                content += f"\n{'---'}\n"
                
        content += f"""

## 🔗 项目依赖关系图

[此处可以添加依赖关系图]

## 📝 分析说明

本文档由ByteIQ超大型项目分析模式自动生成，包含了项目中所有重要文件的接口文档和变量说明。

### 分析范围
- Python文件 (.py)
- JavaScript/TypeScript文件 (.js, .ts, .jsx, .tsx)
- 配置文件 (.json, .yaml, .toml等)
- 文档文件 (.md, .txt等)

### 分析顺序
文件按以下优先级进行分析：
1. 配置文件
2. 主入口文件
3. 核心模块
4. API接口文件
5. 数据模型文件
6. 控制器文件
7. 视图文件
8. 其他文件
9. 测试文件

---
*文档生成完成*
"""
        
        return content
        
    def stop_analysis(self):
        """停止项目分析模式"""
        if not self.is_active:
            return
            
        self.is_active = False
        self.current_project_path = None
        print(f"{Fore.YELLOW}📄 项目分析模式已结束{Style.RESET_ALL}")
        
    def get_status(self) -> Dict:
        """获取当前分析状态"""
        return {
            'is_active': self.is_active,
            'project_path': self.current_project_path,
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'progress': f"{self.processed_files}/{self.total_files}" if self.total_files > 0 else "0/0"
        }

# 全局实例
project_doc_analyzer = ProjectDocAnalyzer()
