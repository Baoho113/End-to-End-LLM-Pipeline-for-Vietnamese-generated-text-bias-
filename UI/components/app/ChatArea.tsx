import React, { useRef, useEffect } from 'react'
import { ChatMessage as ChatMessageType } from '@/types'
import { Message } from './Message'
import { ThinkingIndicator } from './ThinkingIndicator'
import { WelcomeScreen } from './WelcomeScreen'

interface ChatAreaProps {
  messages: ChatMessageType[]
  isAnalyzing: boolean
}

export const ChatArea: React.FC<ChatAreaProps> = ({ messages, isAnalyzing }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isAnalyzing])

  return (
    <div className="flex-1 overflow-y-auto px-4 py-5 flex flex-col gap-3 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-bg-2">
      {messages.length === 0 ? (
        <WelcomeScreen />
      ) : (
        messages.map(msg => (
          <Message key={msg.id} message={msg} />
        ))
      )}

      {isAnalyzing && <ThinkingIndicator />}
      <div ref={messagesEndRef} />
    </div>
  )
}
