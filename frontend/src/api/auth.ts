/** 认证相关 API */
import request from './request'
import type { LoginRequest, LoginResponse } from '@/types'

export function login(data: LoginRequest) {
  return request.post<LoginResponse>('/api/auth/login', data)
}
