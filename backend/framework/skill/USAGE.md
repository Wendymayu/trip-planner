# Skill 系统使用指南

## 概述

Skill 系统支持加载**开源 Skill 格式**（skill.md），并在注册阶段转换为 Tool（早绑定）：
- 先加载元数据（快速）
- 执行时才加载实现（延迟加载）
- 统一通过 ToolRegistry 管理

## 1. 开源 Skill 格式

### 文件夹结构

```
skills/
├── clothing/
│   ├── skill.md          # 元数据和描述（必需）
│   ├── skill.py          # 实现代码（必需）
│   ├── requirements.txt   # 依赖（可选）
│   └── config.json        # 配置（可选）
```

### skill.md 格式

支持 YAML frontmatter 元数据：

```markdown
---
name: clothing
description: 根据天气和活动推荐穿搭
user-invocable: true
license: MIT
metadata:
  version: 1.0.0
  author: Trip Planner Team
  tags: [clothing, travel, weather, recommendation]
---

# Clothing Recommendation Skill

根据给定地点、天气和温度，为用户生成结构化穿搭建议。

## Parameters

- location (string, required): 目的地名称
- weather (string, required): 天气状况（晴、多云、雨、雪等）
- temperature (integer, optional): 温度（摄氏度）
- activity (string, optional): 活动类型（日常、运动、商务等）

## Returns

{
  "location": "string",
  "recommendation": {
    "top": "string",
    "outerwear": "string",
    "accessories": ["string"],
    "tips": ["string"]
  }
}
```

### skill.py 实现

```python
def execute(location: str, weather: str, temperature: int = None) -> dict:
    """推荐穿衣搭配"""
    # 实现逻辑...
    return {
        "location": location,
        "recommendation": {...}
    }
```

## 2. 加载 Skill 并转换为 Tool（推荐）

### 早绑定方式（推荐）

```python
from framework.skill import SkillRegistry
from framework.tools import ToolRegistry

# 创建 Tool 注册表
tool_registry = ToolRegistry()

# 注册普通工具
tool_registry.register(
    name="get_time",
    func=lambda: "2026-05-06 10:30:00",
    description="获取当前时间",
    parameters={"type": "object", "properties": {}, "required": []}
)

# 创建 Skill 加载器并加载 Skills
skill_registry = SkillRegistry()
skill_registry.load_from_directory("./skills")

# 转换为 Tool（早绑定）
skill_registry.register_to_tool(tool_registry)

# 统一通过 ToolRegistry 执行
result = tool_registry.execute("clothing", {"location": "北京", "weather": "晴", "temperature": 30})
```

## 3. 在 Agent 中使用

```python
from framework.llm import LLMClient
from framework.agent import Agent
from framework.skill import SkillRegistry
from framework.tools import ToolRegistry

# 创建 LLM 和 Tool 注册表
llm = LLMClient()
tool_registry = ToolRegistry()

# 加载 Skills 并转换为 Tool
skill_registry = SkillRegistry()
skill_registry.load_from_directory("./skills")
skill_registry.register_to_tool(tool_registry)

# 创建 Agent（只使用 tool_registry）
agent = Agent(
    name="旅行助手",
    llm=llm,
    tool_registry=tool_registry
)

# Agent 会自动调用 Tool
response = agent.act("北京30度晴天，我该穿什么？")
print(response)
```

## 4. 使用 SkillLoader 独立加载

```python
from framework.skill import SkillLoader

loader = SkillLoader()

# 只加载元数据（快速，延迟加载实现）
skill = loader.load_metadata("./skills/clothing")
print(f"Skill: {skill.name}")
print(f"实现已加载: {skill._loaded}")  # False

# 执行时才加载实现
result = skill.execute(location="北京", weather="晴")
print(f"实现已加载: {skill._loaded}")  # True
```

## 5. 最佳实践

### 创建新 Skill

1. 在 `skills/` 目录下创建文件夹（如 `skills/clothing/`）
2. 创建 `skill.md`（包含 YAML frontmatter）
3. 创建 `skill.py`（实现 `execute()` 函数）
4. 可选：添加 `requirements.txt` 和 `config.json`

### 参数定义

在 `skill.md` 中使用标准格式定义参数：

```markdown
## Parameters

- city (string, required): 城市名称
- date (string, optional): 查询日期
- count (integer, optional): 返回数量
```

类型支持：`string`、`integer`、`number`、`boolean`、`array`、`object`

### 错误处理

```python
def execute(city: str) -> dict:
    if not city:
        raise ValueError("城市名称不能为空")

    # 处理逻辑
    return {"city": city, "temp": 25}
```

## 6. 架构说明

```
┌──────────────────────────────────────────────┐
│                    Agent                      │
│                                              │
│   act() → tool_registry.get_openai_tools()   │
│         → tool_registry.execute()            │
└──────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│               ToolRegistry                    │
│                                              │
│   tools: {                                    │
│     "get_time": Tool(func=...),              │
│     "clothing": Tool(func=skill.execute),    │  ← Skill 已转换为 Tool
│   }                                          │
└──────────────────────────────────────────────┘
                       ▲
                       │ register_to_tool_registry()
┌──────────────────────────────────────────────┐
│               SkillRegistry                   │
│                                              │
│   skills: {                                  │
│     "clothing": MetadataSkill(...),          │
│   }                                          │
└──────────────────────────────────────────────┘
```

**早绑定优势：**
- LLM 只看到统一的 Tool schema
- 运行时无需判断类型，直接执行
- Agent 只需持有 tool_registry
- 代码更简洁，性能更好
