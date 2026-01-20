<template>
  <div class="conversation-panel">
    <!-- 可点击的标题栏 -->
    <div class="panel-header" @click="toggleExpanded">
      <div class="header-left">
        <n-icon :component="isExpanded ? ChevronDown : ChevronForward" class="expand-icon" />
        <span class="panel-title">📝 对话</span>
      </div>
      <n-button
        v-if="isExpanded"
        text
        size="small"
        @click.stop="showCreateDialog = true"
      >
        <template #icon>
          <n-icon :component="AddOutline" />
        </template>
        新建
      </n-button>
    </div>

    <!-- 对话列表 -->
    <div v-if="!sidebarStore.isCollapsed && isExpanded" class="conversation-list">
      <ConversationItem
        v-for="conv in chatStore.conversations"
        :key="conv.id"
        :conversation="conv"
        :is-active="conv.id === chatStore.currentConversationId"
        @click="handleSelectConversation(conv)"
        @delete="handleDeleteConversation(conv.id)"
      />

      <n-empty v-if="chatStore.conversations.length === 0" description="暂无对话" size="small" />
    </div>

    <!-- 创建对话弹窗 -->
    <CreateDialog v-model:show="showCreateDialog" @created="handleConversationCreated" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AddOutline, ChevronDown, ChevronForward } from '@vicons/ionicons5'
import { useChatStore } from '@/stores/chat'
import { useSidebarStore } from '@/stores/sidebar'
import { useAppStore } from '@/stores/app'
import ConversationItem from './ConversationItem.vue'
import CreateDialog from './CreateDialog.vue'
import type { Conversation } from '@/types'

const chatStore = useChatStore()
const sidebarStore = useSidebarStore()
const appStore = useAppStore()

const showCreateDialog = ref(false)
const isExpanded = ref(true) // 对话面板展开/折叠状态

function toggleExpanded() {
  isExpanded.value = !isExpanded.value
}

async function handleSelectConversation(conv: Conversation) {
  await chatStore.switchConversation(conv.id)
  // 切换回对话视图
  appStore.switchToConversation()
  // 移动端选择后自动折叠
  if (window.innerWidth < 1024) {
    sidebarStore.setCollapsed(true)
  }
}

async function handleDeleteConversation(id: string) {
  try {
    await chatStore.deleteConversation(id)
  } catch (error) {
    // 错误已在 store 中处理
  }
}

function handleConversationCreated(conv: Conversation) {
  console.log('Conversation created:', conv)
}
</script>

<style scoped>
.conversation-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-header {
  padding: 12px;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s;
  border: 1px solid #e5e7eb;
}

.panel-header:hover {
  background: #eff6ff;
  border-color: #3b82f6;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.expand-icon {
  transition: transform 0.2s;
  font-size: 20px;
}

.panel-title {
  font-weight: 500;
  font-size: 14px;
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}
</style>
