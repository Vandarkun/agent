<template>
  <n-modal
    v-model:show="showDialog"
    :mask-closable="true"
    preset="dialog"
    title="新建对话"
    :positive-text="pending ? '创建中...' : '创建'"
    negative-text="取消"
    :positive-button-props="{ loading: pending }"
    @positive-click="handleCreate"
  >
    <n-form ref="formRef" :model="formData">
      <n-form-item label="对话标题（可选）">
        <n-input
          v-model:value="formData.title"
          placeholder="例如：Python 学习、数据分析..."
          @keydown.enter="handleCreate"
        />
      </n-form-item>

      <n-alert type="info" :show-icon="false">
        创建后可在对话视图中选择 Agent 模式
      </n-alert>
    </n-form>
  </n-modal>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useMessage } from 'naive-ui'
import { useChatStore } from '@/stores/chat'

const emit = defineEmits<{
  created: [conversation: any]
}>()

const message = useMessage()
const chatStore = useChatStore()

const showDialog = defineModel<boolean>('show', { default: false })
const pending = ref(false)

const formData = reactive({
  title: ''
})

async function handleCreate() {
  try {
    pending.value = true

    // 创建对话（只传递 title，不需要选择 agent）
    const conversation = await chatStore.createConversation({
      title: formData.title || undefined
    })

    message.success('对话创建成功')

    // 重置表单
    formData.title = ''
    showDialog.value = false

    // 通知父组件
    emit('created', conversation)
  } catch (error) {
    // 错误已在 store 中处理
  } finally {
    pending.value = false
  }
}
</script>

<style scoped>
:deep(.n-alert) {
  margin-top: 12px;
}
</style>
