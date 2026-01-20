<template>
  <div class="conversation-view">
    <!-- 顶部：对话标题 -->
    <div class="conversation-header">
      <h2 class="conversation-title">
        {{ chatStore.currentConversation?.title || '新对话' }}
      </h2>
    </div>

    <!-- 消息列表 -->
    <div class="message-list">
      <MessageList v-if="chatStore.currentConversation" />
      <n-empty v-else description="请选择或创建一个对话" />
    </div>

    <!-- 输入框 -->
    <div class="chat-input">
      <ChatInput v-if="chatStore.currentConversation" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import MessageList from '@/components/chat/MessageList.vue'
import ChatInput from '@/components/chat/ChatInput.vue'

const chatStore = useChatStore()
</script>

<style scoped>
.conversation-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8fafc;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #f8fafc;
}

.conversation-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
}

.chat-input {
  border-top: 1px solid #e5e7eb;
  padding: 16px 24px;
  background: white;
}
</style>
