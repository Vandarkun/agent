/** 应用全局状态管理 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ViewType = 'conversation' | 'agents' | 'tools'

export const useAppStore = defineStore('app', () => {
  const currentView = ref<ViewType>('conversation')

  function setCurrentView(view: ViewType) {
    currentView.value = view
  }

  function switchToConversation() {
    currentView.value = 'conversation'
  }

  function switchToAgents() {
    currentView.value = 'agents'
  }

  function switchToTools() {
    currentView.value = 'tools'
  }

  return {
    currentView,
    setCurrentView,
    switchToConversation,
    switchToAgents,
    switchToTools
  }
})
