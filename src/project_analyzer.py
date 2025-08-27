"""
项目分析器 - 分析项目结构并生成BYTEIQ.md配置文件
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from colorama import Fore, Style

class ProjectAnalyzer:
    """项目分析器"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.analysis_result = {}
        
    def analyze_project(self) -> Dict[str, Any]:
        """分析项目并返回分析结果"""
        print(f"{Fore.CYAN}🔍 开始分析项目: {self.project_path}{Style.RESET_ALL}")
        
        self.analysis_result = {
            "project_info": self._analyze_project_info(),
            "file_structure": self._analyze_file_structure(),
            "dependencies": self._analyze_dependencies(),
            "code_features": self._analyze_code_features(),
            "project_type": self._detect_project_type(),
            "tech_stack": self._detect_tech_stack(),
        }
        
        print(f"{Fore.GREEN}✓ 项目分析完成{Style.RESET_ALL}")
        return self.analysis_result
    
    def _analyze_project_info(self) -> Dict[str, Any]:
        """分析项目基本信息"""
        info = {
            "name": self.project_path.name,
            "path": str(self.project_path),
            "size": self._calculate_project_size(),
        }
        
        # 查找README文件
        readme_files = list(self.project_path.glob("README*"))
        if readme_files:
            info["readme"] = str(readme_files[0])
            
        return info
    
    def _analyze_file_structure(self) -> Dict[str, Any]:
        """分析文件结构"""
        structure = {
            "total_files": 0,
            "directories": [],
            "file_types": {},
            "main_files": [],
        }
        
        # 忽略的目录
        ignore_dirs = {'.git', '__pycache__', '.vscode', '.idea', 'node_modules', '.env'}
        
        for root, dirs, files in os.walk(self.project_path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            rel_root = os.path.relpath(root, self.project_path)
            if rel_root != '.':
                structure["directories"].append(rel_root)
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                structure["total_files"] += 1
                
                # 统计文件类型
                ext = Path(file).suffix.lower()
                if ext:
                    structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                
                # 识别主要文件
                if file.lower() in ['main.py', 'app.py', 'index.py', 'run.py', '__init__.py']:
                    structure["main_files"].append(os.path.join(rel_root, file))
        
        return structure
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """分析项目依赖"""
        deps = {
            "python": {},
            "javascript": {},
            "other": {}
        }
        
        # Python依赖
        requirements_files = ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile']
        for req_file in requirements_files:
            req_path = self.project_path / req_file
            if req_path.exists():
                deps["python"][req_file] = self._parse_python_deps(req_path)
        
        # JavaScript依赖
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    deps["javascript"]["package.json"] = {
                        "dependencies": package_data.get("dependencies", {}),
                        "devDependencies": package_data.get("devDependencies", {})
                    }
            except Exception:
                pass
        
        return deps
    
    def _parse_python_deps(self, file_path: Path) -> List[str]:
        """解析Python依赖文件"""
        deps = []
        try:
            if file_path.name == 'requirements.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            deps.append(line.split('==')[0].split('>=')[0].split('<=')[0])
            elif file_path.name == 'pyproject.toml':
                # 简单解析pyproject.toml
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'dependencies' in content:
                        deps.append("pyproject.toml配置")
        except Exception:
            pass
        return deps
    
    def _analyze_code_features(self) -> Dict[str, Any]:
        """分析代码特征"""
        features = {
            "languages": set(),
            "frameworks": set(),
            "patterns": set(),
            "imports": set(),
        }
        
        # 分析Python文件
        for py_file in self.project_path.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
                
            features["languages"].add("Python")
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._analyze_python_code(content, features)
            except Exception:
                pass
        
        # 分析其他文件类型
        for js_file in self.project_path.rglob("*.js"):
            features["languages"].add("JavaScript")
        
        for ts_file in self.project_path.rglob("*.ts"):
            features["languages"].add("TypeScript")
            
        for html_file in self.project_path.rglob("*.html"):
            features["languages"].add("HTML")
            
        for css_file in self.project_path.rglob("*.css"):
            features["languages"].add("CSS")
        
        # 转换set为list以便JSON序列化
        for key in features:
            if isinstance(features[key], set):
                features[key] = list(features[key])
        
        return features
    
    def _analyze_python_code(self, content: str, features: Dict[str, Any]):
        """分析Python代码特征"""
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 分析导入
            if line.startswith('import ') or line.startswith('from '):
                if 'flask' in line.lower():
                    features["frameworks"].add("Flask")
                elif 'django' in line.lower():
                    features["frameworks"].add("Django")
                elif 'fastapi' in line.lower():
                    features["frameworks"].add("FastAPI")
                elif 'streamlit' in line.lower():
                    features["frameworks"].add("Streamlit")
                elif 'tkinter' in line.lower():
                    features["frameworks"].add("Tkinter")
                elif 'colorama' in line.lower():
                    features["imports"].add("colorama")
                elif 'requests' in line.lower():
                    features["imports"].add("requests")
                elif 'numpy' in line.lower():
                    features["imports"].add("numpy")
                elif 'pandas' in line.lower():
                    features["imports"].add("pandas")
            
            # 分析模式
            if 'class ' in line and ':' in line:
                features["patterns"].add("面向对象编程")
            if 'async def' in line:
                features["patterns"].add("异步编程")
            if 'if __name__ == "__main__"' in line:
                features["patterns"].add("脚本模式")
    
    def _detect_project_type(self) -> str:
        """检测项目类型"""
        # 检查特定文件存在
        if (self.project_path / 'manage.py').exists():
            return "Django Web应用"
        elif (self.project_path / 'app.py').exists() or any(self.project_path.rglob("*flask*")):
            return "Flask Web应用"
        elif (self.project_path / 'package.json').exists():
            return "Node.js应用"
        elif (self.project_path / 'requirements.txt').exists() or (self.project_path / 'pyproject.toml').exists():
            return "Python应用"
        elif any(self.project_path.rglob("*.py")):
            return "Python项目"
        elif any(self.project_path.rglob("*.js")):
            return "JavaScript项目"
        else:
            return "通用项目"
    
    def _detect_tech_stack(self) -> List[str]:
        """检测技术栈"""
        stack = []
        
        # Python相关
        if any(self.project_path.rglob("*.py")):
            stack.append("Python")
            
        # Web相关
        if any(self.project_path.rglob("*.html")):
            stack.append("HTML")
        if any(self.project_path.rglob("*.css")):
            stack.append("CSS")
        if any(self.project_path.rglob("*.js")):
            stack.append("JavaScript")
            
        # 数据库
        if any(self.project_path.rglob("*.sql")):
            stack.append("SQL")
        if any(self.project_path.rglob("*.db")) or any(self.project_path.rglob("*.sqlite*")):
            stack.append("SQLite")
            
        # 配置文件
        if (self.project_path / 'docker-compose.yml').exists() or (self.project_path / 'Dockerfile').exists():
            stack.append("Docker")
        if (self.project_path / '.git').exists():
            stack.append("Git")
            
        return stack
    
    def _calculate_project_size(self) -> Dict[str, int]:
        """计算项目大小"""
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(self.project_path):
            # 忽略特定目录
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules'}]
            
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except OSError:
                    pass
        
        return {
            "total_bytes": total_size,
            "total_files": file_count,
            "size_mb": round(total_size / (1024 * 1024), 2)
        }
    
    def generate_byteiq_md(self, output_path: Optional[str] = None) -> str:
        """生成BYTEIQ.md配置文件"""
        if not self.analysis_result:
            self.analyze_project()
        
        if output_path is None:
            output_path = self.project_path / "BYTEIQ.md"
        
        content = self._generate_md_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"{Fore.GREEN}✓ BYTEIQ.md 已生成: {output_path}{Style.RESET_ALL}")
        return str(output_path)
    
    def _generate_md_content(self) -> str:
        """生成Markdown内容"""
        info = self.analysis_result["project_info"]
        structure = self.analysis_result["file_structure"]
        features = self.analysis_result["code_features"]
        
        content = f"""# {info['name']} - ByteIQ项目配置

## 项目信息
- **项目类型**: {self.analysis_result['project_type']}
- **技术栈**: {', '.join(self.analysis_result['tech_stack'])}
- **文件总数**: {structure['total_files']}
- **项目大小**: {info['size']['size_mb']} MB

## AI助手配置

### 项目上下文
这是一个{self.analysis_result['project_type']}，主要使用{', '.join(self.analysis_result['tech_stack'])}技术栈。

### 编程语言和框架
- **主要语言**: {', '.join(features['languages']) if features['languages'] else '未检测到'}
- **使用框架**: {', '.join(features['frameworks']) if features['frameworks'] else '无特定框架'}
- **编程模式**: {', '.join(features['patterns']) if features['patterns'] else '标准编程'}

### 项目结构
```
{self._format_directory_structure()}
```

### AI助手规则

1. **代码风格**
   - 遵循项目现有的代码风格和命名规范
   - 保持代码简洁、可读性强
   - 添加适当的注释和文档字符串

2. **技术要求**
   - 优先使用项目已有的技术栈和依赖
   - 确保新代码与现有架构兼容
   - 遵循最佳实践和安全规范

3. **开发流程**
   - 在修改代码前先理解现有实现
   - 提供清晰的修改说明和理由
   - 考虑向后兼容性和性能影响

### 特殊说明
- 这是一个AI辅助编程项目，请特别注意代码的可维护性
- 优先考虑用户体验和系统稳定性
- 在实现新功能时保持现有功能的完整性

### 常用命令和工具
- 主要入口文件: {', '.join(structure['main_files']) if structure['main_files'] else '未检测到'}
- 依赖管理: {'requirements.txt' if 'requirements.txt' in str(self.analysis_result['dependencies']) else '其他方式'}

---
*此配置文件由ByteIQ项目分析器自动生成*
"""
        return content
    
    def _format_directory_structure(self) -> str:
        """格式化目录结构"""
        structure = self.analysis_result["file_structure"]
        dirs = structure["directories"][:10]  # 只显示前10个目录
        
        formatted = f"{self.project_path.name}/\n"
        for directory in sorted(dirs):
            formatted += f"├── {directory}/\n"
        
        if len(structure["directories"]) > 10:
            formatted += f"└── ... (还有 {len(structure['directories']) - 10} 个目录)\n"
        
        return formatted

# 全局项目分析器实例
project_analyzer = ProjectAnalyzer()
