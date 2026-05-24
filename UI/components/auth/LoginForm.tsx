'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button, Input, Toast } from '@/components/ui'
import { useForm } from '@/hooks'
import { Mail, Lock, Eye, EyeOff, LogIn } from 'lucide-react'

interface LoginFormProps {
  onLogin: (email: string, password: string) => Promise<{ success: boolean; message?: string }>
  isLoading?: boolean
}

interface LoginFormValues {
  email: string
  password: string
  showPassword: boolean
}

export const LoginForm: React.FC<LoginFormProps> = ({ onLogin, isLoading = false }) => {
  const { values, setValue } = useForm<LoginFormValues>({
    email: '',
    password: '',
    showPassword: false,
  })
  const [error, setError] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await onLogin(values.email, values.password)
    if (!result.success) {
      setError(result.message || 'Login failed')
    }

    setLoading(false)
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      {/* Header */}
      <div className="flex flex-col gap-2 mb-1">
        <h1 className="text-2xl font-semibold text-text-1">Welcome back</h1>
        <p className="text-sm text-text-3 leading-relaxed">Sign in to continue to BiasLens</p>
      </div>

      {/* Email */}
      <Input
        label="Email address"
        type="email"
        placeholder="you@example.com"
        icon={<Mail size={16} />}
        value={values.email}
        onChange={e => setValue('email', e.target.value)}
      />

      {/* Password */}
      <Input
        label="Password"
        type={values.showPassword ? 'text' : 'password'}
        placeholder="Your password"
        icon={<Lock size={16} />}
        rightIcon={values.showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
        onRightIconClick={() => setValue('showPassword', !values.showPassword)}
        value={values.password}
        onChange={e => setValue('password', e.target.value)}
      />

      {/* Toast */}
      <Toast message={error} type="error" visible={!!error} />

      {/* Submit */}
      <Button type="submit" size="md" loading={loading || isLoading} icon={<LogIn size={16} />}>
        Sign in
      </Button>

      {/* Divider */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-px bg-border" />
        <span className="text-xs text-text-4">or</span>
        <div className="flex-1 h-px bg-border" />
      </div>

      {/* Switch */}
      <div className="text-center text-sm text-text-3">
        No account?{' '}
        <Link href="/auth/register" className="text-accent-text hover:text-white transition-colors">
          Create one with early access
        </Link>
      </div>
    </form>
  )
}
