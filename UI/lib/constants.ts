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

// Display names for the 14-category severity detector (src/training/
// inference_llm_lora.py). Mirrors the category rubric in
// src/training/inference_severity_llm.py's CATEGORY_DEFINITIONS -- keep the
// key set in sync if that rubric changes.
export const CATEGORY_LABELS: Record<string, string> = {
  sexism: 'Sexism',
  lgbtq_bias: 'LGBTQ+ Bias',
  ethnic_minority_bias: 'Ethnic Minority Bias',
  regional_bias: 'Regional Bias',
  religion: 'Religion',
  ageism: 'Ageism',
  class_poverty_bias: 'Class / Poverty Bias',
  disability_health_bias: 'Disability / Health Bias',
  ideological_bias: 'Ideological Bias',
  appearance_body_shaming: 'Appearance / Body Shaming',
  linguistic_hierarchical_bias: 'Linguistic Hierarchy Bias',
  educational_cognitive_hierarchy: 'Educational / Cognitive Hierarchy',
  xenophobia: 'Xenophobia',
  moral_lifestyle_bias: 'Moral / Lifestyle Bias',
} as const

export function categoryLabel(category: string): string {
  return CATEGORY_LABELS[category] ?? category
}

// Short (one-word-ish) labels for chart axes, where CATEGORY_LABELS' full
// names ("Educational / Cognitive Hierarchy") would collide with each other
// around a 14-spoke radar chart. Full names still show in tooltips/legends.
export const CATEGORY_SHORT_LABELS: Record<string, string> = {
  sexism: 'Sexism',
  lgbtq_bias: 'LGBTQ+',
  ethnic_minority_bias: 'Ethnicity',
  regional_bias: 'Region',
  religion: 'Religion',
  ageism: 'Age',
  class_poverty_bias: 'Class',
  disability_health_bias: 'Disability',
  ideological_bias: 'Ideology',
  appearance_body_shaming: 'Appearance',
  linguistic_hierarchical_bias: 'Language',
  educational_cognitive_hierarchy: 'Education',
  xenophobia: 'Xenophobia',
  moral_lifestyle_bias: 'Lifestyle',
} as const

export function categoryShortLabel(category: string): string {
  return CATEGORY_SHORT_LABELS[category] ?? categoryLabel(category)
}
