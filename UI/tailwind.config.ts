import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          0: '#080910',
          1: '#0d0e15',
          2: '#12141e',
          3: '#181a27',
          4: '#1f2130',
        },
        text: {
          1: 'rgba(255,255,255,0.92)',
          2: 'rgba(255,255,255,0.6)',
          3: 'rgba(255,255,255,0.35)',
          4: 'rgba(255,255,255,0.18)',
        },
        border: {
          DEFAULT: 'rgba(255,255,255,0.07)',
          subtle: 'rgba(255,255,255,0.12)',
        },
        accent: {
          DEFAULT: '#5b4fcf',
          hover: '#6a5dd8',
          dim: 'rgba(91,79,207,0.15)',
          border: 'rgba(91,79,207,0.3)',
          text: '#a89ef5',
        },
        status: {
          green: '#6fb96f',
          amber: '#e9a84a',
          red: '#e06060',
        },
      },
      fontFamily: {
        sans: ['var(--font-dm-sans)', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'monospace'],
      },
      borderRadius: {
        sm: '8px',
        md: '11px',
        lg: '14px',
        xl: '18px',
      },
      keyframes: {
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
        thinking: {
          '0%, 60%, 100%': { opacity: '0.3', transform: 'scale(0.8)' },
          '30%': { opacity: '1', transform: 'scale(1.1)' },
        },
      },
      animation: {
        pulse: 'pulse 2s infinite ease-in-out',
        thinking: 'thinking 1.2s infinite ease-in-out',
      },
    },
  },
  plugins: [],
}

export default config
