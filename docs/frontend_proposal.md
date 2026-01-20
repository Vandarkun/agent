# WDK Agent 前端技术方案

## 一、技术栈选型

### 核心框架
- **Vue 3.4+** - 使用 Composition API
- **Vite 5+** - 构建工具，开发体验极佳
- **TypeScript** - 类型安全

### UI 框架（二选一）

#### 推荐：Naive UI
```javascript
理由：
✅ 设计更现代，符合 2025 年审美
✅ 组件丰富，文档完善
✅ TypeScript 原生支持
✅ 主题定制灵活
✅ 性能优秀，按需引入
✅ 暗黑模式内置支持
```

#### 备选：Element Plus
```javascript
理由：
✅ 国内使用最广，社区成熟
✅ 中文文档完善
✅ 组件稳定性高
✅ 企业级应用验证充分
```

### 辅助库

```javascript
// 状态管理
Pinia - Vue 3 官方推荐，轻量简洁

// 路由
Vue Router 4 - 官方路由

// HTTP 客户端
axios - 请求拦截、响应拦截、取消请求

// UI 增强
@vueuse/core - Vue Composition API 工具集

// Markdown 渲染
markdown-it + highlight.js - 消息内容渲染

// 代码高亮
highlight.js - 代码块语法高亮

// 样式
UnoCSS / Tailwind CSS - 原子化 CSS（可选）

// 图标
@iconify/vue - 图标库统一

// 工具库
dayjs - 日期处理
lodash-es - 工具函数
```

---

## 二、项目结构设计

```
wdk-agent-frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/                    # API 请求封装
│   │   ├── index.ts            # axios 实例配置
│   │   ├── auth.ts             # 认证相关 API
│   │   ├── chat.ts             # 对话相关 API
│   │   ├── agent.ts            # Agent 相关 API
│   │   └── types.ts            # API 类型定义
│   │
│   ├── assets/                 # 静态资源
│   │   ├── styles/
│   │   │   ├── main.css        # 全局样式
│   │   │   └── variables.css   # CSS 变量
│   │   └── images/
│   │
│   ├── components/             # 通用组件
│   │   ├── common/
│   │   │   ├── AppHeader.vue       # 顶部导航
│   │   │   ├── AppSidebar.vue      # 侧边栏
│   │   │   ├── LoadingSpinner.vue
│   │   │   └── ErrorMessage.vue
│   │   ├── chat/
│   │   │   ├── MessageList.vue         # 消息列表
│   │   │   ├── MessageItem.vue         # 单条消息
│   │   │   ├── ChatInput.vue           # 输入框
│   │   │   ├── AgentSelector.vue       # Agent 下拉选择器
│   │   │   └── StreamingText.vue       # 流式文本组件
│   │   └── conversation/
│   │       ├── ConversationPanel.vue   # 对话列表面板
│   │       ├── ConversationList.vue    # 对话列表
│   │       ├── ConversationItem.vue    # 单个对话
│   │       └── CreateDialog.vue        # 创建对话弹窗
│   │   └── views/
│   │       ├── ConversationView.vue   # 对话视图（消息+输入）
│   │       ├── AgentsView.vue         # Agents 列表视图
│   │       └── ToolsView.vue          # Tools 列表视图
│   │
│   ├── composables/            # 组合式函数
│   │   ├── useAuth.ts          # 认证逻辑
│   │   ├── useChat.ts          # 聊天逻辑
│   │   ├── useAgent.ts         # Agent 选择
│   │   ├── useStream.ts        # 流式请求处理
│   │   └── useStorage.ts       # 本地存储
│   │
│   ├── layouts/                # 布局组件
│   │   ├── BlankLayout.vue     # 空白布局（登录页）
│   │   └── MainLayout.vue      # 主布局
│   │
│   ├── router/                 # 路由配置
│   │   ├── index.ts
│   │   └── guards.ts           # 路由守卫
│   │
│   ├── stores/                 # Pinia 状态管理
│   │   ├── auth.ts             # 认证状态
│   │   ├── chat.ts             # 聊天状态
│   │   ├── agent.ts            # Agent 状态
│   │   ├── tool.ts             # Tool 状态
│   │   ├── app.ts              # 应用全局状态（视图切换）
│   │   └── sidebar.ts          # 侧边栏状态
│   │
│   ├── types/                  # TypeScript 类型
│   │   ├── auth.ts
│   │   ├── chat.ts
│   │   ├── agent.ts
│   │   └── index.ts
│   │
│   ├── utils/                  # 工具函数
│   │   ├── request.ts          # 请求封装
│   │   ├── storage.ts          # 存储封装
│   │   ├── format.ts           # 格式化函数
│   │   └── constant.ts         # 常量定义
│   │
│   ├── views/                  # 页面组件
│   │   ├── Login.vue           # 登录页
│   │   ├── Chat.vue            # 聊天主页
│   │   └── NotFound.vue        # 404 页面
│   │
│   ├── App.vue                 # 根组件
│   └── main.ts                 # 入口文件
│
├── .env.development            # 开发环境变量
├── .env.production             # 生产环境变量
├── .eslintrc.cjs               # ESLint 配置
├── .prettierrc.json            # Prettier 配置
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

---

## 三、核心功能实现方案

### 3.1 认证流程

```
┌─────────────┐
│  访问应用   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 检查 Token  │──┬── 有 Token ──> 验证有效性 ──┬── 有效 ──> 进入主页
└─────────────┘  │                          │
                  │                          └── 无效 ──> 清除，跳登录
                  │
                  └── 无 Token ──> 跳转登录页
```

**实现要点：**
- Token 存储在 `localStorage`
- Axios 拦截器自动添加 `Authorization: Bearer <token>`
- 401 响应自动跳转登录
- 路由守卫 (`beforeEach`) 检查认证状态

### 3.2 对话功能架构

```
┌────────────────────────────────────────────────────────┐
│                      Chat.vue                          │
├──────────────────────┬─────────────────────────────────┤
│      侧边栏          │       右侧内容区域               │
│                      │                                 │
│ ┌────────────────┐  │  ┌─────────────────────────────┐│
│ │ 📝 对话        │  │  │ 当前对话: 天气查询          ││
│ ├────────────────┤  │  ├─────────────────────────────┤│
│ │ [+ 新建对话]  │  │  │ [Agent选择: ReAct 智能体 ▼] ││ ← 切换Agent
│ │ ├─ 天气查询    │  │  ├─────────────────────────────┤│
│ │ ├─ Python学习  │  │  │                             ││
│ │ └─ 数据分析    │  │  │  MessageList                ││
│ └────────────────┘  │  │  - MessageItem              ││
│                      │  │  - MessageItem              ││
│                      │  │  - MessageItem              ││
│                      │  │                             ││
│                      │  └─────────────────────────────┘│
│                      │                                 │
│                      │  ┌─────────────────────────────┐│
│                      │  │  ChatInput                  ││
│                      │  │  [输入框]              [发送]││
│                      │  └─────────────────────────────┘│
└──────────────────────┴─────────────────────────────────┘
```

**布局说明：**

**两栏式布局（左侧固定导航，右侧动态内容切换）：**

1. **左侧栏（固定）** - 侧边栏
   - 对话列表（可折叠）
   - 新建对话按钮
   - 历史对话列表
   - Agents 导航项
   - Tools 导航项

2. **右侧栏（动态切换）** - 内容展示区
   - **状态1：对话视图**（默认）
     - 对话标题
     - Agent 选择器（下拉框，用于切换当前对话使用的 Agent）
     - 消息列表
     - 输入框
   - **状态2：Agents 列表视图**
     - 显示所有 Agent 的完整信息
     - 包含描述、特性、适用场景
   - **状态3：Tools 列表视图**
     - 显示所有 Tool 的完整信息
     - 包含描述、使用说明

**用户操作流程：**

```
1. 默认状态
   左侧：显示对话列表
   右侧：显示当前对话的消息

2. 点击 [+ 新建对话]
   弹出对话框：输入标题（可选）
   创建成功后自动切换到新对话

3. 点击侧边栏的某个对话
   右侧：切换到该对话的消息视图

4. 点击侧边栏的 "🤖 Agents"
   右侧：切换到 Agents 列表视图

5. 点击侧边栏的 "🛠️ Tools"
   右侧：切换到 Tools 列表视图
```

**Agent 切换：**

- **对话视图顶部下拉框** - 切换当前对话使用的 Agent
  - 下拉选择器，显示所有可用 Agent
  - 切换后应用于下一条消息
  - 不离开对话视图

**状态管理（Pinia Store）：**

```typescript
// stores/chat.ts
interface ChatState {
  conversations: Conversation[]      // 对话列表
  currentConversationId: string | null  // 当前对话ID
  messages: Record<string, Message[]>  // 消息缓存（按对话ID）
  currentAgent: string               // 当前选中的 Agent mode
  isLoading: boolean
  error: string | null
}

// 核心方法
- loadConversations()       // 加载对话列表
- createConversation()       // 创建新对话
- deleteConversation(id)    // 删除对话
- loadMessages(conversationId)  // 加载消息
- sendMessage(content, agentMode)  // 发送消息（流式）
- switchConversation(id)    // 切换对话
- setCurrentAgent(mode)     // 设置当前 Agent（从消息区顶部切换）
}

// stores/agent.ts
interface AgentState {
  agents: AgentInfo[]           // 所有可用 Agent
  isLoading: boolean
}

// 核心方法
- loadAgents()                 // 加载 Agent 列表
- getAgentByMode(mode)         // 根据 mode 获取 Agent 信息
}

// stores/tool.ts
interface ToolState {
  tools: ToolInfo[]             // 所有可用工具
  isLoading: boolean
}

// 核心方法
- loadTools()                  // 加载工具列表
}

// stores/sidebar.ts
interface SidebarState {
  isCollapsed: boolean          // 侧边栏是否折叠
}

// 核心方法
- toggleCollapse()             // 切换侧边栏折叠
}
```

**视图切换逻辑：**

```typescript
// stores/app.ts - 应用全局状态
interface AppState {
  currentView: 'conversation' | 'agents' | 'tools'  // 当前右侧显示的视图
}

// 核心方法
- setCurrentView(view)        // 切换右侧视图
- switchToConversation()      // 切换到对话视图
- switchToAgents()           // 切换到 Agents 视图
- switchToTools()            // 切换到 Tools 视图

// views/Chat.vue - 主页面结构
<template>
  <div class="chat-container">
    <!-- 左侧边栏 - 固定导航 -->
    <AppSidebar />

    <!-- 右侧内容区域 - 动态切换 -->
    <div class="content-area">
      <!-- 对话视图 -->
      <ConversationView v-if="currentView === 'conversation'" />

      <!-- Agents 列表视图 -->
      <AgentsView v-else-if="currentView === 'agents'" />

      <!-- Tools 列表视图 -->
      <ToolsView v-else-if="currentView === 'tools'" />
    </div>
  </div>
</template>
```

### 3.3 流式响应处理

**关键技术：**

```typescript
// composables/useStream.ts
export function useStream() {
  async function streamRequest(
    url: string,
    data: any,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
      })

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader!.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        onChunk(chunk)
      }

      onComplete()
    } catch (error) {
      onError(error as Error)
    }
  }

  return { streamRequest }
}
```

**注意事项：**
- 后端需要支持 SSE（Server-Sent Events）
- 前端使用 `fetch` + `ReadableStream`
- 处理网络中断、重连逻辑
- 显示"正在输入..."状态

### 3.4 Agent 选择器

**UI 设计：**

```
┌─────────────────────────────────┐
│  当前使用: ReAct 智能体    ▼   │  ← 下拉选择
├─────────────────────────────────┤
│  📌 ReAct 智能体               │
│  基于 ReAct 范式的基础智能体...  │
│                                 │
│  🎯 规划-执行智能体             │
│  先规划后执行的智能体...         │
│                                 │
│  💻 代码执行智能体              │
│  通过生成和执行 Python...       │
│                                 │
│  🔌 MCP 子代理                  │
│  针对 MCP 服务优化...           │
└─────────────────────────────────┘
```

**实现方案：**
- 使用 `n-select` 或 `n-dropdown`
- 显示 Agent 图标 + 名称 + 简短描述
- 选择后自动应用到下一条消息
- 可设置"默认 Agent"偏好

---

## 四、UI/UX 设计要点

### 4.1 整体风格

```
设计理念：
- 简洁、现代、专业
- 参考 ChatGPT、Claude 界面
- 支持亮色/暗色主题切换
- 响应式设计，支持移动端
```

### 4.2 消息气泡设计

```
┌────────────────────────────────────┐
│ 用户消息                你 20:30  │  ← 右对齐，蓝色
│ ┌──────────────────────────┐      │
│ │ 这是一条用户消息内容      │      │
│ └──────────────────────────┘      │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│ Agent 20:30                        │  ← 左对齐，灰色
│ ┌──────────────────────────┐      │
│ │ 这是 Agent 的回复内容    │      │
│ │ 支持代码高亮、Markdown   │      │
│ └──────────────────────────┘      │
│            [复制] [重新生成]       │
└────────────────────────────────────┘
```

### 4.3 响应式布局

```css
/* 断点设计 */
Mobile:    < 768px   - 单列布局，侧边栏可隐藏，通过抽屉滑出
Tablet:    768-1024 - 两栏布局，侧边栏 240px
Desktop:   > 1024px  - 两栏布局，侧边栏 280px，右侧自适应
```

### 4.4 侧边栏与视图切换 UI 设计

**侧边栏结构：**

```
┌─────────────────────────────────┐
│  ─              [☰]           │  ← 折叠按钮
├─────────────────────────────────┤
│  ┌───────────────────────────┐  │
│  │ 📝 对话          [展开▼]  │  ← 可折叠对话列表
│  ├───────────────────────────┤  │
│  │ [+ 新建对话]             │  │
│  │ ├─ 如何使用 Python?      │  │
│  │ ├─ 天气查询示例          │  │
│  │ └─ 数据分析任务          │  │
│  └───────────────────────────┘  │
│                                 │
│  ┌───────────────────────────┐  │
│  │ 🤖 Agents                │  ← 导航项
│  │    查看所有可用智能体     │  │
│  └───────────────────────────┘  │
│                                 │
│  ┌───────────────────────────┐  │
│  │ 🛠️ Tools                 │  ← 导航项
│  │    查看所有可用工具       │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

**侧边栏组件设计：**

```vue
<!-- components/common/AppSidebar.vue -->
<template>
  <div class="app-sidebar" :class="{ collapsed: isCollapsed }">
    <!-- 折叠按钮 -->
    <div class="sidebar-header">
      <n-button
        text
        size="large"
        @click="toggleCollapse"
      >
        <n-icon :component="isCollapsed ? Menu : ChevronLeft" />
      </n-button>
    </div>

    <!-- 对话列表面板 -->
    <ConversationPanel />

    <!-- 导航项：Agents -->
    <div
      class="nav-item"
      :class="{ active: currentView === 'agents' }"
      @click="switchToAgents"
    >
      <div class="nav-item-content">
        <span class="nav-icon">🤖</span>
        <span class="nav-text">Agents</span>
      </div>
      <n-icon :component="ChevronRight" class="arrow-icon" />
    </div>

    <!-- 导航项：Tools -->
    <div
      class="nav-item"
      :class="{ active: currentView === 'tools' }"
      @click="switchToTools"
    >
      <div class="nav-item-content">
        <span class="nav-icon">🛠️</span>
        <span class="nav-text">Tools</span>
      </div>
      <n-icon :component="ChevronRight" class="arrow-icon" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSidebarStore } from '@/stores/sidebar'
import { useAppStore } from '@/stores/app'
import { Menu, ChevronLeft, ChevronRight } from '@vicons/ionicons5'

const sidebarStore = useSidebarStore()
const appStore = useAppStore()

const isCollapsed = computed(() => sidebarStore.isCollapsed)
const currentView = computed(() => appStore.currentView)

function toggleCollapse() {
  sidebarStore.toggleCollapse()
}

function switchToAgents() {
  appStore.setCurrentView('agents')
  // 移动端自动折叠侧边栏
  if (window.innerWidth < 1024) {
    sidebarStore.setCollapsed(true)
  }
}

function switchToTools() {
  appStore.setCurrentView('tools')
  if (window.innerWidth < 1024) {
    sidebarStore.setCollapsed(true)
  }
}
</script>

<style scoped>
.app-sidebar {
  width: 280px;
  height: 100vh;
  border-right: 1px solid var(--n-border-color);
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  padding: 12px;
  gap: 12px;
}

.app-sidebar.collapsed {
  width: 64px;
}

.nav-item {
  padding: 12px;
  border-radius: 8px;
  background: var(--n-color-modal);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--n-color-target);
}

.nav-item.active {
  background: var(--n-primary-color);
  color: white;
}

.nav-item-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-icon {
  font-size: 20px;
}

.collapsed .nav-text,
.collapsed .arrow-icon {
  display: none;
}

.collapsed .nav-item {
  justify-content: center;
}
</style>
```

**对话视图组件（右侧内容区 - 状态1）：**

```vue
<!-- components/views/ConversationView.vue -->
<template>
  <div class="conversation-view">
    <!-- 顶部：对话标题 + Agent 选择器 -->
    <div class="conversation-header">
      <div class="conversation-info">
        <h2 class="conversation-title">
          {{ currentConversation?.title || '新对话' }}
        </h2>
      </div>

      <div class="agent-selector-wrapper">
        <n-select
          v-model:value="chatStore.currentAgent"
          :options="agentOptions"
          :render-label="renderAgentLabel"
          :render-tag="renderAgentTag"
          placeholder="选择 Agent"
          size="medium"
          style="width: 240px"
          @update:value="handleAgentChange"
        />
      </div>
    </div>

    <!-- 消息列表 -->
    <MessageList class="message-list" />

    <!-- 输入框 -->
    <ChatInput class="chat-input" />
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { NTag, NText } from 'naive-ui'
import { useChatStore } from '@/stores/chat'
import { useAgentStore } from '@/stores/agent'
import MessageList from '@/components/chat/MessageList.vue'
import ChatInput from '@/components/chat/ChatInput.vue'

const chatStore = useChatStore()
const agentStore = useAgentStore()

const currentConversation = computed(() =>
  chatStore.conversations.find(c => c.id === chatStore.currentConversationId)
)

const agentOptions = computed(() =>
  agentStore.agents.map(agent => ({
    label: agent.name,
    value: agent.mode
  }))
)

function renderAgentLabel(option) {
  const agent = agentStore.agents.find(a => a.mode === option.value)
  return h('div', { class: 'agent-option' }, [
    h('span', { class: 'agent-icon' }, getAgentIcon(option.value)),
    h('div', { class: 'agent-info' }, [
      h('div', { class: 'agent-name' }, agent?.name),
      h(NText, { depth: 3, class: 'agent-desc' }, { default: () => agent?.description })
    ])
  ])
}

function renderAgentTag(props) {
  const icon = getAgentIcon(props.option.value)
  return h(NTag, { type: 'info', bordered: false }, {
    default: () => `${icon} ${props.option.label}`
  })
}

function getAgentIcon(mode: string) {
  const icons = { react: '📌', plan_execute: '🎯', codeact: '💻', mcp: '🔌' }
  return icons[mode] || '🤖'
}

function handleAgentChange(mode: string) {
  chatStore.setCurrentAgent(mode)
}
</script>

<style scoped>
.conversation-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--n-border-color);
}

.conversation-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.message-list {
  flex: 1;
  overflow-y: auto;
}

.chat-input {
  border-top: 1px solid var(--n-border-color);
}
</style>
```

**Agents 视图组件（右侧内容区 - 状态2）：**

```vue
<!-- components/views/AgentsView.vue -->
<template>
  <div class="agents-view">
    <div class="view-header">
      <h2>🤖 可用的 Agents</h2>
      <n-p depth="3">选择一个 Agent 了解详情</n-p>
    </div>

    <div class="agents-grid">
      <n-card
        v-for="agent in agents"
        :key="agent.mode"
        class="agent-card"
        :class="{ selected: agent.mode === currentAgent }"
        hoverable
        @click="selectAgent(agent.mode)"
      >
        <template #header>
          <div class="agent-card-header">
            <span class="agent-icon">{{ getAgentIcon(agent.mode) }}</span>
            <span class="agent-name">{{ agent.name }}</span>
          </div>
        </template>

        <n-p depth="3">{{ agent.description }}</n-p>

        <template #footer>
          <div class="agent-footer">
            <n-tag v-if="agent.mode === currentAgent" type="success">
              当前使用
            </n-tag>
            <n-button
              v-else
              type="primary"
              size="small"
              @click.stop="selectAgent(agent.mode)"
            >
              设为当前
            </n-button>
          </div>
        </template>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAgentStore } from '@/stores/agent'
import { useAppStore } from '@/stores/app'
import { useChatStore } from '@/stores/chat'

const agentStore = useAgentStore()
const appStore = useAppStore()
const chatStore = useChatStore()

const agents = computed(() => agentStore.agents)
const currentAgent = computed(() => chatStore.currentAgent)

function getAgentIcon(mode: string) {
  const icons = { react: '📌', plan_execute: '🎯', codeact: '💻', mcp: '🔌' }
  return icons[mode] || '🤖'
}

function selectAgent(mode: string) {
  chatStore.setCurrentAgent(mode)
  // 可选：切换回对话视图
  // appStore.setCurrentView('conversation')
}
</script>

<style scoped>
.agents-view {
  padding: 24px;
  height: 100vh;
  overflow-y: auto;
}

.view-header {
  margin-bottom: 24px;
}

.view-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.agent-card {
  transition: all 0.2s;
}

.agent-card.selected {
  border-color: var(--n-primary-color);
  box-shadow: 0 0 0 2px var(--n-primary-color);
}

.agent-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.agent-icon {
  font-size: 32px;
}

.agent-name {
  font-size: 18px;
  font-weight: 500;
}

.agent-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
```

**Tools 视图组件（右侧内容区 - 状态3）：**

```vue
<!-- components/views/ToolsView.vue -->
<template>
  <div class="tools-view">
    <div class="view-header">
      <h2>🛠️ 可用的 Tools</h2>
      <n-p depth="3">当前系统提供的工具列表</n-p>
    </div>

    <n-list hoverable clickable>
      <n-list-item v-for="tool in tools" :key="tool.name">
        <template #prefix>
          <span class="tool-icon">{{ getToolIcon(tool.name) }}</span>
        </template>

        <div class="tool-content">
          <div class="tool-name">{{ tool.name }}</div>
          <n-p depth="3">{{ tool.description }}</n-p>
        </div>
      </n-list-item>
    </n-list>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useToolStore } from '@/stores/tool'

const toolStore = useToolStore()
const tools = computed(() => toolStore.tools)

function getToolIcon(name: string) {
  const icons = {
    get_weather: '🔍',
    bocha_search: '🌐',
    get_arxiv: '📄',
    get_delivery_info: '📦',
    send_email: '📧'
  }
  return icons[name] || '🔧'
}
</script>

<style scoped>
.tools-view {
  padding: 24px;
  height: 100vh;
  overflow-y: auto;
}

.view-header {
  margin-bottom: 24px;
}

.view-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.tool-icon {
  font-size: 28px;
  margin-right: 12px;
}

.tool-name {
  font-weight: 500;
  margin-bottom: 4px;
}
</style>
```

**主页面结构（Chat.vue）：**

```vue
<!-- views/Chat.vue -->
<template>
  <div class="chat-container">
    <!-- 左侧边栏 - 固定导航 -->
    <AppSidebar />

    <!-- 右侧内容区域 - 动态切换 -->
    <div class="content-area">
      <!-- 对话视图 -->
      <ConversationView v-if="currentView === 'conversation'" />

      <!-- Agents 列表视图 -->
      <AgentsView v-else-if="currentView === 'agents'" />

      <!-- Tools 列表视图 -->
      <ToolsView v-else-if="currentView === 'tools'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import AppSidebar from '@/components/common/AppSidebar.vue'
import ConversationView from '@/components/views/ConversationView.vue'
import AgentsView from '@/components/views/AgentsView.vue'
import ToolsView from '@/components/views/ToolsView.vue'

const appStore = useAppStore()
const currentView = computed(() => appStore.currentView)
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
}

.content-area {
  flex: 1;
  overflow: hidden;
}
</style>
```

**响应式设计：**

```css
/* 桌面端（> 1024px）- 两栏布局 */
@media (min-width: 1024px) {
  .app-sidebar { width: 280px; }
  .content-area { margin-left: 0; }
}

/* 平板端（768-1024px）- 侧边栏可折叠 */
@media (max-width: 1024px) {
  .app-sidebar {
    position: fixed;
    left: 0;
    z-index: 100;
  }

  .app-sidebar.collapsed {
    transform: translateX(-100%);
  }

  .content-area {
    margin-left: 0 !important;
  }
}

/* 移动端（< 768px）- 侧边栏全屏 */
@media (max-width: 768px) {
  .app-sidebar {
    width: 100vw;
  }

  .agents-grid {
    grid-template-columns: 1fr;
  }
}
```

**创建对话弹窗组件：**

```vue
<!-- components/conversation/CreateDialog.vue -->
<template>
  <n-modal
    v-model:show="showDialog"
    :mask-closable="true"
    preset="dialog"
    title="新建对话"
    :positive-text="pending ? '创建中...' : '创建'"
    :negative-text="'取消'"
    :positive-button-props="{ loading: pending }"
    @positive-click="handleCreate"
  >
    <n-form ref="formRef" :model="formData" :rules="rules">
      <n-form-item path="title" label="对话标题（可选）">
        <n-input
          v-model:value="formData.title"
          placeholder="例如：Python 学习、数据分析..."
          @keydown.enter="handleCreate"
        />
      </n-form-item>

      <n-alert type="info" :show-icon="false">
        创建后可在对话视图中选择 Agent 模式
      </n-alert>
    </n-form>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useMessage } from 'naive-ui'
import { useChatStore } from '@/stores/chat'

const emit = defineEmits(['created'])

const message = useMessage()
const chatStore = useChatStore()

const showDialog = defineModel<boolean>('show', { default: false })
const pending = ref(false)

const formData = reactive({
  title: ''
})

const rules = {
  // title 不是必填的，所以没有验证规则
}

async function handleCreate() {
  try {
    pending.value = true

    // 创建对话（只传递 title，不需要选择 agent）
    const conversation = await chatStore.createConversation({
      title: formData.title || undefined  // 空标题传 undefined
    })

    message.success('对话创建成功')

    // 重置表单
    formData.title = ''
    showDialog.value = false

    // 切换到新创建的对话
    await chatStore.switchConversation(conversation.id)

    // 通知父组件
    emit('created', conversation)
  } catch (error) {
    message.error('创建失败：' + error.message)
  } finally {
    pending.value = false
  }
}
</script>

<style scoped>
:deep(.n-alert) {
  margin-top: 12px;
}
</style>
```

**对话列表面板中的使用：**

```vue
<!-- components/conversation/ConversationPanel.vue -->
<template>
  <div class="conversation-panel">
    <div class="panel-header">
      <span class="panel-title">📝 对话</span>
      <n-button
        text
        size="small"
        @click="showCreateDialog = true"
      >
        <template #icon>
          <n-icon :component="AddOutline" />
        </template>
        新建
      </n-button>
    </div>

    <div v-if="!isCollapsed" class="conversation-list">
      <ConversationItem
        v-for="conv in conversations"
        :key="conv.id"
        :conversation="conv"
        :is-active="conv.id === currentConversationId"
        @click="handleSelectConversation"
      />

      <n-empty
        v-if="conversations.length === 0"
        description="暂无对话"
        size="small"
      />
    </div>

    <!-- 创建对话弹窗 -->
    <CreateDialog
      v-model:show="showCreateDialog"
      @created="handleConversationCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { AddOutline } from '@vicons/ionicons5'
import { useChatStore } from '@/stores/chat'
import { useSidebarStore } from '@/stores/sidebar'
import ConversationItem from './ConversationItem.vue'
import CreateDialog from './CreateDialog.vue'

const chatStore = useChatStore()
const sidebarStore = useSidebarStore()

const showCreateDialog = ref(false)

const conversations = computed(() => chatStore.conversations)
const currentConversationId = computed(() => chatStore.currentConversationId)
const isCollapsed = computed(() => sidebarStore.isCollapsed)

function handleSelectConversation(conv: any) {
  chatStore.switchConversation(conv.id)
  // 移动端选择后自动折叠
  if (window.innerWidth < 1024) {
    sidebarStore.setCollapsed(true)
  }
}

function handleConversationCreated(conv: any) {
  // 对话创建后的处理（已在弹窗中处理切换）
  console.log('Conversation created:', conv)
}
</script>

<style scoped>
.conversation-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
}

.panel-title {
  font-weight: 500;
  font-size: 14px;
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
</style>
```

**创建对话流程：**

```
用户操作流程：

1. 点击侧边栏 [+ 新建对话]
   ↓
2. 弹出对话框：输入标题（可选）
   ↓
3. 点击"创建"按钮
   ↓
4. API 调用 POST /api/conversations { title?: string }
   ↓
5. 创建成功，自动切换到新对话
   ↓
6. 用户在对话视图顶部的下拉框选择 Agent
   ↓
7. 开始发送消息
```

**关键点：**
- ✅ 创建对话时**只需要标题**（title 是可选的）
- ✅ **不需要选择 Agent**
- ✅ Agent 选择在对话视图顶部，创建后再选
- ✅ 创建后自动切换到新对话，方便直接开始

**交互效果：**

1. **侧边栏折叠** - 平滑宽度/transform 动画
2. **视图切换** - 无动画，直接切换内容
3. **移动端优化** - 侧边栏折叠后自动显示汉堡菜单
4. **卡片选中状态** - 当前使用的 Agent 高亮显示
5. **加载骨架屏** - 数据加载时显示占位
6. **弹窗创建** - 支持回车键快速创建，创建后自动切换到新对话

---

## 五、API 对接方案

### 5.1 API 封装结构

```typescript
// api/index.ts
import axios from 'axios'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080',
  timeout: 30000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Token 过期，跳转登录
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default request
```

### 5.2 API 模块划分

```typescript
// api/auth.ts
export function login(data: { username: string; password: string }) {
  return request.post('/api/auth/login', data)
}

// api/chat.ts
export function getConversations() {
  return request.get<Conversation[]>('/api/conversations')
}

export function createConversation(data: { title?: string }) {
  return request.post<Conversation>('/api/conversations', data)
}

export function deleteConversation(id: string) {
  return request.delete(`/api/conversations/${id}`)
}

export function getMessages(conversationId: string, params?: { limit?: number; offset?: number }) {
  return request.get<MessagesPage>(`/api/conversations/${conversationId}/messages`, { params })
}

export function sendMessage(conversationId: string, data: { content: string; agent_mode: string }) {
  // 返回流式响应
  return fetch(`${baseURL}/api/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify(data)
  })
}

// api/agent.ts
export function getAgents() {
  return request.get<AgentInfo[]>('/api/agents')
}

// api/tool.ts
export function getTools() {
  return request.get<ToolInfo[]>('/api/tools')
}
```

### 5.3 类型定义

```typescript
// api/types.ts
export interface User {
  id: string
  username: string
}

export interface Conversation {
  id: string
  title: string | null
  created_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'agent'
  content: string
  agent_mode: string
  created_at: string
}

export interface MessagesPage {
  items: Message[]
  total: number
}

export interface AgentInfo {
  mode: string
  name: string
  description: string | null
}

export interface ToolInfo {
  name: string
  description: string | null
}

export interface LoginResponse {
  access_token: string
  expires_at: string
}
```

---

## 六、开发计划

### Phase 1: 基础框架（1-2天）
- [x] 初始化项目
- [x] 配置 Vite + Vue 3 + TypeScript
- [x] 集成 Naive UI
- [x] 配置路由和状态管理
- [x] 实现登录页

### Phase 2: 对话功能（3-4天）
- [ ] 实现对话列表
- [ ] 实现消息列表
- [ ] 实现发送消息
- [ ] 实现流式响应
- [ ] 实现 Markdown 渲染
- [ ] 实现代码高亮

### Phase 3: Agent & Tool 功能（2-3天）
- [ ] Agent 列表获取
- [ ] Agent 信息面板组件
- [ ] Agent 选择器组件
- [ ] Tool 列表获取
- [ ] Tool 信息面板组件
- [ ] 侧边栏面板切换逻辑
- [ ] 应用 Agent 选择

### Phase 4: 优化完善（2-3天）
- [ ] 主题切换
- [ ] 响应式适配
- [ ] 错误处理
- [ ] 加载状态
- [ ] 性能优化

### Phase 5: 测试部署（1-2天）
- [ ] 单元测试
- [ ] E2E 测试
- [ ] 构建优化
- [ ] 部署上线

**总计：8-13 天**

---

## 七、部署方案

### 7.1 构建配置

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'ui': ['naive-ui'],
        }
      }
    }
  }
})
```

### 7.2 部署选项

**选项1：静态托管（推荐）**
```bash
# 构建静态文件
npm run build

# 部署到 Nginx
cp -r dist/* /var/www/html/

# Nginx 配置
location / {
  try_files $uri $uri/ /index.html;
}

location /api {
  proxy_pass http://localhost:8080;
}
```

**选项2：Docker**
```dockerfile
# Dockerfile
FROM node:20-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

**选项3：Vercel/Netlify**
- 连接 Git 仓库
- 自动构建部署
- 推荐 Vercel（国内访问快）

---

## 八、技术难点与解决方案

### 8.1 流式响应断点续传

**问题：** 网络中断导致流式响应丢失

**方案：**
```typescript
// 实现简单的重连机制
let retryCount = 0
const MAX_RETRY = 3

async function fetchWithRetry(url, options) {
  while (retryCount < MAX_RETRY) {
    try {
      return await fetch(url, options)
    } catch (error) {
      retryCount++
      if (retryCount >= MAX_RETRY) throw error
      await new Promise(resolve => setTimeout(resolve, 1000 * retryCount))
    }
  }
}
```

### 8.2 大量消息渲染性能

**问题：** 对话消息过多导致页面卡顿

**方案：**
```vue
<!-- 使用虚拟滚动 -->
<template>
  <VirtualScroller
    :items="messages"
    :item-height="80"
    :buffer="200"
  >
    <template #default="{ item }">
      <MessageItem :message="item" />
    </template>
  </VirtualScroller>
</template>

<!-- 或使用分页加载 -->
// 首次加载 50 条
// 滚动到顶部时加载更多
```

### 8.3 Markdown 安全渲染

**问题：** XSS 攻击风险

**方案：**
```typescript
import markdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const md = markdownIt()
function safeRender(markdown: string) {
  const html = md.render(markdown)
  return DOMPurify.sanitize(html)
}
```

---

## 九、后续扩展方向

### 9.1 功能扩展
- [ ] Agent 配置页面（自定义参数）
- [ ] 文件上传（图片、PDF）
- [ ] 语音输入/输出
- [ ] 导出对话（Markdown、PDF）
- [ ] 对话分享功能
- [ ] 使用统计和分析

### 9.2 体验优化
- [ ] 快捷键支持
- [ ] 对话搜索
- [ ] 标签/分类管理
- [ ] 多语言支持
- [ ] PWA 离线支持

---

## 十、参考资源

### 官方文档
- [Vue 3 文档](https://cn.vuejs.org/)
- [Vite 文档](https://cn.vitejs.dev/)
- [Naive UI 文档](https://www.naiveui.com/zh-CN)
- [Pinia 文档](https://pinia.vuejs.org/zh/)

### 开源项目参考
- [ChatGPT-Next-Web](https://github.com/Yidadaa/ChatGPT-Next-Web) - 优秀的 ChatGPT 界面实现
- [Lobe Chat](https://github.com/lobehub/lobe-chat) - 现代化聊天框架
- [Vue Vben Admin](https://github.com/vbenjs/vue-vben-admin) - Vue 3 后台管理模板

### UI 设计参考
- [ChatGPT](https://chat.openai.com/)
- [Claude](https://claude.ai/)
- [Naive UI Admin](https://www.naiveui.com/en-US/os-theme)

---

## 十一、总结

**推荐技术栈：**
- Vue 3 + TypeScript + Vite
- Naive UI（首选）或 Element Plus
- Pinia + Vue Router
- Axios + Fetch

**核心优势：**
✅ 开发效率高，2 周可上线
✅ 代码质量好，类型安全
✅ 用户体验好，响应迅速
✅ 可维护性强，易于扩展

**适用场景：**
- 面向国内用户的产品
- 团队熟悉 Vue 技术栈
- 需要快速迭代开发

---

**文档版本：** v1.3
**创建时间：** 2025-01-20
**最后更新：** 2025-01-20
**维护者：** WDK Team

**更新日志：**
- v1.3 (2025-01-20)
  - **优化创建对话流程**：创建对话时只需要标题（可选），不需要选择 Agent
  - Agent 选择在对话视图顶部的下拉框中进行
  - 创建后自动切换到新对话，方便直接开始
  - 保留完整的视图切换功能（对话、Agents、Tools）

- v1.2 (2025-01-20)
  - **重大调整**：重新设计为两栏布局架构
  - 左侧侧边栏：导航菜单（对话列表、Agents 导航、Tools 导航）
  - 右侧内容区：动态视图切换（ConversationView、AgentsView、ToolsView）
  - Agent 切换功能位于对话视图顶部（下拉选择器）
  - 优化交互流程：侧边栏导航 → 右侧视图切换
  - 新增视图组件（views/ConversationView.vue、views/AgentsView.vue、views/ToolsView.vue）
  - 更新状态管理（app.ts 添加 currentView 状态）
  - 移除旧的三栏 + 滑出面板设计

- v1.1 (2025-01-20)
  - 增加侧边栏详细设计
  - 增加 Agent 和 Tool 信息面板组件设计
  - 增加侧边栏响应式设计和交互效果
  - 增加相关 Store 和 API 接口定义

- v1.0 (2025-01-20)
  - 初始版本
  - 完成技术栈选型和基础架构设计
