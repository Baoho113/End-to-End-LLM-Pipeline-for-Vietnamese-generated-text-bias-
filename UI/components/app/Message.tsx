import React from 'react'
import { ChatMessage } from '@/types'
import { BiasCard } from '@/components/ui'
import { truncateText } from '@/lib/utils'
import clsx from 'clsx'

interface MessageProps {
  message: ChatMessage
}

export const Message: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.role === 'user'

  return (
    <div className={clsx('flex flex-col max-w-xs', isUser ? 'items-end self-end' : 'items-start self-start')}>
      <div
        className={clsx(
          'px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed',
          isUser
            ? 'bg-accent text-white rounded-br-sm'
            : 'bg-bg-2 border border-border text-text-2 rounded-bl-sm',
        )}
      >
        {truncateText(message.text, 200)}
      </div>

      {message.biasData && !isUser && (
        <div className="mt-2 w-full">
          <BiasCard data={message.biasData} />
        </div>
      )}
    </div>
  )
}
