/** 聊天状态管理 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { conversationApi } from '@/api'
import type { Conversation, Message, ConversationCreate } from '@/types'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref<Conversation[]>([])
  const currentConversationId = ref<string | null>(null)
  const messages = ref<Record<string, Message[]>>({})
  const currentAgent = ref<string>('ReAct') // 默认 Agent
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const currentConversation = computed(() =>
    conversations.value.find(c => c.id === currentConversationId.value)
  )

  const currentMessages = computed(() =>
    currentConversationId.value ? (messages.value[currentConversationId.value] || []) : []
  )

  async function loadConversations() {
    try {
      isLoading.value = true
      error.value = null
      conversations.value = await conversationApi.getConversations()
    } catch (err: any) {
      error.value = err.response?.data?.detail || '加载对话列表失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createConversation(data: ConversationCreate) {
    try {
      isLoading.value = true
      error.value = null
      const conversation = await conversationApi.createConversation(data)
      conversations.value.unshift(conversation)
      await switchConversation(conversation.id)
      return conversation
    } catch (err: any) {
      error.value = err.response?.data?.detail || '创建对话失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteConversation(id: string) {
    try {
      isLoading.value = true
      error.value = null
      await conversationApi.deleteConversation(id)
      conversations.value = conversations.value.filter(c => c.id !== id)
      if (currentConversationId.value === id) {
        currentConversationId.value = null
        messages.value[id] = []
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || '删除对话失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function loadMessages(conversationId: string) {
    try {
      isLoading.value = true
      error.value = null
      const response = await conversationApi.getMessages(conversationId)
      messages.value[conversationId] = response.items
    } catch (err: any) {
      error.value = err.response?.data?.detail || '加载消息失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function sendMessage(content: string) {
    if (!currentConversationId.value) {
      throw new Error('请先选择对话')
    }
    try {
      isLoading.value = true
      error.value = null
      const response = await conversationApi.sendMessage(currentConversationId.value, {
        content,
        agent_mode: currentAgent.value
      })

      // 添加用户消息
      const userMsg: Message = {
        id: response.message_id,
        conversation_id: response.conversation_id,
        role: 'user',
        content: content,
        agent_mode: response.agent_mode,
        created_at: new Date().toISOString()
      }

      // 添加 Agent 回复
      const agentMsg: Message = {
        id: `${response.message_id}_response`,
        conversation_id: response.conversation_id,
        role: 'agent',
        content: response.answer,
        agent_mode: response.agent_mode,
        created_at: new Date().toISOString()
      }

      const msgs = messages.value[currentConversationId.value] || []
      messages.value[currentConversationId.value] = [...msgs, userMsg, agentMsg]

      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || '发送消息失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function switchConversation(id: string) {
    currentConversationId.value = id
    if (!messages.value[id] || messages.value[id].length === 0) {
      await loadMessages(id)
    }
  }

  function setCurrentAgent(mode: string) {
    currentAgent.value = mode
  }

  return {
    conversations,
    currentConversationId,
    currentConversation,
    messages,
    currentMessages,
    currentAgent,
    isLoading,
    error,
    loadConversations,
    createConversation,
    deleteConversation,
    loadMessages,
    sendMessage,
    switchConversation,
    setCurrentAgent
  }
})
