// Auth codes and storage keys
export const EARLY_ACCESS_CODE = 'NEK@NDIDN_CODE'
export const USER_STORAGE_KEY = 'bl_users'
export const SESSION_STORAGE_KEY = 'bl_session'

// Sample texts for bias detection
export const BIAS_SAMPLES = {
  gender: 'The businessman negotiated the deal aggressively while his female assistant quietly took notes. The decisive, no-nonsense CEO — naturally a man — led from the front, while the women handled the softer, emotional side of client relations.',
  political: 'The radical left-wing agenda is destroying the fabric of our society, while true patriots stand firm against the socialist takeover being pushed by coastal elites who despise hard-working Americans and traditional values.',
  racial: 'Property values in the neighbourhood dropped significantly after families from the inner city started moving in, bringing with them the kinds of social problems that make long-time residents feel unsafe.',
  media: 'Officials insist the situation is under control, though anonymous sources close to the matter suggest a coordinated cover-up may be hiding the true scale of the crisis from an unsuspecting and easily-misled public.',
  corporate: 'We are looking for a rockstar developer who can hit the ground running and crush it in a high-pressure, fast-paced environment. Only top performers with thick skin need apply — we don\'t have time for hand-holding.',
} as const

export type BiasSampleKey = keyof typeof BIAS_SAMPLES

// AI System prompt for Claude
export const BIAS_DETECTION_SYSTEM_PROMPT = `You are a bias detection assistant. Analyze the given text for bias and respond ONLY with valid JSON — no markdown, no extra text, no explanation.
Format exactly:
{"summary":"one concise sentence summarising the overall bias","overall":"low|medium|high","biases":[{"type":"Gender","score":0,"note":"brief note"},{"type":"Political","score":0,"note":"brief note"},{"type":"Racial","score":0,"note":"brief note"},{"type":"Sentiment","score":0,"note":"brief note"}]}
Scoring: 0 = no bias, 100 = extreme bias. Be precise and consistent.`

// Feature highlights for sidebar
export const FEATURES = [
  {
    icon: 'bolt',
    title: 'Real-time analysis',
    subtitle: 'Instant AI-powered scoring',
  },
  {
    icon: 'shield-lock',
    title: 'Early access',
    subtitle: 'Invite-only beta program',
  },
] as const

// Default fallback bias analysis
export const DEFAULT_BIAS_ANALYSIS = {
  summary: 'Analysis complete.',
  overall: 'medium' as const,
  biases: [
    { type: 'Gender' as const, score: 25, note: '' },
    { type: 'Political' as const, score: 50, note: '' },
    { type: 'Racial' as const, score: 15, note: '' },
    { type: 'Sentiment' as const, score: 60, note: '' },
  ],
}
