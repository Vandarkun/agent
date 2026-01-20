/** API 响应的通用类型定义 */

export interface User {
  id: string
  username: string
}

export interface Conversation {
  id: string
  title: string | null
  created_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'agent'
  content: string
  agent_mode: string
  created_at: string
}

export interface MessagesPage {
  items: Message[]
  total: number
}

export interface AgentInfo {
  mode: string
  name: string
  description: string | null
}

export interface ToolInfo {
  name: string
  description: string | null
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  expires_at: string
}

export interface ConversationCreate {
  title?: string
}

export interface MessageCreate {
  content: string
  agent_mode: string
}

export interface MessageResponse {
  message_id: string
  conversation_id: string
  agent_mode: string
  answer: string
}
