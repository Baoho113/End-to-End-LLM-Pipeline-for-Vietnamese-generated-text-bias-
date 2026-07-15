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
}

export const useAuth = (): UseAuthReturn => {
  const [user, setUser] = useState<UserSession | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await apiClient.getCurrentUser()
        setUser({ email: response.email, name: response.user?.name ?? response.name })
      } catch (error) {
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

  return { user, isLoading, login, register, logout }
}
