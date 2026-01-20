<template>
  <div class="chat-input-container">
    <!-- 智能体选择器 -->
    <div class="agent-selector">
      <n-select
        v-model:value="chatStore.currentAgent"
        :options="agentOptions"
        :render-label="renderAgentLabel"
        :render-tag="renderAgentTag"
        placeholder="智能体"
        size="large"
        @update:value="handleAgentChange"
      />
    </div>

    <!-- 输入框 -->
    <n-input
      v-model:value="inputText"
      type="textarea"
      :autosize="{ minRows: 1, maxRows: 6 }"
      placeholder="输入消息..."
      :disabled="chatStore.isLoading"
      @keydown="handleKeyDown"
    />

    <!-- 发送按钮 -->
    <n-button
      type="primary"
      size="large"
      :loading="chatStore.isLoading"
      :disabled="!inputText.trim()"
      @click="handleSend"
    >
      发送
    </n-button>
  </div>
</template>

<script setup lang="ts">
import { ref, h, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { NTag, NText } from 'naive-ui'
import { useChatStore } from '@/stores/chat'
import { useAgentStore } from '@/stores/agent'

const message = useMessage()
const chatStore = useChatStore()
const agentStore = useAgentStore()

const inputText = ref('')

const agentOptions = computed(() =>
  agentStore.agents.map(agent => ({
    label: agent.name,
    value: agent.mode
  }))
)

function getAgentIcon(mode: string) {
  const icons: Record<string, string> = {
    react: '📌',
    plan_execute: '🎯',
    codeact: '💻',
    mcp: '🔌'
  }
  return icons[mode] || '🤖'
}

function renderAgentLabel(option: any) {
  const agent = agentStore.agents.find(a => a.mode === option.value)
  return h('div', { class: 'agent-option' }, [
    h('div', { class: 'agent-mode' }, agent?.mode)
  ])
}

function renderAgentTag(props: any) {
  return h('span', { class: 'agent-tag' }, props.option.value)
}

function handleAgentChange(mode: string) {
  chatStore.setCurrentAgent(mode)
}

function handleKeyDown(e: KeyboardEvent) {
  // Enter 发送，Shift+Enter 换行
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

async function handleSend() {
  if (!inputText.value.trim() || chatStore.isLoading) {
    return
  }

  const content = inputText.value.trim()
  inputText.value = ''

  try {
    await chatStore.sendMessage(content)
  } catch (err) {
    message.error('发送失败，请重试')
    inputText.value = content // 恢复输入内容
  }
}
</script>

<style scoped>
.chat-input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.agent-selector {
  width: 140px;
  flex-shrink: 0;
}

/* 移除选择器背景 */
.agent-selector :deep(.n-base-selection) {
  background-color: transparent !important;
}

.chat-input-container :deep(.n-input) {
  flex: 1;
}

.chat-input-container :deep(.n-input__border) {
  border-radius: 12px !important;
}

.chat-input-container :deep(.n-input__textarea-el) {
  border-radius: 12px !important;
}

/* 智能体选项样式 */
.agent-option {
  padding: 4px 0;
}

.agent-mode {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 4px;
}

.agent-desc {
  font-size: 12px;
  color: #64748b;
  line-height: 1.4;
}

.agent-tag {
  font-weight: 500;
  font-size: 14px;
}
</style>
