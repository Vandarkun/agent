<template>
  <div class="tools-view">
    <div class="view-header">
      <h2>🛠️ 可用的 Tools</h2>
      <n-p depth="3">当前系统提供的工具列表</n-p>
    </div>

    <div v-if="toolStore.isLoading" class="loading-container">
      <n-spin size="large" />
    </div>

    <n-list v-else hoverable clickable>
      <n-list-item v-for="tool in toolStore.tools" :key="tool.name">
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
import { useToolStore } from '@/stores/tool'

const toolStore = useToolStore()

function getToolIcon(name: string) {
  const icons: Record<string, string> = {
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

.tool-icon {
  font-size: 28px;
  margin-right: 12px;
}

.tool-name {
  font-weight: 500;
  margin-bottom: 4px;
}
</style>
