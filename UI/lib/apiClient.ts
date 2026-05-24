const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor() {
    this.baseUrl = API_URL
    this.loadToken()
  }

  private loadToken() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('authToken')
    }
  }

  private setToken(token: string) {
    this.token = token
    localStorage.setItem('authToken', token)
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }
    return headers
  }

  async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'API request failed')
    }

    return response.json()
  }

  // Auth endpoints
  async register(name: string, email: string, password: string, code: string) {
    const data = await this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password, code }),
    })
    this.setToken(data.token)
    return data
  }

  async login(email: string, password: string) {
    const data = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    this.setToken(data.token)
    return data
  }

  async getCurrentUser() {
    return this.request('/api/auth/me')
  }

  logout() {
    this.token = null
    localStorage.removeItem('authToken')
  }

  // Conversation endpoints
  async createConversation(title?: string) {
    return this.request('/api/conversations', {
      method: 'POST',
      body: JSON.stringify({ title }),
    })
  }

  async listConversations(archived = false) {
    return this.request(`/api/conversations?archived=${archived}`)
  }

  async getConversation(id: string) {
    return this.request(`/api/conversations/${id}`)
  }

  async updateConversation(id: string, data: { title?: string; pinned?: boolean; archived?: boolean }) {
    return this.request(`/api/conversations/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteConversation(id: string) {
    return this.request(`/api/conversations/${id}`, {
      method: 'DELETE',
    })
  }

  // Chat endpoints
  async saveChat(conversationId: string, role: string, text: string, biasData?: any) {
    return this.request('/api/chats', {
      method: 'POST',
      body: JSON.stringify({ conversationId, role, text, biasData }),
    })
  }

  async getConversationChats(conversationId: string) {
    return this.request(`/api/chats/${conversationId}`)
  }

  async deleteChat(id: string) {
    return this.request(`/api/chats/${id}`, {
      method: 'DELETE',
    })
  }
}

export const apiClient = new ApiClient()
