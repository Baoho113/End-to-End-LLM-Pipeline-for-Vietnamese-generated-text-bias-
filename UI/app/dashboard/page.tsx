'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ChatArea, InputArea } from '@/components/app'
import { Sidebar, Topbar } from '@/components/layout'
import { useAuth, useChat } from '@/hooks'

export default function DashboardPage() {
  const router = useRouter()
  const { user, isLoading, logout } = useAuth()
  const {
    messages,
    conversations,
    archivedConversations,
    activeConversationId,
    isAnalyzing,
    ghostMode,
    toggleGhostMode,
    cancelAnalysis,
    sendMessage,
    clearChat,
    selectConversation,
    renameConversation,
    togglePinConversation,
    archiveConversation,
    unarchiveConversation,
    deleteConversation,
  } = useChat()

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace('/auth/login')
    }
  }, [isLoading, router, user])

  const handleLogout = () => {
    logout()
    router.replace('/auth/login')
  }

  if (isLoading || !user) {
    return null
  }

  return (
    <main className="flex h-screen w-full bg-bg-0">
      <Sidebar
        userName={user.name}
        conversations={conversations}
        archivedConversations={archivedConversations}
        activeConversationId={activeConversationId}
        onNewChat={clearChat}
        onSelectConversation={selectConversation}
        onRenameConversation={renameConversation}
        onTogglePinConversation={togglePinConversation}
        onArchiveConversation={archiveConversation}
        onUnarchiveConversation={unarchiveConversation}
        onDeleteConversation={deleteConversation}
        onLogout={handleLogout}
      />
      <section className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <Topbar ghostMode={ghostMode} onToggleGhostMode={toggleGhostMode} />
        <ChatArea messages={messages} isAnalyzing={isAnalyzing} />
        <InputArea onSend={sendMessage} isAnalyzing={isAnalyzing} ghostMode={ghostMode} onCancel={cancelAnalysis} />
      </section>
    </main>
  )
}
