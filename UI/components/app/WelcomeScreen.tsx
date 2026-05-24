import React from 'react'
import { Eye } from 'lucide-react'

export const WelcomeScreen: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center flex-1 text-center gap-3 p-5 min-h-64">
      <div className="w-14 h-14 rounded-2xl bg-accent-dim border border-accent-border flex items-center justify-center text-2xl text-accent-text">
        <Eye size={28} />
      </div>
      <div className="text-lg font-medium text-text-1">Paste any text to detect bias</div>
      <div className="text-sm text-text-3 max-w-xs leading-relaxed">
        Analyzes gender, political, racial, and sentiment bias in seconds. Use the sample chips below to get started.
      </div>
    </div>
  )
}
