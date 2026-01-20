<template>
  <div class="chat-container">
    <!-- 左侧边栏 - 固定导航 -->
    <AppSidebar />

    <!-- 右侧内容区域 - 动态切换 -->
    <div class="content-area">
      <!-- 对话视图 -->
      <ConversationView v-if="appStore.currentView === 'conversation'" />

      <!-- Agents 列表视图 -->
      <AgentsView v-else-if="appStore.currentView === 'agents'" />

      <!-- Tools 列表视图 -->
      <ToolsView v-else-if="appStore.currentView === 'tools'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useChatStore } from '@/stores/chat'
import { useAgentStore } from '@/stores/agent'
import { useToolStore } from '@/stores/tool'
import AppSidebar from '@/components/common/AppSidebar.vue'
import ConversationView from '@/components/views/ConversationView.vue'
import AgentsView from '@/components/views/AgentsView.vue'
import ToolsView from '@/components/views/ToolsView.vue'

const appStore = useAppStore()
const chatStore = useChatStore()
const agentStore = useAgentStore()
const toolStore = useToolStore()

onMounted(async () => {
  // 加载初始数据
  await Promise.all([
    chatStore.loadConversations(),
    agentStore.loadAgents(),
    toolStore.loadTools()
  ])
})
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
