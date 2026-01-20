# WDK Agent Frontend

基于 Vue 3 + Naive UI 的 WDK Agent 前端应用。

## 技术栈

- **Vue 3.4+** - Composition API
- **Vite 5+** - 构建工具
- **TypeScript** - 类型安全
- **Naive UI** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router 4** - 路由管理
- **Axios** - HTTP 客户端
- **dayjs** - 日期处理

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 请求封装
│   │   ├── request.ts    # axios 实例配置
│   │   ├── auth.ts       # 认证 API
│   │   ├── conversation.ts # 对话 API
│   │   ├── agent.ts      # Agent API
│   │   └── tool.ts       # Tool API
│   ├── assets/           # 静态资源
│   │   └── styles/       # 全局样式
│   ├── components/       # 组件
│   │   ├── common/       # 通用组件
│   │   ├── chat/         # 聊天组件
│   │   ├── conversation/ # 对话组件
│   │   └── views/        # 视图组件
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia 状态管理
│   ├── types/            # TypeScript 类型
│   ├── views/            # 页面组件
│   ├── App.vue           # 根组件
│   └── main.ts           # 入口文件
├── .env.development      # 开发环境变量
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 安装依赖

```bash
npm install
```

## 开发运行

```bash
npm run dev
```

访问 http://localhost:5173

默认登录账号：
- 用户名：123
- 密码：123

## 构建生产版本

```bash
npm run build
```

构建产物在 `dist` 目录。

## 功能特性

- ✅ 用户认证（JWT）
- ✅ 对话管理（创建、删除、切换）
- ✅ 消息发送与接收
- ✅ Agent 选择与切换
- ✅ Agents 列表展示
- ✅ Tools 列表展示
- ✅ 响应式布局

## API 对接

前端通过 Vite 代理与后端 API 通信：

```
前端请求 /api/* → Vite 代理 → http://localhost:8080/api/*
```

确保后端服务运行在 `http://localhost:8080`。

## 环境变量

开发环境配置在 `.env.development`：

```
VITE_API_BASE_URL=http://localhost:8080
```
