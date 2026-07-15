'use client'

import { useState } from 'react'
import { Button } from '@/components/ui'
import { DETECTION_SAMPLES } from '@/lib/constants'
import { Sparkles } from 'lucide-react'

interface InputStageProps {
  onSubmit: (text: string) => void
  loading: boolean
}

export function InputStage({ onSubmit, loading }: InputStageProps) {
  const [text, setText] = useState('')

  return (
    <div className="rounded-lg bg-bg-2 border border-border-subtle overflow-hidden">
      <div className="flex flex-wrap gap-2 px-4 py-3 border-b border-border">
        {DETECTION_SAMPLES.map((sample) => (
          <button
            key={sample.key}
            type="button"
            onClick={() => setText(sample.text)}
            className="text-xs px-3 py-1.5 rounded-full bg-bg-3 border border-border-subtle text-text-3 hover:text-text-1 hover:border-opacity-40 transition-colors"
          >
            {sample.label}
          </button>
        ))}
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Dán văn bản tiếng Việt do AI tạo ra để phân tích..."
        rows={5}
        className="w-full resize-none bg-transparent px-4 py-4 text-[15px] leading-relaxed text-text-1 placeholder:text-text-4 outline-none"
      />

      <div className="flex items-center justify-between px-4 py-3 border-t border-border">
        <span className="text-xs text-text-4">{text.length} characters</span>
        <Button
          icon={<Sparkles size={15} />}
          disabled={!text.trim()}
          loading={loading}
          onClick={() => onSubmit(text.trim())}
        >
          Phân tích văn bản
        </Button>
      </div>
    </div>
  )
}
