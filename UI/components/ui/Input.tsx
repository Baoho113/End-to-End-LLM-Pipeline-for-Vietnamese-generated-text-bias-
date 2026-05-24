import React from 'react'
import clsx from 'clsx'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  icon?: React.ReactNode
  rightIcon?: React.ReactNode
  onRightIconClick?: () => void
  error?: boolean | string
  valid?: boolean
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    { className, label, icon, rightIcon, onRightIconClick, error, valid, type = 'text', ...props },
    ref,
  ) => (
    <div className="flex flex-col gap-2">
      {label && (
        <label className="text-xs font-medium uppercase tracking-wider text-text-3">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none text-text-4 text-base">
            {icon}
          </div>
        )}
        <input
          ref={ref}
          type={type}
          className={clsx(
            'w-full bg-bg-2 border rounded-md px-3 py-3 text-sm text-text-1 font-medium',
            'placeholder:text-text-4 outline-none transition-all duration-150',
            'hover:border-opacity-30 focus:border-opacity-70 focus:bg-opacity-10',
            !error && !valid && 'border border-border-subtle',
            error && 'border border-red border-opacity-55 bg-red bg-opacity-5',
            valid && 'border border-green border-opacity-50 bg-green bg-opacity-5',
            icon && 'pl-10',
            rightIcon && 'pr-10',
            className,
          )}
          {...props}
        />
        {rightIcon && (
          <button
            type="button"
            onClick={onRightIconClick}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-text-4 hover:text-text-2 transition-colors"
            aria-label="Toggle"
          >
            {rightIcon}
          </button>
        )}
      </div>
    </div>
  ),
)

Input.displayName = 'Input'
