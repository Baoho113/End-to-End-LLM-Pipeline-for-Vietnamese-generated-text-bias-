'use client'

import React, { useEffect, useRef, useState } from 'react'
import clsx from 'clsx'
import {
  ArrowUp,
  Briefcase,
  Landmark,
  Newspaper,
  Users,
} from 'lucide-react'

import { BIAS_SAMPLES } from '@/lib/constants'

interface InputAreaProps {
  onSend: (text: string) => Promise<void>
  isAnalyzing?: boolean
  onSampleSelect?: (text: string) => void
  ghostMode?: boolean
  onCancel?: () => void
}

const samples = [
  {
    key: 'gender',
    label: 'Gender',
    icon: Users,
  },
  {
    key: 'political',
    label: 'Political',
    icon: Landmark,
  },
  {
    key: 'racial',
    label: 'Racial',
    icon: Users,
  },
  {
    key: 'media',
    label: 'Media',
    icon: Newspaper,
  },
  {
    key: 'corporate',
    label: 'Corporate',
    icon: Briefcase,
  },
] as const

export const InputArea: React.FC<InputAreaProps> = ({
  onSend,
  isAnalyzing = false,
  onSampleSelect,
  ghostMode = false,
  onCancel,
}) => {
  const [text, setText] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (!textareaRef.current) return

    textareaRef.current.style.height = '24px'

    textareaRef.current.style.height = `${Math.min(
      textareaRef.current.scrollHeight,
      140,
    )}px`
  }, [text])

  const canSend =
    text.trim().length > 0 &&
    !isLoading &&
    !isAnalyzing

  const handleSubmit = async () => {
    if (!canSend) return

    try {
      setIsLoading(true)

      await onSend(text)

      setText('')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSampleClick = (
    sampleKey: keyof typeof BIAS_SAMPLES,
  ) => {
    const sample = BIAS_SAMPLES[sampleKey]

    setText(sample)

    onSampleSelect?.(sample)
  }

  const handleKeyDown = (
    e: React.KeyboardEvent<HTMLTextAreaElement>,
  ) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()

      handleSubmit()
    }
  }

  return (
    <div className="border-t border-white/[0.04] bg-bg-1/70 px-4 py-4 backdrop-blur-xl">
      <div className="mx-auto max-w-4xl">
        {/* Samples */}
        <div className="mb-3 flex flex-wrap gap-2">
          {samples.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              type="button"
              onClick={() => handleSampleClick(key)}
              className="
                group
                flex items-center gap-1.5

                rounded-full

                border border-white/[0.06]
                bg-white/[0.03]

                px-3 py-1.5

                text-[11px]
                font-medium
                tracking-[-0.01em]
                text-text-3

                backdrop-blur-md

                transition-all duration-200
                ease-[cubic-bezier(0.22,1,0.36,1)]

                hover:border-white/[0.09]
                hover:bg-white/[0.05]
                hover:text-text-1
                hover:shadow-[0_0_20px_rgba(255,255,255,0.03)]

                active:scale-95
              "
            >
              <Icon
                className="
                  h-3.5 w-3.5
                  transition-transform duration-200
                  group-hover:scale-110
                "
              />

              {label}
            </button>
          ))}
        </div>

        {/* Ghost Notice */}
        {ghostMode && (
          <div
            className="
              mb-3
              flex items-center gap-2

              rounded-2xl

              border border-accent/10
              bg-accent/[0.045]

              px-3 py-2.5

              text-[11px]
              font-medium
              tracking-[-0.01em]
              text-accent

              backdrop-blur-md
            "
          >
            <div className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />

            <span>
              Incognito mode enabled — conversations are not stored.
            </span>
          </div>
        )}

        {/* Input Shell */}
        <div
          className="
            relative

            rounded-[30px]

            bg-bg-2/70
            backdrop-blur-2xl

            shadow-[0_0_0_1px_rgba(255,255,255,0.05)]

            transition-all duration-300
            ease-[cubic-bezier(0.22,1,0.36,1)]

            hover:bg-bg-2/80

            focus-within:bg-bg-2/90
            focus-within:shadow-[0_0_0_1px_rgba(99,102,241,0.20),0_0_40px_rgba(99,102,241,0.08)]
          "
        >
          {/* Ambient Glow */}
          <div
            className="
              pointer-events-none
              absolute inset-0 rounded-[inherit]

              bg-[radial-gradient(circle_at_top,rgba(99,102,241,0.12),transparent_70%)]

              opacity-70
            "
          />

          {/* Content */}
          <div className="relative flex items-end gap-2.5 px-3 py-2.5">
            {/* Textarea */}
            <textarea
              ref={textareaRef}
              value={text}
              onChange={e => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              placeholder={
                ghostMode
                  ? 'Chat privately in incognito mode...'
                  : 'Analyze language, framing, and bias...'
              }
              className="
                min-h-7
                max-h-36
                flex-1
                resize-none

                bg-transparent

                px-1.5 py-2

                text-[15px]
                font-normal
                leading-6
                tracking-[-0.015em]

                text-text-1
                placeholder:text-text-4
                placeholder:font-normal

                outline-none
              "
            />

            {/* Actions */}
            <div className="flex items-center justify-end pb-0.5">
              {isAnalyzing ? (
                <button
                  type="button"
                  onClick={() => onCancel?.()}
                  aria-label="Cancel generation"
                  className="
                    group
                    relative

                    flex h-10 w-10
                    flex-shrink-0
                    items-center justify-center

                    rounded-full

                    border border-white/[0.06]
                    bg-white/[0.04]

                    text-text-2

                    backdrop-blur-md

                    transition-all duration-200
                    ease-[cubic-bezier(0.22,1,0.36,1)]

                    hover:border-white/[0.09]
                    hover:bg-white/[0.06]
                    hover:shadow-[0_0_24px_rgba(255,255,255,0.05)]

                    active:scale-90
                  "
                >
                  <div
                    className="
                      h-2.5 w-2.5
                      rounded-[3px]
                      bg-current

                      transition-transform duration-200

                      group-hover:scale-90
                    "
                  />
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={!canSend}
                  aria-label="Analyze"
                  className={clsx(
                    `
                      group
                      relative

                      flex h-10 w-10
                      flex-shrink-0
                      items-center justify-center

                      rounded-full

                      transition-all duration-200
                      ease-[cubic-bezier(0.22,1,0.36,1)]

                      active:scale-90
                    `,
                    canSend
                      ? `
                          bg-accent
                          text-white

                          shadow-[0_6px_30px_rgba(99,102,241,0.35)]

                          hover:scale-105
                          hover:bg-accent-hover
                          hover:shadow-[0_10px_40px_rgba(99,102,241,0.45)]
                        `
                      : `
                          cursor-not-allowed

                          bg-white/[0.06]
                          text-white/30
                        `,
                  )}
                >
                  {/* Button Glow */}
                  {canSend && (
                    <div
                      className="
                        absolute inset-0 rounded-full

                        bg-[radial-gradient(circle,rgba(255,255,255,0.22),transparent_70%)]

                        opacity-80
                      "
                    />
                  )}

                  <ArrowUp
                    className="
                      relative z-10

                      h-4 w-4

                      transition-transform duration-200

                      group-hover:-translate-y-[1px]
                    "
                  />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}