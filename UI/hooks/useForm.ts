'use client'

import { useState } from 'react'

interface UseFormReturn<T> {
  values: T
  errors: Partial<Record<keyof T, string>>
  touched: Partial<Record<keyof T, boolean>>
  setValue: (key: keyof T, value: any) => void
  setError: (key: keyof T, error: string) => void
  clearError: (key: keyof T) => void
  setTouched: (key: keyof T, value: boolean) => void
  resetForm: () => void
}

export const useForm = <T extends Record<string, any>>(initialValues: T): UseFormReturn<T> => {
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({})
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({})

  const setValue = (key: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [key]: value }))
  }

  const setError = (key: keyof T, error: string) => {
    setErrors(prev => ({ ...prev, [key]: error }))
  }

  const clearError = (key: keyof T) => {
    setErrors(prev => {
      const newErrors = { ...prev }
      delete newErrors[key]
      return newErrors
    })
  }

  const handleSetTouched = (key: keyof T, value: boolean) => {
    setTouched(prev => ({ ...prev, [key]: value }))
  }

  const resetForm = () => {
    setValues(initialValues)
    setErrors({})
    setTouched({})
  }

  return {
    values,
    errors,
    touched,
    setValue,
    setError,
    clearError,
    setTouched: handleSetTouched,
    resetForm,
  }
}
