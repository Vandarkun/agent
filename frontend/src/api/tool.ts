/** Tool 相关 API */
import request from './request'
import type { ToolInfo } from '@/types'

export function getTools() {
  return request.get<ToolInfo[]>('/api/tools')
}
