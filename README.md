# WDK Agent

一个完整的多智能体聊天系统，包含后端 Agent 引擎与前端聊天界面，支持工具调用与流式回复展示。

## 特性

- 多种 Agent 模式：ReAct / Plan-Execute / CodeAct / MCP
- 统一会话与消息管理（创建、删除、切换）
- 工具调用与 MCP 工具接入
- 流式输出（前端逐段展示生成回复）
- 前后端分离，便于独立部署

## 技术栈

- 后端：FastAPI + SQLAlchemy + LangChain/LangGraph
- 前端：Vue 3 + Vite + TypeScript + Naive UI + Pinia
- 数据库：SQLite（默认）

## 目录结构

```
.
├── agentchat/          # 核心智能体与工具实现
├── api/                # FastAPI 后端
├── database/           # SQLite 数据文件
├── frontend/           # Vue 前端
├── docs/               # 设计与说明文档
└── run_api.py          # 后端启动入口
```

## 快速开始

### 1) 后端

准备好 Python 环境并安装依赖后，启动后端：

```bash
python run_api.py
```

默认监听 `http://localhost:8080`。

### 2) 前端

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:8082`。

默认登录账号：

- 用户名：`123`
- 密码：`123`

## 配置

模型与工具的配置位于 `agentchat/config.yaml`，请替换为你自己的密钥与模型地址。

```yaml
multi_models:
  conversation_model:
    api_key: "YOUR_API_KEY"
    base_url: "YOUR_BASE_URL"
    model_name: "YOUR_MODEL"
  tool_call_model:
    api_key: "YOUR_API_KEY"
    base_url: "YOUR_BASE_URL"
    model_name: "YOUR_MODEL"
```

## 流式回复

前端通过流式接口实时显示回复片段：

```
POST /api/conversations/{conversation_id}/messages/stream
```

前端在 `frontend/src/api/conversation.ts` 中使用 `fetch` + `ReadableStream` 读取增量内容。

## 相关文档

- 前端说明：`frontend/README.md`
- API/DB 设计：`docs/api_db_design.md`

## License

MIT
