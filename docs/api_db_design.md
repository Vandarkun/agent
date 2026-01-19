# WDK Agent 前后端接口与数据库设计

面向最小可用的登录、对话管理、消息发送（每次消息可选不同 Agent 模式）与工具展示。严格限定功能：仅包含登录、新建/查看/删除对话、消息发送、工具列表展示，不扩展注册等其他流程。

## 数据库表结构

### users
- `id` UUID PK
- `username` VARCHAR(64) UNIQUE NOT NULL
- `password_hash` TEXT NOT NULL  // 预置账号，BCrypt/Scrypt 等存储
- `is_active` BOOLEAN DEFAULT TRUE
- `created_at` TIMESTAMPTZ DEFAULT now()

> 无注册流程，账号通过运维/脚本预置。

### user_sessions
- `id` UUID PK
- `user_id` UUID FK → users(id)
- `access_token` TEXT UNIQUE NOT NULL  // 简单 JWT（共享密钥、短过期）或随机字符串
- `expires_at` TIMESTAMPTZ NOT NULL
- `created_at` TIMESTAMPTZ DEFAULT now()
- `revoked_at` TIMESTAMPTZ NULL

### conversations
- `id` UUID PK
- `user_id` UUID FK → users(id)
- `title` VARCHAR(128) NULL
- `created_at` TIMESTAMPTZ DEFAULT now()
- `updated_at` TIMESTAMPTZ DEFAULT now()

### messages
- `id` UUID PK
- `conversation_id` UUID FK → conversations(id) ON DELETE CASCADE
- `role` VARCHAR(16) NOT NULL  // user | agent
- `content` TEXT NOT NULL
- `agent_mode` VARCHAR(32) NOT NULL  // 记录本轮使用的智能体模式
- `created_at` TIMESTAMPTZ DEFAULT now()

## Agent 模式枚举
- `react` → `agentchat.core.agents.react_agent.ReactAgent`
- `plan_execute` → `agentchat.core.agents.plan_execute_agent.PlanExecuteAgent`
- `codeact` → `agentchat.core.agents.codeact_agent.CodeActAgent`

## 后端接口设计（REST）

### 认证
- `POST /api/auth/login`
  - 入参：`{ "username": "...", "password": "..." }`
  - 返回：`{ "access_token": "...", "expires_at": "..." }`
  - 行为：校验 users 表；签发简单 JWT（HS256 共享密钥、短过期即可），写入 user_sessions；无注册、无刷新接口。

### 对话管理
- `POST /api/conversations`
  - Header: `Authorization: Bearer <token>`
  - 入参：`{ "title": "可选" }`
  - 返回：`{ "id": "...", "title": "...", "created_at": "..." }`

- `GET /api/conversations`
  - 返回当前用户未删除的对话列表。

- `DELETE /api/conversations/{id}`
  - 物理删除对话，并通过 FK 级联删除其全部 messages，返回 204。

- `GET /api/conversations/{id}/messages`
  - 支持查询历史消息。

### 消息发送（选择 Agent 模式）
- `POST /api/conversations/{id}/messages`
  - Header: `Authorization`
  - 入参：
    ```json
    {
      "content": "用户提问内容",
      "agent_mode": "plan_execute"  // 必选，每次发送时选择
    }
    ```
  - 响应：`{ "message_id": "...", "conversation_id": "...", "agent_mode": "...", "answer": "..." }`
  - 后端写入 messages 两条记录：一条用户消息（role=user），一条 Agent 回复（role=agent）。

## 工具展示
- `GET /api/tools`
  - 直接读取已有工具定义（如 `agentchat/tools` 目录及 `AgentTools` 导出），返回列表：
    ```json
    [
      { "name": "get_weather", "description": "天气查询" },
      { "name": "bocha_search", "description": "联网搜索" },
      ...
    ]
    ```
  - 无数据库表，实时扫描或缓存读取。

## 前端交互要点
- 登录页：仅用户名/密码；成功后持久化 `access_token`。
- 会话页：
  - 左侧列表：`GET /api/conversations`，支持点击、删除。
  - 新建按钮：调用 `POST /api/conversations`。
  - 工具抽屉/侧栏：调用 `GET /api/tools` 展示工具名称与说明。
  - 聊天区域：顶部/消息框提供 Agent 模式下拉；发送时调用 `POST /api/conversations/{id}/messages`，直接渲染完整回复（不考虑流式）。
- 仅实现上述流程，不包含注册、角色管理、收藏等额外功能。

## 技术栈
后端使用FastAPI
后端代码放入单独文件夹，然后后端代码编写要严格按照分层结构：controller、service、数据库映射层、数据库查询层、乱七八糟工具、各种结构化定义都需要严格分层。
数据库使用SQLLite
前端代码暂不需要