<template>
  <div class="message-list">
    <MessageItem
      v-for="message in chatStore.currentMessages"
      :key="message.id"
      :message="message"
    />

    <n-empty v-if="chatStore.currentMessages.length === 0" description="开始对话吧" />
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import MessageItem from './MessageItem.vue'

const chatStore = useChatStore()
</script>

<style scoped>
.message-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
