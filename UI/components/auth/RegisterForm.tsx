'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button, Input, Toast, PasswordStrength } from '@/components/ui'
import { useForm } from '@/hooks'
import { validateCode } from '@/lib/validation'
import { EARLY_ACCESS_CODE } from '@/lib/constants'
import { User, Mail, Lock, Eye, EyeOff, Key, CheckCircle2, Info, UserCheck } from 'lucide-react'

interface RegisterFormProps {
  onRegister: (name: string, email: string, password: string, code: string) => Promise<{ success: boolean; message?: string }>
  isLoading?: boolean
}

interface RegisterFormValues {
  name: string
  email: string
  password: string
  code: string
  showPassword: boolean
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onRegister, isLoading = false }) => {
  const { values, setValue } = useForm<RegisterFormValues>({
    name: '',
    email: '',
    password: '',
    code: '',
    showPassword: false,
  })
  const [error, setError] = useState<string>('')
  const [codeValid, setCodeValid] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value.toUpperCase().trim()
    setValue('code', val)
    const validation = validateCode(val, EARLY_ACCESS_CODE)
    setCodeValid(validation.isValid)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await onRegister(values.name, values.email, values.password, values.code)
    if (!result.success) {
      setError(result.message || 'Registration failed')
    }

    setLoading(false)
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      {/* Header */}
      <div className="flex flex-col gap-2 mb-1">
        <h1 className="text-2xl font-semibold text-text-1">Create your account</h1>
        <p className="text-sm text-text-3 leading-relaxed">Early access — invite code required to join</p>
      </div>

      {/* Name */}
      <Input
        label="Full name"
        type="text"
        placeholder="Jamie Doe"
        icon={<User size={16} />}
        value={values.name}
        onChange={e => setValue('name', e.target.value)}
      />

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
      <div>
        <Input
          label="Password"
          type={values.showPassword ? 'text' : 'password'}
          placeholder="Min. 8 characters"
          icon={<Lock size={16} />}
          rightIcon={values.showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          onRightIconClick={() => setValue('showPassword', !values.showPassword)}
          value={values.password}
          onChange={e => setValue('password', e.target.value)}
        />
        <div className="mt-2">
          <PasswordStrength password={values.password} />
        </div>
      </div>

      {/* Code */}
      <div>
        <Input
          label="Early access code"
          type="text"
          placeholder="Enter your invite code"
          icon={<Key size={16} />}
          valid={codeValid && values.code.length > 0}
          error={values.code.length > 0 && !codeValid}
          value={values.code}
          onChange={handleCodeChange}
        />
        <div className="mt-2 flex items-start gap-2 p-3 rounded-md bg-accent-dim border border-accent-border">
          <Info size={16} className="text-accent-text flex-shrink-0 mt-0.5" />
          <span className="text-xs text-text-3 leading-relaxed">
            Required for beta access to get in.
          </span>
        </div>
      </div>

      {/* Toast */}
      <Toast message={error} type="error" visible={!!error} />

      {/* Submit */}
      <Button type="submit" size="md" loading={loading || isLoading} icon={<UserCheck size={16} />} disabled={!codeValid}>
        Create account
      </Button>

      {/* Switch */}
      <div className="text-center text-sm text-text-3">
        Already have an account?{' '}
        <Link href="/auth/login" className="text-accent-text hover:text-white transition-colors">
          Sign in
        </Link>
      </div>
    </form>
  )
}
