import { User, UserSession } from '@/types'
import { USER_STORAGE_KEY, SESSION_STORAGE_KEY } from './constants'

// User management
export const getUsers = (): User[] => {
  if (typeof window === 'undefined') return []
  try {
    return JSON.parse(localStorage.getItem(USER_STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

export const saveUsers = (users: User[]): void => {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(users))
  } catch {}
}

export const findUser = (email: string, password: string): User | undefined => {
  const users = getUsers()
  const encoded = btoa(password)
  return users.find(u => u.email === email && u.pw === encoded)
}

export const userExists = (email: string): boolean => {
  return getUsers().some(u => u.email === email)
}

export const createUser = (name: string, email: string, password: string): User => {
  return {
    name,
    email,
    pw: btoa(password),
  }
}

// Session management
export const getSession = (): UserSession | null => {
  if (typeof window === 'undefined') return null
  try {
    return JSON.parse(localStorage.getItem(SESSION_STORAGE_KEY) || 'null')
  } catch {
    return null
  }
}

export const setSession = (session: UserSession): void => {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session))
  } catch {}
}

export const clearSession = (): void => {
  if (typeof window === 'undefined') return
  try {
    localStorage.removeItem(SESSION_STORAGE_KEY)
  } catch {}
}
