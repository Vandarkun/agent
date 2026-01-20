<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <router-view />
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { type GlobalThemeOverrides } from 'naive-ui'

// 蓝白主题配色
const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#3B82F6',
    primaryColorHover: '#2563EB',
    primaryColorPressed: '#1D4ED8',
    primaryColorSuppl: '#60A5FA',
    borderRadius: '12px'
  }
}
</script>

<style>
/* 全局样式覆盖 */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  height: 100vh;
  overflow: hidden;
}

/* 圆角全局覆盖 */
.n-button {
  border-radius: 12px !important;
}

.n-input {
  border-radius: 12px !important;
}

.n-select {
  border-radius: 12px !important;
}

.n-card {
  border-radius: 16px !important;
}

.n-modal {
  border-radius: 16px !important;
}
</style>
