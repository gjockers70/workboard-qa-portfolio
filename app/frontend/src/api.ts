export type User = {
  id: number
  email: string
  display_name: string
  role: string
}

export type Task = {
  id: number
  title: string
  description: string
  completed: boolean
  owner_id: number
  created_at: string
  updated_at: string
  owner_email?: string
  owner_name?: string
}

type AuthResponse = {
  access_token: string
  token_type: string
  user: User
}

const API_URL = 'http://127.0.0.1:8000'

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'Request failed' }))
    const detail = typeof body.detail === 'string' ? body.detail : 'Check the submitted values'
    throw new Error(detail)
  }

  return response.status === 204 ? (undefined as T) : response.json()
}

export const api = {
  register: (email: string, displayName: string, password: string) =>
    request<AuthResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, display_name: displayName, password }),
    }),
  login: (email: string, password: string) =>
    request<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  tasks: (token: string, search: string, state: string) =>
    request<Task[]>(`/api/tasks?search=${encodeURIComponent(search)}&state=${state}`, {}, token),
  allTasks: (token: string) => request<Task[]>('/api/admin/tasks', {}, token),
  updateProfile: (token: string, displayName: string) =>
    request<User>('/api/profile', {
      method: 'PATCH',
      body: JSON.stringify({ display_name: displayName }),
    }, token),
  createTask: (token: string, title: string, description: string) =>
    request<Task>('/api/tasks', { method: 'POST', body: JSON.stringify({ title, description }) }, token),
  updateTask: (token: string, id: number, changes: Partial<Pick<Task, 'title' | 'description' | 'completed'>>) =>
    request<Task>(`/api/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(changes) }, token),
  deleteTask: (token: string, id: number) =>
    request<void>(`/api/tasks/${id}`, { method: 'DELETE' }, token),
}
