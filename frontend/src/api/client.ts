import type { Message, Portfolio, ResumeInfo, Sections, SectionKey, Stats } from './types'

const BASE = `${(import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')}/api`
const TOKEN_KEY = 'portfolio_admin_token'

export const tokenStore = {
  get: () => { try { return localStorage.getItem(TOKEN_KEY) } catch { return null } },
  set: (t: string) => { try { localStorage.setItem(TOKEN_KEY, t) } catch { /* ignore */ } },
  clear: () => { try { localStorage.removeItem(TOKEN_KEY) } catch { /* ignore */ } },
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) { super(message); this.status = status }
}

let onUnauthorized: (() => void) | null = null
export const setUnauthorizedHandler = (fn: (() => void) | null) => { onUnauthorized = fn }

function errorMessage(body: unknown, fallback: string): string {
  if (body && typeof body === 'object' && 'detail' in body) {
    const d = (body as { detail: unknown }).detail
    if (typeof d === 'string') return d
    if (Array.isArray(d)) return d.map((e: { loc?: unknown[]; msg?: string }) => `${e.loc?.slice(-1)[0] ?? ''}: ${e.msg}`).join('; ')
  }
  return fallback
}

async function request<T>(path: string, init: RequestInit = {}, auth = false): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body && !(init.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  if (auth) {
    const t = tokenStore.get()
    if (t) headers.set('Authorization', `Bearer ${t}`)
  }
  const res = await fetch(`${BASE}${path}`, { ...init, headers })
  if (res.status === 204) return undefined as T
  const body = await res.json().catch(() => null)
  if (!res.ok) {
    if (res.status === 401 && auth) onUnauthorized?.()
    throw new ApiError(res.status, errorMessage(body, res.statusText || 'Request failed'))
  }
  return body as T
}

const json = (data: unknown) => JSON.stringify(data)

export const resumeUrl = `${BASE}/resume`
export const certificateUrl = (id: number) => `${BASE}/certifications/${id}/file`

export const publicApi = {
  portfolio: () => request<Portfolio>('/portfolio'),
  sendMessage: (data: { name: string; email: string; subject?: string; body: string; website?: string }) =>
    request<{ ok: boolean }>('/messages', { method: 'POST', body: json(data) }),
}

export const authApi = {
  login: (email: string, password: string) =>
    request<{ access_token: string; expires_in: number }>('/auth/login', { method: 'POST', body: json({ email, password }) }),
  me: () => request<{ id: number; email: string }>('/auth/me', {}, true),
  changePassword: (current_password: string, new_password: string) =>
    request<void>('/auth/change-password', { method: 'POST', body: json({ current_password, new_password }) }, true),
}

export type CollectionName = 'facts' | 'projects' | 'timeline' | 'skills' | 'life-cards' | 'certifications'

export const adminApi = {
  stats: () => request<Stats>('/admin/stats', {}, true),
  sections: () => request<Sections>('/admin/sections', {}, true),
  saveSection: <K extends SectionKey>(key: K, data: Partial<Sections[K]>) =>
    request<Sections[K]>(`/admin/sections/${key}`, { method: 'PUT', body: json(data) }, true),

  list: <T>(c: CollectionName) => request<T[]>(`/admin/${c}`, {}, true),
  create: <T>(c: CollectionName, data: unknown) => request<T>(`/admin/${c}`, { method: 'POST', body: json(data) }, true),
  update: <T>(c: CollectionName, id: number, data: unknown) =>
    request<T>(`/admin/${c}/${id}`, { method: 'PUT', body: json(data) }, true),
  remove: (c: CollectionName, id: number) => request<void>(`/admin/${c}/${id}`, { method: 'DELETE' }, true),
  reorder: <T>(c: CollectionName, ids: number[]) =>
    request<T[]>(`/admin/${c}/reorder`, { method: 'POST', body: json({ ids }) }, true),

  messages: () => request<Message[]>('/admin/messages', {}, true),
  markMessage: (id: number, is_read: boolean) =>
    request<Message>(`/admin/messages/${id}`, { method: 'PATCH', body: json({ is_read }) }, true),
  deleteMessage: (id: number) => request<void>(`/admin/messages/${id}`, { method: 'DELETE' }, true),

  resume: () => request<ResumeInfo>('/admin/resume', {}, true),
  uploadResume: (file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return request<ResumeInfo>('/admin/resume', { method: 'POST', body: fd }, true)
  },
  uploadCertificateFile: <T>(id: number, file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return request<T>(`/admin/certifications/${id}/file`, { method: 'POST', body: fd }, true)
  },
  deleteCertificateFile: <T>(id: number) => request<T>(`/admin/certifications/${id}/file`, { method: 'DELETE' }, true),
  deleteResume: () => request<void>('/admin/resume', { method: 'DELETE' }, true),
}
