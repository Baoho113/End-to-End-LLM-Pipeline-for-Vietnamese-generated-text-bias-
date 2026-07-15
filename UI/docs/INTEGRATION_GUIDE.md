# Frontend Integration Guide

This guide shows how to integrate the BiasLens frontend with the Prisma backend.

## Setup

### 1. Update Frontend Environment Variables

Create `.env.local` in your frontend root:

```env
NEXT_PUBLIC_API_URL=http://localhost:3001
```

### 2. Create API Client

Create `lib/apiClient.ts`:

```typescript
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

  async listConversations() {
    return this.request('/api/conversations')
  }

  async getConversation(id: string) {
    return this.request(`/api/conversations/${id}`)
  }

  async updateConversation(id: string, title: string) {
    return this.request(`/api/conversations/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ title }),
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
```

### 3. Update useAuth Hook

Update `hooks/useAuth.ts`:

```typescript
'use client'

import { useState, useEffect, useCallback } from 'react'
import { UserSession } from '@/types'
import { apiClient } from '@/lib/apiClient'

interface UseAuthReturn {
  user: UserSession | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<{ success: boolean; message?: string }>
  register: (name: string, email: string, password: string, code: string) => Promise<{ success: boolean; message?: string }>
  logout: () => void
  demoLogin: () => void
}

export const useAuth = (): UseAuthReturn => {
  const [user, setUser] = useState<UserSession | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await apiClient.getCurrentUser()
        setUser({ email: response.email, name: response.name })
      } catch (error) {
        // User not authenticated
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = useCallback(
    async (email: string, password: string): Promise<{ success: boolean; message?: string }> => {
      try {
        const response = await apiClient.login(email, password)
        setUser({ email: response.user.email, name: response.user.name })
        return { success: true }
      } catch (error) {
        return { success: false, message: error instanceof Error ? error.message : 'Login failed' }
      }
    },
    [],
  )

  const register = useCallback(
    async (name: string, email: string, password: string, code: string): Promise<{ success: boolean; message?: string }> => {
      try {
        const response = await apiClient.register(name, email, password, code)
        setUser({ email: response.user.email, name: response.user.name })
        return { success: true }
      } catch (error) {
        return { success: false, message: error instanceof Error ? error.message : 'Registration failed' }
      }
    },
    [],
  )

  const logout = () => {
    apiClient.logout()
    setUser(null)
  }

  const demoLogin = () => {
    const session: UserSession = { name: 'Demo User', email: 'demo@biaslens.ai' }
    setUser(session)
  }

  return { user, isLoading, login, register, logout, demoLogin }
}
```

### 4. Update useChat Hook

Update `hooks/useChat.ts` to save chats to backend:

```typescript
'use client'

import { useState, useCallback } from 'react'
import { ChatMessage, BiasAnalysisResult, ConversationMessage } from '@/types'
import { analyzeTextForBias } from '@/lib/api'
import { generateId } from '@/lib/utils'
import { apiClient } from '@/lib/apiClient'

interface UseChatReturn {
  messages: ChatMessage[]
  isAnalyzing: boolean
  conversationHistory: ConversationMessage[]
  conversationId: string | null
  sendMessage: (text: string) => Promise<void>
  clearChat: () => void
  startConversation: () => Promise<void>
}

export const useChat = (): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [conversationHistory, setConversationHistory] = useState<ConversationMessage[]>([])
  const [conversationId, setConversationId] = useState<string | null>(null)

  const startConversation = useCallback(async () => {
    try {
      const conversation = await apiClient.createConversation('New Analysis')
      setConversationId(conversation.id)
    } catch (error) {
      console.error('Failed to create conversation:', error)
    }
  }, [])

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim()) return

      // Start conversation if needed
      if (!conversationId) {
        await startConversation()
      }

      setIsAnalyzing(true)

      // Add user message
      const userMessage: ChatMessage = {
        id: generateId(),
        role: 'user',
        text,
        timestamp: Date.now(),
      }
      setMessages(prev => [...prev, userMessage])

      // Save user message to backend
      if (conversationId) {
        try {
          await apiClient.saveChat(conversationId, 'user', text)
        } catch (error) {
          console.error('Failed to save user message:', error)
        }
      }

      try {
        // Analyze text
        const analysis = await analyzeTextForBias(text, conversationHistory)

        // Add assistant message with bias data
        const assistantMessage: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          text: analysis.summary,
          biasData: analysis,
          timestamp: Date.now(),
        }
        setMessages(prev => [...prev, assistantMessage])

        // Save assistant message to backend
        if (conversationId) {
          try {
            await apiClient.saveChat(conversationId, 'assistant', analysis.summary, analysis)
          } catch (error) {
            console.error('Failed to save assistant message:', error)
          }
        }

        // Update conversation history
        setConversationHistory(prev => [
          ...prev,
          { role: 'user', content: `Analyze this text for bias: ${text}` },
          { role: 'assistant', content: JSON.stringify(analysis) },
        ])
      } catch (error) {
        console.error('Error analyzing text:', error)
        const errorMessage: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          text: 'Analysis failed — check your connection and try again.',
          timestamp: Date.now(),
        }
        setMessages(prev => [...prev, errorMessage])
      } finally {
        setIsAnalyzing(false)
      }
    },
    [conversationId, conversationHistory, startConversation],
  )

  const clearChat = useCallback(async () => {
    setMessages([])
    setConversationHistory([])
    setConversationId(null)
    await startConversation()
  }, [startConversation])

  return { messages, isAnalyzing, conversationHistory, conversationId, sendMessage, clearChat, startConversation }
}
```

## Running Both Services

### Terminal 1: Backend

```bash
cd backend
npm install
# Set up .env with your PostgreSQL database URL
npx prisma migrate dev --name init
npm run dev
```

Backend runs on `http://localhost:3001`

### Terminal 2: Frontend

```bash
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## Data Flow

1. **User registers** → Frontend sends to `/api/auth/register` → Backend creates user & returns JWT
2. **User logs in** → Frontend sends to `/api/auth/login` → Backend verifies & returns JWT
3. **User starts chat** → Frontend creates conversation via `/api/conversations`
4. **User sends message** → Frontend saves to backend via `/api/chats` → AI analysis → Save assistant response
5. **Chat history** → Frontend loads from backend via `/api/chats/:conversationId`

## Security Notes

- ✅ JWT tokens stored in localStorage
- ✅ Auth header validated on every protected route
- ✅ Passwords hashed with bcrypt
- ✅ CORS configured to allow frontend only
- ⚠️ For production: Use httpOnly cookies instead of localStorage
- ⚠️ For production: Use environment variables for secrets
- ⚠️ For production: Add rate limiting & input validation
