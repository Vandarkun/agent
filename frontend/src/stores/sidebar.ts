/** 侧边栏状态管理 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSidebarStore = defineStore('sidebar', () => {
  const isCollapsed = ref(false)

  function toggleCollapse() {
    isCollapsed.value = !isCollapsed.value
  }

  function setCollapsed(collapsed: boolean) {
    isCollapsed.value = collapsed
  }

  return {
    isCollapsed,
    toggleCollapse,
    setCollapsed
  }
})
