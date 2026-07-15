import React from 'react'
import { getPasswordStrength, getPasswordHint } from '@/lib/validation'
import clsx from 'clsx'

interface PasswordStrengthProps {
  password: string
}

export const PasswordStrength: React.FC<PasswordStrengthProps> = ({ password }) => {
  const strength = getPasswordStrength(password)
  const hint = getPasswordHint(password)

  const getBarColor = (index: number) => {
    if (index >= strength) return 'bg-opacity-10'
    if (strength === 1) return 'bg-status-red'
    if (strength === 2) return 'bg-status-amber'
    if (strength === 3) return 'bg-status-green'
    return 'bg-blue-500'
  }

  const getHintColor = () => {
    if (!password) return 'text-text-4'
    if (strength === 1) return 'text-status-red'
    if (strength === 2) return 'text-status-amber'
    if (strength === 3 || strength === 4) return 'text-status-green'
    return 'text-text-4'
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex gap-1">
        {[0, 1, 2, 3].map(index => (
          <div key={index} className={clsx('flex-1 h-1 rounded-sm bg-white transition-colors', getBarColor(index))} />
        ))}
      </div>
      <span className={clsx('text-xs transition-colors', getHintColor())}>
        {hint}
      </span>
    </div>
  )
}
