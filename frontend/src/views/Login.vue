<template>
  <div class="login-container">
    <n-card class="login-card" title="WDK Agent">
      <n-form ref="formRef" :model="formData" :rules="rules" size="large">
        <n-form-item path="username" label="用户名">
          <n-input
            v-model:value="formData.username"
            placeholder="请输入用户名"
            @keydown.enter="handleLogin"
          />
        </n-form-item>

        <n-form-item path="password" label="密码">
          <n-input
            v-model:value="formData.password"
            type="password"
            show-password-on="click"
            placeholder="请输入密码"
            @keydown.enter="handleLogin"
          />
        </n-form-item>

        <n-form-item>
          <n-button
            type="primary"
            block
            size="large"
            :loading="authStore.isLoading"
            @click="handleLogin"
          >
            登录
          </n-button>
        </n-form-item>
      </n-form>

      <n-alert v-if="authStore.error" type="error" :show-icon="false" style="margin-top: 16px">
        {{ authStore.error }}
      </n-alert>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { FormInst, FormRules } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()

const formData = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: {
    required: true,
    message: '请输入用户名',
    trigger: ['blur', 'input']
  },
  password: {
    required: true,
    message: '请输入密码',
    trigger: ['blur', 'input']
  }
}

async function handleLogin() {
  try {
    await authStore.login(formData)
    router.push('/')
  } catch (err) {
    // 错误已在 store 中处理
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.login-card {
  width: 400px;
  box-shadow: 0 8px 30px rgba(59, 130, 246, 0.2);
  border: none;
}
</style>
