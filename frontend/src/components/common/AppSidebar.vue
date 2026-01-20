<template>
  <div class="app-sidebar" :class="{ collapsed: sidebarStore.isCollapsed }">
    <!-- 折叠按钮 -->
    <div class="sidebar-header">
      <n-button text size="large" @click="sidebarStore.toggleCollapse()">
        <template #icon>
          <n-icon :component="sidebarStore.isCollapsed ? Menu : ChevronBack" />
        </template>
      </n-button>
    </div>

    <!-- 对话列表面板 -->
    <ConversationPanel />

    <!-- 导航项：Agents -->
    <div
      class="nav-item"
      :class="{ active: appStore.currentView === 'agents' }"
      @click="switchToAgents"
    >
      <div class="nav-item-content">
        <span class="nav-icon">🤖</span>
        <span class="nav-text">Agents</span>
      </div>
      <n-icon :component="ChevronForward" class="arrow-icon" />
    </div>

    <!-- 导航项：Tools -->
    <div
      class="nav-item"
      :class="{ active: appStore.currentView === 'tools' }"
      @click="switchToTools"
    >
      <div class="nav-item-content">
        <span class="nav-icon">🛠️</span>
        <span class="nav-text">Tools</span>
      </div>
      <n-icon :component="ChevronForward" class="arrow-icon" />
    </div>

    <!-- 底部：退出登录 -->
    <div class="sidebar-footer">
      <n-button
        text
        size="large"
        @click="handleLogout"
        :style="{ width: '100%', justifyContent: sidebarStore.isCollapsed ? 'center' : 'flex-start' }"
      >
        <template #icon>
          <n-icon :component="LogOutOutline" />
        </template>
        <span v-if="!sidebarStore.isCollapsed" class="nav-text">退出登录</span>
      </n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Menu, ChevronBack, ChevronForward, LogOutOutline } from '@vicons/ionicons5'
import { useSidebarStore } from '@/stores/sidebar'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { useDialog } from 'naive-ui'
import ConversationPanel from '@/components/conversation/ConversationPanel.vue'

const router = useRouter()
const dialog = useDialog()
const sidebarStore = useSidebarStore()
const appStore = useAppStore()
const authStore = useAuthStore()

function switchToAgents() {
  appStore.switchToAgents()
  // 移动端自动折叠侧边栏
  if (window.innerWidth < 1024) {
    sidebarStore.setCollapsed(true)
  }
}

function switchToTools() {
  appStore.switchToTools()
  if (window.innerWidth < 1024) {
    sidebarStore.setCollapsed(true)
  }
}

function handleLogout() {
  dialog.warning({
    title: '退出登录',
    content: '确定要退出登录吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: () => {
      authStore.logout()
      router.push('/login')
    }
  })
}
</script>

<style scoped>
.app-sidebar {
  width: 280px;
  height: 100vh;
  border-right: 1px solid #e5e7eb;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  padding: 12px;
  gap: 12px;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}

.app-sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  display: flex;
  justify-content: flex-end;
}

.nav-item {
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

.nav-item:hover {
  background: #eff6ff;
  border-color: #3b82f6;
}

.nav-item.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.nav-item-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-icon {
  font-size: 20px;
}

.collapsed .nav-text,
.collapsed .arrow-icon {
  display: none;
}

.collapsed .nav-item {
  justify-content: center;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}
</style>
