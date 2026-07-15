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

// Sample Vietnamese sentences for the detection module (src/training/), each
// already exercised against the trained checkpoint during development.
export const DETECTION_SAMPLES = [
  {
    key: 'gender-occupation',
    label: 'Gender + occupation',
    text: 'Là một giám đốc thành đạt, anh ấy luôn đưa ra những quyết định quyết đoán và mạnh mẽ. Trong khi đó, các nữ trợ lý trong công ty chỉ phù hợp với những công việc nhẹ nhàng như pha trà, sắp xếp lịch họp và chăm sóc khách hàng.',
  },
  {
    key: 'age',
    label: 'Age',
    text: 'Người già thường khó tiếp thu.',
  },
  {
    key: 'gender-slang',
    label: 'Gender (colloquial)',
    text: 'Bọn đàn ông ẻo lả chỉ hợp làm thiết kế thời trang thôi.',
  },
  {
    key: 'neutral',
    label: 'Neutral (no bias)',
    text: 'Hôm nay trời đẹp, tôi đi dạo công viên.',
  },
] as const
