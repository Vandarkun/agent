/** Agent 状态管理 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { agentApi } from '@/api'
import type { AgentInfo } from '@/types'

export const useAgentStore = defineStore('agent', () => {
  const agents = ref<AgentInfo[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function loadAgents() {
    try {
      isLoading.value = true
      error.value = null
      agents.value = await agentApi.getAgents()
    } catch (err: any) {
      error.value = err.response?.data?.detail || '加载 Agent 列表失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function getAgentByMode(mode: string) {
    return agents.value.find(a => a.mode === mode)
  }

  return {
    agents,
    isLoading,
    error,
    loadAgents,
    getAgentByMode
  }
})
