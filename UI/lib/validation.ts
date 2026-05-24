export const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export const validatePassword = (password: string): boolean => {
  return password.length >= 8
}

export const getPasswordStrength = (password: string): number => {
  let strength = 0
  if (password.length >= 8) strength++
  if (password.length >= 12) strength++
  if (/[A-Z]/.test(password) && /[0-9]/.test(password)) strength++
  if (/[^a-zA-Z0-9]/.test(password)) strength++
  return strength
}

export const getPasswordHint = (password: string): string => {
  if (!password) return 'Enter a password'
  const strength = getPasswordStrength(password)
  const hints = ['', 'Weak', 'Fair', 'Good', 'Strong']
  return hints[strength] || 'Weak'
}

export interface ValidationResult {
  isValid: boolean
  message?: string
}

export const validateCode = (code: string, validCode: string): ValidationResult => {
  const normalized = code.trim().toUpperCase()
  if (!normalized) {
    return { isValid: false }
  }
  if (normalized === validCode) {
    return { isValid: true }
  }
  return { isValid: false, message: `Invalid code. Hint: ${validCode}` }
}
