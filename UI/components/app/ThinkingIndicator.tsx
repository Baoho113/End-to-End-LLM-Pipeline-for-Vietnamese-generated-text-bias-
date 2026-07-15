import React from 'react'

export const ThinkingIndicator: React.FC = () => {
  return (
    <div className="flex items-center gap-1 px-3.5 py-2.5 bg-bg-2 border border-border rounded-2xl rounded-bl-sm self-start">
      <span className="w-1 h-1 rounded-full bg-text-3 animate-thinking" style={{ animationDelay: '0s' }} />
      <span className="w-1 h-1 rounded-full bg-text-3 animate-thinking" style={{ animationDelay: '0.2s' }} />
      <span className="w-1 h-1 rounded-full bg-text-3 animate-thinking" style={{ animationDelay: '0.4s' }} />
    </div>
  )
}
