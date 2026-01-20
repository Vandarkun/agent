<template>
  <div
    class="conversation-item"
    :class="{ active: isActive }"
    @click="$emit('click')"
  >
    <div class="conversation-info">
      <div class="conversation-title">
        {{ conversation.title || '新对话' }}
      </div>
      <div class="conversation-time">
        {{ formatTime(conversation.created_at) }}
      </div>
    </div>

    <n-button
      v-if="isActive"
      text
      size="tiny"
      @click.stop="$emit('delete', conversation.id)"
    >
      <template #icon>
        <n-icon :component="TrashOutline" />
      </template>
    </n-button>
  </div>
</template>

<script setup lang="ts">
import { TrashOutline } from '@vicons/ionicons5'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'
import type { Conversation } from '@/types'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

defineProps<{
  conversation: Conversation
  isActive: boolean
}>()

defineEmits<{
  click: []
  delete: [id: string]
}>()

function formatTime(time: string) {
  return dayjs(time).fromNow()
}
</script>

<style scoped>
.conversation-item {
  padding: 12px;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s;
  border: 1px solid #e5e7eb;
}

.conversation-item:hover {
  background: #eff6ff;
  border-color: #3b82f6;
}

.conversation-item.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.conversation-item.active .conversation-time {
  color: rgba(255, 255, 255, 0.8);
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-time {
  font-size: 12px;
  color: #9ca3af;
  transition: color 0.2s;
}
</style>
