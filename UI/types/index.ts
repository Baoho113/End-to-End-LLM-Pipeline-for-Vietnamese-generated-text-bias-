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

// --- Detection module (src/training, served via FastAPI) ---
// Real API response shape from src/training/inference_test.py:predict() --
// 13-category single-label classifier with a confidence-threshold multi-label
// list, not the 4-category shape above (which the old chat mock invented).

export interface DetectionLabel {
  label: string
  confidence: number
}

export interface DetectionResult {
  text: string
  label: string
  confidence: number
  labels: DetectionLabel[]
  probabilities: Record<string, number>
}

// --- Mitigation module (src/training/mitigate.py, OpenAI rewrite) ---

export interface MitigationResult {
  original_text: string
  safer_text: string
  label: string | null
  model: string
}

export interface CategoryMetric {
  label: string
  precision: number
  recall: number
  f1: number
  support: number
}

export interface EvalMetrics {
  generated_at: string
  dataset: { train: number; val: number; test: number }
  overall: {
    accuracy: number
    macro_precision: number
    macro_recall: number
    macro_f1: number
    weighted_f1: number
  }
  per_category: CategoryMetric[]
}
