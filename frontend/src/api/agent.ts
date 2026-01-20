/** Agent 相关 API */
import request from './request'
import type { AgentInfo } from '@/types'

export function getAgents() {
  return request.get<AgentInfo[]>('/api/agents')
}
