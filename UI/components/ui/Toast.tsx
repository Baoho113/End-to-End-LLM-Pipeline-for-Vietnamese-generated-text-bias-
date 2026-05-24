import React from 'react'
import clsx from 'clsx'

interface ToastProps {
  message: string
  type?: 'success' | 'error' | 'info'
  icon?: React.ReactNode
  visible?: boolean
}

export const Toast: React.FC<ToastProps> = ({
  message,
  type = 'error',
  icon,
  visible = true,
}) => {
  if (!visible || !message) return null

  const bgClass = type === 'success'
    ? 'bg-status-green bg-opacity-10 border border-status-green border-opacity-25 text-status-green'
    : type === 'info'
      ? 'bg-accent-dim border border-accent-border text-accent-text'
      : 'bg-status-red bg-opacity-10 border border-status-red border-opacity-25 text-status-red'

  return (
    <div className={clsx('flex items-center gap-2 px-3 py-2.5 rounded-md text-sm leading-relaxed', bgClass)}>
      {icon && <span className="flex-shrink-0 text-base">{icon}</span>}
      <span>{message}</span>
    </div>
  )
}
