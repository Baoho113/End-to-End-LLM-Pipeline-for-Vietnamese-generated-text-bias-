export const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(word => word[0] || '')
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

export const clamp = (value: number, min: number, max: number): number => {
  return Math.max(min, Math.min(max, value))
}

export const formatScore = (score: number): number => {
  return Math.max(0, Math.min(100, Math.round(score)))
}

export const getScoreCategory = (score: number): 'low' | 'medium' | 'high' => {
  if (score < 33) return 'low'
  if (score < 66) return 'medium'
  return 'high'
}

export const calculateAverageScore = (scores: number[]): number => {
  if (scores.length === 0) return 0
  return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
}

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '…'
}

export const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}
