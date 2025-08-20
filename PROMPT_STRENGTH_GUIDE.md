# 🎯 Forge AI Code - 提示词强度系统指南

## 📋 概述

Forge AI Code 现在支持根据不同AI模型的能力，提供4种不同强度的提示词模板，确保各种模型都能有效工作。

## 🔧 提示词强度级别

### 1. Claude专用 (claude) - 完整强度
- **适用模型**: Claude-3-Haiku, Claude-3-Sonnet, Claude-3-Opus
- **特点**: 提示词最详细完整，包含所有规则和示例
- **长度**: 
  - Ask模式: ~4,563字符
  - Sprint模式: ~3,775字符
- **推荐**: Claude系列模型的最佳选择

### 2. Flash专用 (flash) - 缩减强度  
- **适用模型**: GPT-4-Turbo, GPT-4o, Gemini-Flash等快速模型
- **特点**: 保留核心功能，适度缩减详细说明
- **长度**:
  - Ask模式: ~1,122字符
  - Sprint模式: ~1,305字符
- **推荐**: 快速响应模型的平衡选择

### 3. Qwen Coder专用 (qwen) - 保留关键细节
- **适用模型**: Qwen-Coder, CodeLlama, DeepSeek-Coder等代码专用模型
- **特点**: 专注编程相关指令，保留关键技术细节
- **长度**:
  - Ask模式: ~1,056字符  
  - Sprint模式: ~1,282字符
- **推荐**: 代码专用模型的优化选择

### 4. Mini专用 (mini) - 最简强度
- **适用模型**: GPT-3.5-Turbo, GPT-4o-Mini, Gemini-Nano等轻量模型
- **特点**: 最简化提示词，只保留最重要的规则
- **长度**:
  - Ask模式: ~729字符
  - Sprint模式: ~814字符
- **推荐**: 轻量模型和资源受限环境

## ⚙️ 使用方法

### 1. 通过设置界面配置
```bash
# 启动程序
python forgeai.py

# 进入设置
> /s

# 选择"4 - 设置提示词强度"
# 根据你使用的模型选择合适的强度级别
```

### 2. 配置文件直接修改
```json
{
  "api_key": "your-api-key",
  "model": "gpt-4o-mini", 
  "language": "zh-CN",
  "prompt_strength": "mini"
}
```

## 📊 强度对比表

| 强度级别 | Ask模式长度 | Sprint模式长度 | 适用场景 |
|---------|------------|---------------|----------|
| claude  | 4,563字符   | 3,775字符      | Claude系列，需要详细指导 |
| flash   | 1,122字符   | 1,305字符      | 快速模型，平衡性能 |
| qwen    | 1,056字符   | 1,282字符      | 代码模型，专业编程 |
| mini    | 729字符     | 814字符        | 轻量模型，资源受限 |

## 🎯 模型推荐配置

### Claude系列
```
模型: claude-3-sonnet
强度: claude
说明: 充分利用Claude的理解能力
```

### GPT系列
```
模型: gpt-4o-mini
强度: mini
说明: 轻量模型，简化提示词

模型: gpt-4-turbo  
强度: flash
说明: 快速模型，平衡配置
```

### 代码专用模型
```
模型: qwen-coder
强度: qwen
说明: 专注编程任务的优化配置
```

## 🔄 自动适配建议

根据模型名称自动选择合适的强度：

- 包含"claude"的模型 → claude强度
- 包含"flash"或"turbo"的模型 → flash强度  
- 包含"coder"或"code"的模型 → qwen强度
- 包含"mini"、"nano"、"lite"的模型 → mini强度

## 🧪 测试验证

系统包含完整的测试套件：

```bash
# 运行提示词强度测试
python test_prompt_strength.py
```

测试内容：
- ✅ 所有强度级别的提示词生成
- ✅ 配置系统集成测试
- ✅ AI客户端集成验证
- ✅ 强度对比分析

## 📈 性能优化

不同强度的性能特点：

### Claude强度
- **优点**: 最详细的指导，最佳的任务执行效果
- **缺点**: Token消耗较高，响应时间较长
- **适用**: 复杂任务，需要高质量输出

### Flash强度  
- **优点**: 平衡的性能和效果
- **缺点**: 某些复杂场景可能需要更多指导
- **适用**: 日常开发任务

### Qwen强度
- **优点**: 专注编程，代码质量高
- **缺点**: 非编程任务可能不够详细
- **适用**: 纯代码开发项目

### Mini强度
- **优点**: 最快的响应速度，最低的Token消耗
- **缺点**: 复杂任务可能执行不够完善
- **适用**: 简单任务，快速原型

## 🔧 技术实现

### 核心文件
- `src/prompt_templates.py` - 提示词模板系统
- `src/config.py` - 配置管理（包含强度设置）
- `src/ai_client.py` - AI客户端（集成强度选择）

### 架构设计
```python
# 提示词获取流程
config = load_config()
strength = config.get('prompt_strength', 'claude')
mode = mode_manager.get_current_mode()
prompt = get_prompt_template(mode, strength)
```

## 🚀 未来扩展

计划中的功能：
- [ ] 自动模型检测和强度推荐
- [ ] 用户自定义提示词模板
- [ ] 动态强度调整（根据任务复杂度）
- [ ] 更多模型专用优化

---

**提示**: 选择合适的提示词强度可以显著提升AI的工作效果和响应速度。建议根据实际使用的模型和任务复杂度进行调整。
