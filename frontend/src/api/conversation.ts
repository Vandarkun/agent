/** 对话相关 API */
import request from './request'
import type { Conversation, MessagesPage, MessageResponse, MessageCreate, ConversationCreate } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

export function getConversations() {
  return request.get<Conversation[]>('/api/conversations')
}

export function createConversation(data: ConversationCreate) {
  return request.post<Conversation>('/api/conversations', data)
}

export function deleteConversation(id: string) {
  return request.delete<{ message: string; conversation_id: string }>(`/api/conversations/${id}`)
}

export function getMessages(conversationId: string, params?: { limit?: number; offset?: number }) {
  return request.get<MessagesPage>(`/api/conversations/${conversationId}/messages`, { params })
}

export async function sendMessage(conversationId: string, data: MessageCreate): Promise<MessageResponse> {
  return request.post<MessageResponse>(`/api/conversations/${conversationId}/messages`, data)
}

export async function sendMessageStream(
  conversationId: string,
  data: MessageCreate,
  onChunk: (chunk: string) => void
): Promise<void> {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}/messages/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify(data)
  })

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    const detail = await response.text()
    throw new Error(detail || `请求失败 (${response.status})`)
  }

  if (!response.body) {
    throw new Error('响应缺少可读流')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { value, done } = await reader.read()
    if (value) {
      const chunk = decoder.decode(value, { stream: !done })
      if (chunk) {
        onChunk(chunk)
      }
    }
    if (done) {
      break
    }
  }
}
