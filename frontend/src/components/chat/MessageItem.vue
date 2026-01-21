<template>
  <div class="message-item" :class="`message-item-${message.role}`">
    <div class="message-content">
      <div class="message-header">
        <span class="message-role">
          {{ message.role === 'user' ? '你' : getAgentName(message.agent_mode) }}
        </span>
        <span class="message-time">{{ formatTime(message.created_at) }}</span>
      </div>

      <div class="message-text">
        {{ message.content }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAgentStore } from '@/stores/agent'
import dayjs from 'dayjs'
import type { Message } from '@/types'

const props = defineProps<{
  message: Message
}>()

const agentStore = useAgentStore()

function normalizeAgentMode(mode: string | undefined) {
  if (!mode) {
    return ''
  }
  const normalized = mode.trim().toLowerCase()
  if (normalized === 'planexecute') {
    return 'plan_execute'
  }
  return normalized
}

function getAgentName(mode: string) {
  const agent = agentStore.getAgentByMode(normalizeAgentMode(mode))
  return agent?.name || 'Agent'
}

function formatTime(time: string) {
  return dayjs(time).format('HH:mm')
}
</script>

<style scoped>
.message-item {
  display: flex;
}

.message-item-user {
  justify-content: flex-end;
}

.message-item-agent {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
}

.message-item-user .message-content {
  background: #667eea;
  color: white;
  padding: 12px 16px;
  border-radius: 12px 12px 0 12px;
}

.message-item-agent .message-content {
  background: #f5f5f5;
  padding: 12px 16px;
  border-radius: 12px 12px 12px 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  opacity: 0.8;
}

.message-role {
  font-weight: 500;
}

.message-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
}
</style>
