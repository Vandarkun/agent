/** 对话相关 API */
import request from './request'
import type { Conversation, MessagesPage, MessageResponse, MessageCreate, ConversationCreate } from '@/types'

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
