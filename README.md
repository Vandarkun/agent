# WDK Agent Core

基于 LangGraph 和 LangChain 的多智能体框架，提供完整的工具调用、代码执行和 MCP 协议集成能力。

## 项目概述

WDK Agent Core 是一个独立的多智能体运行时系统，从 AgentChat 提取并精简而来。项目实现了基于 ReAct（Reasoning and Acting）范式的智能体架构，支持工具调用、代码沙箱执行、MCP 服务集成等功能。

### 核心特性

- **多种智能体类型**：支持 ReAct、规划-执行、代码执行、MCP 子代理等模式
- **丰富的工具生态**：内置天气查询、网络搜索、arXiv 论文、物流查询、邮件发送等工具
- **MCP 协议支持**：完整集成 Model Context Protocol，支持 SSE、WebSocket、stdio 等传输方式
- **代码沙箱执行**：基于 Pyodide 和 Deno 的安全 Python 代码执行环境
- **灵活的提示词系统**：内置多种场景的提示词模板

## 目录结构

```
wdk_agent/
├── agentchat/                          # 主代码目录
│   ├── config.yaml                     # 全局配置文件
│   ├── settings.py                     # 配置加载模块
│   │
│   ├── core/                           # 核心智能体层
│   │   ├── agents/                     # 各种智能体实现
│   │   │   ├── __init__.py
│   │   │   ├── react_agent.py          # ReAct 智能体
│   │   │   ├── plan_execute_agent.py   # 规划-执行智能体
│   │   │   ├── codeact_agent.py        # 代码执行智能体
│   │   │   ├── mcp_agent.py            # MCP 子代理
│   │   │   └── structured_response_agent.py  # 结构化输出代理
│   │   │
│   │   ├── models/                     # 模型管理层
│   │   │   ├── __init__.py
│   │   │   └── manager.py              # 模型管理器
│   │   │
│   │   └── callbacks/                  # 回调处理
│   │       └── __init__.py
│   │
│   ├── prompts/                        # 提示词模板
│   │   ├── __init__.py
│   │   ├── chat.py                     # 对话提示词
│   │   ├── llm.py                      # LLM 提示词
│   │   ├── mars.py                     # Mars 特定提示词
│   │   ├── lingseek.py                 # LingSeek 特定提示词
│   │   ├── mcp.py                      # MCP 相关提示词
│   │   ├── rewrite.py                  # 重写提示词
│   │   ├── template.py                 # 模板提示词
│   │   └── tool.py                     # 工具提示词
│   │
│   ├── schema/                         # 数据模型定义
│   │   ├── __init__.py
│   │   ├── common.py                   # 通用数据模型
│   │   ├── chat.py                     # 聊天相关模型
│   │   └── mcp.py                      # MCP 配置模型
│   │
│   ├── services/                       # 服务层
│   │   ├── __init__.py
│   │   ├── mcp/                        # MCP 服务
│   │   │   ├── __init__.py
│   │   │   ├── manager.py              # MCP 管理器
│   │   │   ├── multi_client.py         # MCP 多服务器客户端
│   │   │   ├── schema.py               # MCP 数据模型
│   │   │   ├── sessions.py             # MCP 会话管理
│   │   │   └── load_mcp/               # MCP 资源加载
│   │   │       ├── __init__.py
│   │   │       ├── tools.py            # 工具加载
│   │   │       ├── resources.py        # 资源加载
│   │   │       └── prompts.py          # 提示词加载
│   │   │
│   │   └── sandbox/                    # 沙箱服务
│   │       ├── __init__.py
│   │       └── pyodide.py              # Pyodide 沙箱实现
│   │
│   ├── tools/                          # 工具集成
│   │   ├── __init__.py                 # 工具导出
│   │   ├── arxiv/                      # arXiv 论文搜索
│   │   │   ├── __init__.py
│   │   │   └── action.py
│   │   ├── crawl_web/                  # 网页爬取
│   │   │   ├── __init__.py
│   │   │   └── action.py
│   │   ├── delivery/                   # 物流查询
│   │   │   ├── __init__.py
│   │   │   └── action.py
│   │   ├── get_weather/                # 天气查询
│   │   │   ├── __init__.py
│   │   │   └── action.py
│   │   ├── send_email/                 # 邮件发送
│   │   │   ├── __init__.py
│   │   │   └── action.py
│   │   └── web_search/                 # 网络搜索
│   │       ├── __init__.py
│   │       └── bocha_search/
│   │           ├── __init__.py
│   │           └── action.py
│   │
│   └── utils/                          # 工具函数
│       ├── __init__.py
│       ├── convert.py                  # 格式转换工具
│       ├── extract.py                  # 代码提取工具
│       ├── file_utils.py               # 文件操作工具
│       └── helpers.py                  # 辅助函数
│
├── test_agents.py                      # 测试脚本
├── pyproject.toml                      # 项目配置
└── README.md                           # 本文档
```

## 核心模块详解

### 1. 智能体层 (`core/agents/`)

#### ReactAgent (`react_agent.py`)
**功能**：基于 ReAct 范式的基础智能体，实现"推理-行动-观察"循环。

**工作流程**：
```
用户输入 → LLM 推理 → 判断是否需要工具
                    ↓
              需要工具 → 执行工具 → 反馈结果 → LLM 继续推理
                    ↓
              不需要 → 直接回答 → 结束
```

**核心方法**：
- `astream()`: 流式输出，返回模型生成的内容片段
- `ainvoke()`: 一次性执行完整流程并返回最终回复

**状态管理**：
- `messages`: 完整的对话历史
- `tool_call_count`: 工具调用次数计数
- `model_call_count`: 模型调用次数计数

**使用场景**：通用对话、简单工具调用、快速响应场景

---

#### PlanExecuteAgent (`plan_execute_agent.py`)
**功能**：先规划后执行的智能体，适合复杂任务处理。

**工作流程**：
```
用户输入 → 规划阶段（生成结构化计划）
                ↓
            执行阶段（按步骤调用工具）
                ↓
            对话生成（基于结果回复）
```

**核心方法**：
- `_plan_agent_actions()`: 使用 StructuredResponseAgent 生成工具调用计划
- `_execute_agent_actions()`: 按计划逐步执行工具调用
- `astream()` / `ainvoke()`: 流式/非流式调用

**特点**：
- 支持串行和并行工具调用
- 自动处理缺失参数
- 内置 JSON 格式错误修复

**使用场景**：复杂任务、多步骤操作、需要精细控制的场景

---

#### CodeActAgent (`codeact_agent.py`)
**功能**：通过生成和执行 Python 代码来解决问题。

**工作流程**：
```
用户输入 → LLM 生成 Python 代码
                ↓
            Pyodide 沙箱执行代码
                ↓
            捕获输出和变量 → 反馈给 LLM
                ↓
            LLM 继续生成代码或给出答案
```

**核心组件**：
- `PyodideSandbox`: 基于 Deno + Pyodide 的安全执行环境
- 代码块提取和合并机制
- 上下文变量传递

**状态管理**：
- `script`: 即将执行的 Python 代码
- `context`: 执行上下文（包含工具函数和变量）

**使用场景**：数据分析、计算任务、需要编程能力的场景

---

#### MCPAgent (`mcp_agent.py`)
**功能**：针对单个 MCP 服务的子代理。

**核心职责**：
- 加载 MCP 工具并绑定到模型
- 注入用户级配置（如鉴权 token）
- 发送执行事件（中间件支持）

**工作流程**：
```
初始化 → 加载 MCP 工具 → 配置中间件
                        ↓
            ReAct 代理处理工具调用
                        ↓
            注入用户配置 → 执行工具 → 返回结果
```

**使用场景**：需要鉴权的 MCP 服务、事件追踪、子任务处理

---

#### StructuredResponseAgent (`structured_response_agent.py`)
**功能**：包装 LangChain 的结构化输出能力，强制模型按指定 schema 返回结果。

**核心方法**：
- `get_structured_response()`: 返回解析后的结构化数据

**使用场景**：规划阶段、数据解析、需要严格格式的场景

---

### 2. 模型管理层 (`core/models/`)

#### ModelManager (`manager.py`)
**功能**：统一的模型获取接口，支持多模型配置。

**核心方法**：
- `get_tool_invocation_model()`: 获取用于工具调用的模型
- `get_conversation_model()`: 获取用于对话的模型

**配置来源**：从 `app_settings.multi_models` 读取模型配置

---

### 3. 服务层 (`services/`)

#### MCP 服务 (`services/mcp/`)

**核心组件**：

1. **MCPManager (`manager.py`)**
   - 管理多个 MCP 服务器连接
   - 提供工具获取、展示、调用的统一接口
   - 支持并发工具调用

2. **MultiServerMCPClient (`multi_client.py`)**
   - 连接多个 MCP 服务器
   - 加载 LangChain 兼容的工具、提示词和资源
   - 支持动态会话管理

3. **会话管理 (`sessions.py`)**
   - 实现多种传输协议：SSE、WebSocket、stdio、StreamableHttp
   - 提供异步上下文管理器

4. **资源加载 (`load_mcp/`)**
   - `tools.py`: 将 MCP 工具转换为 LangChain 工具
   - `resources.py`: 加载 MCP 资源为 Blob
   - `prompts.py`: 加载 MCP 提示词为消息列表

**支持的传输协议**：
- **SSE**: Server-Sent Events，单向推送
- **WebSocket**: 双向通信
- **stdio**: 标准输入输出，适合本地进程
- **StreamableHttp**: 可流式 HTTP

---

#### 沙箱服务 (`services/sandbox/`)

**PyodideSandbox (`pyodide.py`)**

**功能**：提供安全的 Python 代码执行环境。

**安全特性**：
- 基于 Deno 的安全沙箱
- 精细的权限控制（文件、网络、环境变量等）
- 执行超时限制
- 内存使用监控

**权限配置**：
- `allow_net`: 网络访问控制（支持域名白名单）
- `allow_read`/`allow_write`: 文件系统访问
- `allow_env`: 环境变量访问
- `allow_run`: 子进程执行
- `allow_ffi`: 外部函数接口

**执行模式**：
- **Stateful**: 保持会话状态，变量和导入可复用
- **Stateless**: 每次独立执行

---

### 4. 工具集成 (`tools/`)

#### 内置工具

| 工具名称 | 功能描述 | 文件位置 |
|---------|---------|---------|
| `get_weather` | 天气查询，支持多日预报 | `tools/get_weather/action.py` |
| `bocha_search` | 联网搜索，返回带摘要的结果 | `tools/web_search/bocha_search/action.py` |
| `get_arxiv` | arXiv 论文搜索 | `tools/arxiv/action.py` |
| `get_delivery_info` | 物流单号查询 | `tools/delivery/action.py` |
| `send_email` | 邮件发送 | `tools/send_email/action.py` |

**工具导出**：
- `AgentTools`: 所有工具的列表
- `AgentToolsWithName`: 字典形式的工具映射
- `WeChatTools`: 微信场景使用的工具子集

---

### 5. 提示词系统 (`prompts/`)

**核心提示词**（`chat.py`）：
- `CALL_END_PROMPT`: 工具调用终止指令
- `DEFAULT_CALL_PROMPT`: 默认工具调用提示词
- `SYSTEM_PROMPT`: 系统角色提示词
- `PLAN_CALL_TOOL_PROMPT`: 规划阶段提示词
- `FIX_JSON_PROMPT`: JSON 修复提示词
- `SINGLE_PLAN_CALL_PROMPT`: 单步执行提示词

**场景特定提示词**：
- `mars.py`: Mars 智能体专用
- `lingseek.py`: LingSeek 智能体专用
- `mcp.py`: MCP 服务相关

---

### 6. 数据模型 (`schema/`)

**通用模型**（`common.py`）：
- `ModelConfig`: 模型配置
- `MultiModels`: 多模型配置
- `Tools`: 工具配置

**聊天模型**（`chat.py`）：
- `ToolCall`: 工具调用定义
- `PlanToolFlow`: 规划流程结构

**MCP 模型**（`mcp.py`）：
- `MCPBaseConfig`: MCP 基础配置
- `MCPSSEConfig`: SSE 传输配置
- `MCPWebsocketConfig`: WebSocket 传输配置
- `MCPStreamableHttpConfig`: 可流式 HTTP 配置
- `MCPStdioConfig`: stdio 传输配置

---

### 7. 工具函数 (`utils/`)

**核心工具**：
- `convert.py`: 格式转换（MCP 配置、函数签名等）
- `extract.py`: 代码块提取
- `file_utils.py`: 文件操作
- `helpers.py`: 辅助函数

---

## 功能关联关系图

### 智能体关系图

```
                                用户请求
                                   ↓
        ┌────────────────────────────────────────────┐
        │              智能体选择层                   │
        └────────────────────────────────────────────┘
                    ↓           ↓           ↓
            ┌───────┴──────┐  ┌──┴────┐  ┌──┴──────┐
            │  ReactAgent  │  │ Plan  │  │ CodeAct │
            │   (简单任务)  │  │Execute│  │  Agent  │
            └──────────────┘  │ Agent │  └─────────┘
                             └───────┘
                                   ↓
        ┌────────────────────────────────────────────┐
        │              工具调用层                     │
        │  ┌──────────────────────────────────────┐ │
        │  │  本地工具 (get_weather, search...)   │ │
        │  └──────────────────────────────────────┘ │
        │  ┌──────────────────────────────────────┐ │
        │  │  MCP 工具 (动态加载)                 │ │
        │  │  ┌────────────────────────────────┐ │ │
        │  │  │  MCPAgent (子代理)             │ │ │
        │  │  └────────────────────────────────┘ │ │
        │  └──────────────────────────────────────┘ │
        └────────────────────────────────────────────┘
                                   ↓
        ┌────────────────────────────────────────────┐
        │              服务支持层                     │
        │  - MCPManager (MCP 服务管理)               │
        │  - PyodideSandbox (代码执行)               │
        │  - ModelManager (模型管理)                 │
        └────────────────────────────────────────────┘
                                   ↓
        ┌────────────────────────────────────────────┐
        │              基础设施层                     │
        │  - 配置管理 (settings.py)                  │
        │  - 提示词系统 (prompts/)                   │
        │  - 数据模型 (schema/)                     │
        │  - 工具函数 (utils/)                      │
        └────────────────────────────────────────────┘
```

### 数据流向图

```
配置加载阶段：
config.yaml → settings.py → app_settings
                              ↓
                         ModelManager
                         (模型初始化)

执行阶段：
用户消息 → 智能体 (Agent)
            ↓
         提示词构建 (prompts/)
            ↓
         LLM 调用 (ModelManager)
            ↓
      ┌─────┴─────┐
      ↓           ↓
  需要工具    直接回答
      ↓
  工具查找
  ├─ 本地工具 (tools/)
  └─ MCP 工具 (MCPManager)
      ↓
  工具执行
  ├─ 直接调用
  └─ MCPAgent (带鉴权)
      ↓
  结果反馈 → LLM 继续推理
      ↓
  最终回复
```

### MCP 集成流程

```
MCP 服务器配置
       ↓
MCPManager 初始化
       ↓
连接 MCP 服务器
  ├─ SSE 传输
  ├─ WebSocket 传输
  ├─ stdio 传输
  └─ HTTP 传输
       ↓
加载工具/资源/提示词
       ↓
转换为 LangChain 工具
       ↓
注册到智能体
       ↓
运行时调用
  ├─ 注入用户配置
  ├─ 执行工具
  └─ 返回结果
```

### 代码执行流程（CodeActAgent）

```
用户请求
    ↓
LLM 生成 Python 代码
    ↓
提取代码块 (extract.py)
    ↓
PyodideSandbox 执行
    ├─ 启动 Deno 进程
    ├─ 加载 Pyodide 环境
    ├─ 注入工具函数和变量
    └─ 执行代码
         ↓
    捕获结果
    ├─ stdout (标准输出)
    ├─ 新增变量
    └─ 错误信息
         ↓
    反馈给 LLM
         ↓
    继续生成代码或给出答案
```

## 使用示例

### ReactAgent - 简单工具调用

```python
import asyncio
from langchain_core.messages import HumanMessage
from agentchat.settings import initialize_app_settings
from agentchat.core.agents.react_agent import ReactAgent
from agentchat.core.models.manager import ModelManager
from agentchat.tools import AgentTools

async def main():
    # 初始化配置
    await initialize_app_settings()

    # 获取模型和智能体
    model = ModelManager.get_tool_invocation_model()
    agent = ReactAgent(model=model, tools=AgentTools)

    # 调用智能体
    response = await agent.ainvoke([
        HumanMessage(content="北京明天的天气怎么样？")
    ])
    print(response)

asyncio.run(main())
```

### PlanExecuteAgent - 复杂任务规划

```python
from agentchat.core.agents.plan_execute_agent import PlanExecuteAgent

agent = PlanExecuteAgent(
    user_id="demo",
    tools=AgentTools,
    mcp_servers=[{
        "server_name": "tools",
        "type": "sse",
        "url": "http://localhost:8000/sse"
    }]
)

response = await agent.ainvoke([
    HumanMessage(content="查询单号YT3760955655914的物流信息")
])
```

### CodeActAgent - 代码执行

```python
from agentchat.core.agents.codeact_agent import CodeActAgent

agent = CodeActAgent(tools=AgentTools, user_id="demo")

async for chunk in agent.astream([
    HumanMessage(content="计算斐波那契数列前20项")
]):
    print(chunk, end="")
```

### 流式输出

```python
async for chunk in agent.astream(messages):
    print(chunk, end="", flush=True)
```

## 配置说明

配置文件：`agentchat/config.yaml`

```yaml
# 基础模型配置
multi_models:
  conversation_model:
    api_key: "your-api-key"
    base_url: "https://api.example.com"
    model_name: "model-name"
  tool_call_model:
    api_key: "your-api-key"
    base_url: "https://api.example.com"
    model_name: "model-name"

# 工具配置
tools:
  weather:
    api_key: "weather-api-key"
    endpoint: "https://api.weather.com"
  bocha:
    api_key: "search-api-key"
  delivery:
    api_key: "delivery-api-key"
    endpoint: "https://api.delivery.com"
```

## 模块依赖关系

### 核心依赖链

```
智能体层 (agents/)
    ↓ 依赖
模型管理层 (models/)
    ↓ 依赖
配置层 (settings.py)
    ↓ 依赖
数据模型 (schema/)

智能体层 (agents/)
    ↓ 依赖
工具层 (tools/)
    ↓ 依赖
服务层 (services/)
    ↓ 依赖
工具函数 (utils/)

所有模块
    ↓ 依赖
提示词系统 (prompts/)
```

### 关键导入关系

- `ReactAgent` → `ModelManager`, `AgentTools`, `prompts/`
- `PlanExecuteAgent` → `ModelManager`, `MCPManager`, `StructuredResponseAgent`
- `CodeActAgent` → `ModelManager`, `PyodideSandbox`
- `MCPAgent` → `ModelManager`, `MCPManager`
- `MCPManager` → `MultiServerMCPClient`, `load_mcp/`
- `PyodideSandbox` → `Deno` (外部依赖)

## 扩展开发

### 添加新工具

1. 在 `tools/` 下创建新目录
2. 实现 `action.py`，使用 `@tool` 装饰器
3. 在 `tools/__init__.py` 中导出

### 添加新智能体

1. 在 `core/agents/` 下创建新文件
2. 继承或组合现有智能体
3. 实现标准接口：`astream()`, `ainvoke()`
4. 在 `core/agents/__init__.py` 中导出

### 集成新的 MCP 服务

1. 在 `config.yaml` 中添加 MCP 服务器配置
2. 创建智能体时传入 `mcp_servers` 参数
3. 使用 `MCPManager` 自动加载工具

## 技术栈

- **智能体框架**: LangGraph, LangChain
- **LLM 接口**: OpenAI 兼容 API
- **MCP 协议**: mcp >= 1.20.0
- **代码执行**: Pyodide + Deno
- **日志**: loguru
- **配置**: Pydantic, PyYAML
- **异步**: asyncio

## 设计模式

- **工厂模式**: `ModelManager` 统一创建模型实例
- **策略模式**: 不同智能体实现不同的任务处理策略
- **代理模式**: `MCPAgent` 作为 MCP 工具的代理
- **模板方法**: 智能体的通用执行流程框架
- **适配器模式**: MCP 工具适配为 LangChain 工具
