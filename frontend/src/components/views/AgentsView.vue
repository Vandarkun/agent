<template>
  <div class="agents-view">
    <div class="view-header">
      <h2>🤖 可用的 Agents</h2>
      <n-p depth="3">选择一个 Agent 了解详情</n-p>
    </div>

    <div v-if="agentStore.isLoading" class="loading-container">
      <n-spin size="large" />
    </div>

    <div v-else class="agents-grid">
      <n-card
        v-for="agent in agentStore.agents"
        :key="agent.mode"
        class="agent-card"
        :class="{ selected: agent.mode === chatStore.currentAgent }"
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
            <n-tag v-if="agent.mode === chatStore.currentAgent" type="success">
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
import { useAgentStore } from '@/stores/agent'
import { useChatStore } from '@/stores/chat'

const agentStore = useAgentStore()
const chatStore = useChatStore()

function getAgentIcon(mode: string) {
  const icons: Record<string, string> = {
    react: '📌',
    plan_execute: '🎯',
    codeact: '💻',
    mcp: '🔌'
  }
  return icons[mode] || '🤖'
}

function selectAgent(mode: string) {
  chatStore.setCurrentAgent(mode)
}
</script>

<style scoped>
.agents-view {
  padding: 24px;
  height: 100vh;
  overflow-y: auto;
  background: white;
}

.view-header {
  margin-bottom: 24px;
}

.view-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding-top: 100px;
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
  border-color: #667eea;
  box-shadow: 0 0 0 2px #667eea;
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
