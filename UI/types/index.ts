export type BiasLevel = 'low' | 'medium' | 'high'

export interface BiasScore {
  type: 'Gender' | 'Political' | 'Racial' | 'Sentiment'
  score: number
  note: string
}

export interface BiasAnalysisResult {
  summary: string
  overall: BiasLevel
  biases: BiasScore[]
}

export interface UserSession {
  email: string
  name: string
}

export interface User extends UserSession {
  pw: string // Base64 encoded password
}

export interface ConversationMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
  biasData?: BiasAnalysisResult
  timestamp: number
}

export interface ConversationHistory {
  id: string
  title: string
  messages: ChatMessage[]
  timestamp: number
}
