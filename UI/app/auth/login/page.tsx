'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { LoginForm } from '@/components/auth'
import { AuthLayout } from '@/components/layout'
import { useAuth } from '@/hooks'

export default function LoginPage() {
  const router = useRouter()
  const { user, isLoading, login } = useAuth()

  useEffect(() => {
    if (!isLoading && user) {
      router.replace('/dashboard')
    }
  }, [isLoading, router, user])

  return (
    <AuthLayout>
      <LoginForm onLogin={login} isLoading={isLoading} />
    </AuthLayout>
  )
}
