"""
代理式编程增强模块 - 实现自主规划和执行能力
"""

import json
import time
import re
from typing import List, Dict, Any, Optional
from colorama import Fore, Style

class TaskPlan:
    """任务计划类"""
    
    def __init__(self, task_id: str, description: str, priority: str = "medium"):
        self.task_id = task_id
        self.description = description
        self.priority = priority
        self.status = "pending"  # pending, in_progress, completed, failed
        self.subtasks = []
        self.dependencies = []
        self.created_at = time.time()
        self.started_at = None
        self.completed_at = None
        self.error_count = 0
        self.max_retries = 3
        
    def add_subtask(self, subtask: 'TaskPlan'):
        """添加子任务"""
        self.subtasks.append(subtask)
        
    def add_dependency(self, task_id: str):
        """添加依赖任务"""
        self.dependencies.append(task_id)
        
    def can_execute(self, completed_tasks: set) -> bool:
        """检查是否可以执行（依赖已完成）"""
        return all(dep in completed_tasks for dep in self.dependencies)
        
    def start(self):
        """开始执行任务"""
        self.status = "in_progress"
        self.started_at = time.time()
        
    def complete(self):
        """完成任务"""
        self.status = "completed"
        self.completed_at = time.time()
        
    def fail(self, error: str = ""):
        """任务失败"""
        self.error_count += 1
        if self.error_count >= self.max_retries:
            self.status = "failed"
        else:
            self.status = "pending"  # 重试

class AgentEnhancer:
    """代理式编程增强器"""
    
    def __init__(self):
        self.task_plans = {}
        self.execution_queue = []
        self.completed_tasks = set()
        self.current_task = None
        self.thinking_keywords = ["think", "think hard", "think harder", "ultrathink"]
        self.auto_retry_enabled = True
        self.max_planning_depth = 5
        
    def analyze_user_request(self, user_input: str) -> Dict[str, Any]:
        """分析用户请求，自动生成执行计划"""
        analysis = {
            "complexity": self._assess_complexity(user_input),
            "task_type": self._identify_task_type(user_input),
            "requires_planning": self._requires_planning(user_input),
            "thinking_mode": self._detect_thinking_mode(user_input),
            "estimated_steps": self._estimate_steps(user_input)
        }
        
        return analysis
    
    def _assess_complexity(self, user_input: str) -> str:
        """评估任务复杂度"""
        complexity_indicators = {
            "simple": ["读取", "显示", "查看", "列出", "read", "show", "list"],
            "medium": ["创建", "修改", "添加", "删除", "create", "modify", "add", "delete"],
            "complex": ["构建", "重构", "优化", "调试", "build", "refactor", "optimize", "debug"],
            "very_complex": ["设计", "架构", "系统", "框架", "design", "architecture", "system", "framework"]
        }
        
        user_lower = user_input.lower()
        
        for complexity, keywords in complexity_indicators.items():
            if any(keyword in user_lower for keyword in keywords):
                return complexity
                
        return "medium"  # 默认中等复杂度
    
    def _identify_task_type(self, user_input: str) -> str:
        """识别任务类型"""
        task_types = {
            "file_operation": ["文件", "创建", "修改", "删除", "file", "create", "modify", "delete"],
            "code_generation": ["代码", "函数", "类", "模块", "code", "function", "class", "module"],
            "debugging": ["调试", "错误", "修复", "bug", "debug", "error", "fix", "bug"],
            "analysis": ["分析", "检查", "审查", "analyze", "check", "review"],
            "project_setup": ["项目", "初始化", "配置", "project", "init", "setup", "config"],
            "documentation": ["文档", "注释", "说明", "document", "comment", "documentation"]
        }
        
        user_lower = user_input.lower()
        
        for task_type, keywords in task_types.items():
            if any(keyword in user_lower for keyword in keywords):
                return task_type
                
        return "general"
    
    def _requires_planning(self, user_input: str) -> bool:
        """判断是否需要详细规划"""
        planning_indicators = [
            "构建", "开发", "创建项目", "实现", "设计",
            "build", "develop", "create project", "implement", "design",
            "多个", "复杂", "系统", "完整", "multiple", "complex", "system", "complete"
        ]
        
        user_lower = user_input.lower()
        return any(indicator in user_lower for indicator in planning_indicators)
    
    def _detect_thinking_mode(self, user_input: str) -> str:
        """检测思考模式"""
        user_lower = user_input.lower()
        
        for keyword in reversed(self.thinking_keywords):  # 从最强的开始检查
            if keyword in user_lower:
                return keyword
                
        # 根据复杂度自动选择思考模式
        complexity = self._assess_complexity(user_input)
        if complexity == "very_complex":
            return "ultrathink"
        elif complexity == "complex":
            return "think harder"
        elif complexity == "medium":
            return "think"
        else:
            return "normal"
    
    def _estimate_steps(self, user_input: str) -> int:
        """估算执行步骤数"""
        complexity = self._assess_complexity(user_input)
        
        step_estimates = {
            "simple": 1,
            "medium": 3,
            "complex": 6,
            "very_complex": 10
        }
        
        base_steps = step_estimates.get(complexity, 3)
        
        # 根据关键词调整
        if any(word in user_input.lower() for word in ["多个", "批量", "所有", "multiple", "batch", "all"]):
            base_steps *= 2
            
        return min(base_steps, 15)  # 最多15步
    
    def create_execution_plan(self, user_input: str, analysis: Dict[str, Any]) -> str:
        """创建执行计划"""
        plan_id = f"plan_{int(time.time())}"
        
        if not analysis["requires_planning"]:
            # 简单任务，直接执行
            return self._create_simple_plan(plan_id, user_input, analysis)
        else:
            # 复杂任务，详细规划
            return self._create_detailed_plan(plan_id, user_input, analysis)
    
    def _create_simple_plan(self, plan_id: str, user_input: str, analysis: Dict[str, Any]) -> str:
        """创建简单执行计划"""
        main_task = TaskPlan(
            task_id=f"{plan_id}_main",
            description=user_input,
            priority="high"
        )
        
        self.task_plans[main_task.task_id] = main_task
        self.execution_queue.append(main_task.task_id)
        
        return f"已创建简单执行计划: {user_input}"
    
    def _create_detailed_plan(self, plan_id: str, user_input: str, analysis: Dict[str, Any]) -> str:
        """创建详细执行计划"""
        # 分解任务
        subtasks = self._decompose_task(user_input, analysis)
        
        main_task = TaskPlan(
            task_id=f"{plan_id}_main",
            description=user_input,
            priority="high"
        )
        
        # 创建子任务
        for i, subtask_desc in enumerate(subtasks):
            subtask = TaskPlan(
                task_id=f"{plan_id}_sub_{i}",
                description=subtask_desc,
                priority="medium"
            )
            
            # 设置依赖关系
            if i > 0:
                subtask.add_dependency(f"{plan_id}_sub_{i-1}")
            
            main_task.add_subtask(subtask)
            self.task_plans[subtask.task_id] = subtask
            self.execution_queue.append(subtask.task_id)
        
        self.task_plans[main_task.task_id] = main_task
        
        return f"已创建详细执行计划，包含 {len(subtasks)} 个子任务"
    
    def _decompose_task(self, user_input: str, analysis: Dict[str, Any]) -> List[str]:
        """分解复杂任务"""
        task_type = analysis["task_type"]
        
        decomposition_templates = {
            "code_generation": [
                "分析需求和设计结构",
                "创建基础代码框架",
                "实现核心功能",
                "添加错误处理",
                "编写测试代码",
                "验证和优化"
            ],
            "project_setup": [
                "创建项目目录结构",
                "初始化配置文件",
                "设置依赖管理",
                "创建核心模块",
                "编写文档",
                "测试项目设置"
            ],
            "debugging": [
                "分析错误信息",
                "定位问题源码",
                "设计修复方案",
                "实施修复",
                "验证修复效果"
            ],
            "file_operation": [
                "检查目标路径",
                "备份现有文件",
                "执行文件操作",
                "验证操作结果"
            ]
        }
        
        template = decomposition_templates.get(task_type, [
            "分析任务需求",
            "制定实施方案", 
            "执行核心操作",
            "验证执行结果"
        ])
        
        # 根据估算步骤数调整
        estimated_steps = analysis["estimated_steps"]
        if estimated_steps < len(template):
            # 简化模板
            step_ratio = len(template) / estimated_steps
            simplified = []
            for i in range(estimated_steps):
                index = int(i * step_ratio)
                if index < len(template):
                    simplified.append(template[index])
            return simplified
        
        return template
    
    def get_next_task(self) -> Optional[TaskPlan]:
        """获取下一个可执行的任务"""
        for task_id in self.execution_queue:
            if task_id in self.completed_tasks:
                continue
                
            task = self.task_plans.get(task_id)
            if task and task.status == "pending" and task.can_execute(self.completed_tasks):
                return task
                
        return None
    
    def execute_task(self, task: TaskPlan) -> Dict[str, Any]:
        """执行任务"""
        task.start()
        self.current_task = task
        
        print(f"{Fore.CYAN}🤖 执行任务: {task.description}{Style.RESET_ALL}")
        
        # 这里返回任务信息，由AI工具处理器实际执行
        return {
            "task_id": task.task_id,
            "description": task.description,
            "status": "executing",
            "thinking_mode": self._get_task_thinking_mode(task)
        }
    
    def _get_task_thinking_mode(self, task: TaskPlan) -> str:
        """获取任务的思考模式"""
        # 根据任务复杂度和类型确定思考模式
        if "复杂" in task.description or "complex" in task.description.lower():
            return "think harder"
        elif "分析" in task.description or "analyze" in task.description.lower():
            return "think"
        else:
            return "normal"
    
    def complete_task(self, task_id: str, success: bool = True, error: str = ""):
        """完成任务"""
        task = self.task_plans.get(task_id)
        if not task:
            return
            
        if success:
            task.complete()
            self.completed_tasks.add(task_id)
            print(f"{Fore.GREEN}✓ 任务完成: {task.description}{Style.RESET_ALL}")
        else:
            task.fail(error)
            if task.status == "failed":
                print(f"{Fore.RED}❌ 任务失败: {task.description} - {error}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ 任务重试: {task.description}{Style.RESET_ALL}")
        
        self.current_task = None
    
    def get_execution_status(self) -> Dict[str, Any]:
        """获取执行状态"""
        total_tasks = len(self.task_plans)
        completed_count = len(self.completed_tasks)
        
        pending_tasks = [
            task for task in self.task_plans.values() 
            if task.status == "pending"
        ]
        
        failed_tasks = [
            task for task in self.task_plans.values() 
            if task.status == "failed"
        ]
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_count,
            "pending_tasks": len(pending_tasks),
            "failed_tasks": len(failed_tasks),
            "progress_percent": round((completed_count / total_tasks * 100) if total_tasks > 0 else 0, 1),
            "current_task": self.current_task.description if self.current_task else None
        }
    
    def enhance_prompt_with_thinking(self, prompt: str, thinking_mode: str) -> str:
        """使用思考模式增强提示词"""
        if thinking_mode == "normal":
            return prompt
            
        thinking_instructions = {
            "think": "\n\n请仔细思考这个问题，分析所有相关因素后再回答。",
            "think hard": "\n\n请深入思考这个问题，考虑多种可能的解决方案，权衡利弊后给出最佳答案。",
            "think harder": "\n\n请进行深度分析，从多个角度审视问题，考虑潜在的复杂性和边界情况，提供全面的解决方案。",
            "ultrathink": "\n\n请启动最高级别的深度思考模式：\n1. 全面分析问题的各个维度\n2. 考虑所有可能的解决路径\n3. 评估每种方案的优缺点\n4. 预测潜在的问题和风险\n5. 制定详细的实施计划\n6. 提供最优化的解决方案"
        }
        
        enhancement = thinking_instructions.get(thinking_mode, "")
        return prompt + enhancement
    
    def clear_plans(self):
        """清除所有计划"""
        self.task_plans = {}
        self.execution_queue = []
        self.completed_tasks = set()
        self.current_task = None
        print(f"{Fore.GREEN}✓ 已清除所有执行计划{Style.RESET_ALL}")

# 全局代理增强器实例
agent_enhancer = AgentEnhancer()
