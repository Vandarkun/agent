/** Tool 状态管理 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { toolApi } from '@/api'
import type { ToolInfo } from '@/types'

export const useToolStore = defineStore('tool', () => {
  const tools = ref<ToolInfo[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function loadTools() {
    try {
      isLoading.value = true
      error.value = null
      tools.value = await toolApi.getTools()
    } catch (err: any) {
      error.value = err.response?.data?.detail || '加载 Tool 列表失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    tools,
    isLoading,
    error,
    loadTools
  }
})
