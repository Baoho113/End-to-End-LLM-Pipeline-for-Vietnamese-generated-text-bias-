import { BiasAnalysisResult, ConversationMessage } from '@/types'
import { BIAS_DETECTION_SYSTEM_PROMPT, DEFAULT_BIAS_ANALYSIS } from './constants'

export async function analyzeTextForBias(
  text: string,
  conversationHistory: ConversationMessage[],
): Promise<BiasAnalysisResult> {
  try {
    const messages: ConversationMessage[] = [
      ...conversationHistory,
      {
        role: 'user',
        content: `Analyze this text for bias: ${text}`,
      },
    ]

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        system: BIAS_DETECTION_SYSTEM_PROMPT,
        messages,
      }),
    })

    if (!response.ok) {
      console.error('API error:', response.statusText)
      return DEFAULT_BIAS_ANALYSIS
    }

    const data = await response.json()
    const raw = data.content.map((item: any) => item.text || '').join('')

    try {
      const parsed = JSON.parse(raw.replace(/```json|```/g, '').trim())
      return parsed as BiasAnalysisResult
    } catch (parseError) {
      console.error('Failed to parse API response:', parseError)
      return DEFAULT_BIAS_ANALYSIS
    }
  } catch (error) {
    console.error('Analysis error:', error)
    return DEFAULT_BIAS_ANALYSIS
  }
}

export function getAssistantMessageFromAnalysis(analysis: BiasAnalysisResult): string {
  return JSON.stringify(analysis)
}
