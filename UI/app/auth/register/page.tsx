'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { RegisterForm } from '@/components/auth'
import { AuthLayout } from '@/components/layout'
import { useAuth } from '@/hooks'

export default function RegisterPage() {
  const router = useRouter()
  const { user, isLoading, register } = useAuth()

  useEffect(() => {
    if (!isLoading && user) {
      router.replace('/dashboard')
    }
  }, [isLoading, router, user])

  return (
    <AuthLayout>
      <RegisterForm onRegister={register} isLoading={isLoading} />
    </AuthLayout>
  )
}
