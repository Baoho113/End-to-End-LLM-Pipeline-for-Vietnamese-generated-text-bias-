'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { ChatMessage } from '@/types'
import { apiClient } from '@/lib/apiClient'
import { generateId } from '@/lib/utils'

interface ConversationSummary {
  id: string
  title: string
  pinned: boolean
  createdAt: string
  updatedAt: string
  _count: {
    chats: number
  }
}

interface UseChatReturn {
  messages: ChatMessage[]
  isAnalyzing: boolean
  conversations: ConversationSummary[]
  archivedConversations: ConversationSummary[]
  activeConversationId: string | null
  ghostMode: boolean
  cancelAnalysis: () => void
  selectConversation: (conversationId: string) => Promise<void>
  renameConversation: (conversationId: string, title: string) => Promise<void>
  togglePinConversation: (conversationId: string) => Promise<void>
  archiveConversation: (conversationId: string) => Promise<void>
  unarchiveConversation: (conversationId: string) => Promise<void>
  deleteConversation: (conversationId: string) => Promise<void>
  toggleGhostMode: () => Promise<void>
  sendMessage: (text: string) => Promise<void>
  clearChat: () => Promise<void>
}

export const useChat = (): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [archivedConversations, setArchivedConversations] = useState<ConversationSummary[]>([])
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null)
  const [ghostMode, setGhostMode] = useState(false)
  const [prevActiveConversationId, setPrevActiveConversationId] = useState<string | null>(null)
  const analysisTimeoutRef = useRef<number | null>(null)
  const TIMEOUT_MS = 30000 // 30 seconds

  const loadConversationChats = useCallback(async (conversationId: string) => {
    try {
      const chats = await apiClient.getConversationChats(conversationId)
      setMessages(
        chats.map((chat: any) => ({
          id: chat.id,
          role: chat.role,
          text: chat.text,
          biasData: chat.biasData ? JSON.parse(chat.biasData) : undefined,
          timestamp: new Date(chat.createdAt).getTime(),
        })),
      )
      setActiveConversationId(conversationId)
    } catch (error) {
      console.error('Failed to load conversation chats:', error)
      setMessages([])
      setActiveConversationId(conversationId)
    }
  }, [])

  const loadConversations = useCallback(async () => {
    try {
      const [active, archived] = await Promise.all([
        apiClient.listConversations(false),
        apiClient.listConversations(true),
      ])
      setConversations(active)
      setArchivedConversations(archived)
      if (active.length > 0) {
        await loadConversationChats(active[0].id)
      }
    } catch (error) {
      console.error('Failed to load conversations:', error)
    }
  }, [loadConversationChats])

  const createConversation = useCallback(async (title = 'New analysis') => {
    try {
      const conversation = await apiClient.createConversation(title)
      const conv = { ...conversation, _count: conversation._count ?? { chats: 0 } }
      setConversations(prev => [conv, ...prev])
      setMessages([])
      setActiveConversationId(conv.id)
      return conv.id
    } catch (error) {
      console.error('Failed to create conversation:', error)
      return null
    }
  }, [])

  const renameConversation = useCallback(
    async (conversationId: string, title: string) => {
      try {
        const updated = await apiClient.updateConversation(conversationId, { title })
        setConversations(prev => prev.map(conv => (conv.id === conversationId ? { ...conv, title: updated.title } : conv)))
      } catch (error) {
        console.error('Failed to rename conversation:', error)
      }
    },
    [],
  )

  const togglePinConversation = useCallback(
    async (conversationId: string) => {
      const target = conversations.find(conv => conv.id === conversationId)
      if (!target) return

      try {
        const updated = await apiClient.updateConversation(conversationId, { pinned: !target.pinned })
        setConversations(prev =>
          prev
            .map(conv => (conv.id === conversationId ? { ...conv, pinned: updated.pinned } : conv))
            .sort((a, b) => Number(b.pinned) - Number(a.pinned) || new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()),
        )
      } catch (error) {
        console.error('Failed to pin/unpin conversation:', error)
      }
    },
    [conversations],
  )

  const archiveConversation = useCallback(
    async (conversationId: string) => {
      try {
        const updated = await apiClient.updateConversation(conversationId, { archived: true })
        setConversations(prev => prev.filter(conv => conv.id !== conversationId))
        setArchivedConversations(prev => [updated, ...prev])

        if (activeConversationId === conversationId) {
          if (conversations.length > 0) {
            const nextConversation = conversations.find(conv => conv.id !== conversationId)
            if (nextConversation) {
              await loadConversationChats(nextConversation.id)
            } else {
              setMessages([])
              setActiveConversationId(null)
            }
          } else {
            setMessages([])
            setActiveConversationId(null)
          }
        }
      } catch (error) {
        console.error('Failed to archive conversation:', error)
      }
    },
    [activeConversationId, conversations, loadConversationChats],
  )

  const unarchiveConversation = useCallback(
    async (conversationId: string) => {
      try {
        const updated = await apiClient.updateConversation(conversationId, { archived: false })
        setArchivedConversations(prev => prev.filter(conv => conv.id !== conversationId))
        setConversations(prev => [updated, ...prev].sort((a, b) => Number(b.pinned) - Number(a.pinned) || new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()))
      } catch (error) {
        console.error('Failed to unarchive conversation:', error)
      }
    },
    [],
  )

  const deleteConversation = useCallback(
    async (conversationId: string) => {
      try {
        await apiClient.deleteConversation(conversationId)
        setConversations(prev => prev.filter(conv => conv.id !== conversationId))

        if (activeConversationId === conversationId) {
          const nextConversation = conversations.find(conv => conv.id !== conversationId)
          if (nextConversation) {
            await loadConversationChats(nextConversation.id)
          } else {
            setMessages([])
            setActiveConversationId(null)
          }
        }
      } catch (error) {
        console.error('Failed to delete conversation:', error)
      }
    },
    [activeConversationId, conversations, loadConversationChats],
  )

  const selectConversation = useCallback(
    async (conversationId: string) => {
      await loadConversationChats(conversationId)
    },
    [loadConversationChats],
  )

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim()) return

      setIsAnalyzing(true)
      // start timeout to guard against infinite analysis
      if (typeof window !== 'undefined') {
        analysisTimeoutRef.current = window.setTimeout(() => {
          analysisTimeoutRef.current = null
          setIsAnalyzing(false)
          setMessages(prev => [
            ...prev,
            {
              id: generateId(),
              role: 'assistant',
              text: 'Error: analysis timed out. Please try again.',
              timestamp: Date.now(),
            },
          ])
        }, TIMEOUT_MS)
      }

      const targetConversationId = ghostMode ? null : activeConversationId ?? (await createConversation())
      if (!ghostMode && !targetConversationId) {
        setIsAnalyzing(false)
        return
      }

      const userMessage: ChatMessage = {
        id: generateId(),
        role: 'user',
        text,
        timestamp: Date.now(),
      }

      setMessages(prev => [...prev, userMessage])

      if (!ghostMode) {
        try {
          await apiClient.saveChat(targetConversationId!, 'user', text)
        } catch (error) {
          console.error('Failed to save user message:', error)
        }
      }

      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        text: ghostMode
          ? 'Ghost mode is active — this response is shown locally and will not be saved.'
          : 'Assistant response is pending integration.',
        timestamp: Date.now(),
      }

      setMessages(prev => [...prev, assistantMessage])

      if (!ghostMode) {
        try {
          await apiClient.saveChat(targetConversationId!, 'assistant', assistantMessage.text)
        } catch (error) {
          console.error('Failed to save assistant placeholder:', error)
        }
      }
    },
    [activeConversationId, createConversation, ghostMode],
  )

  // cancel or clear an ongoing analysis
  const cancelAnalysis = useCallback(() => {
    if (analysisTimeoutRef.current) {
      clearTimeout(analysisTimeoutRef.current)
      analysisTimeoutRef.current = null
    }
    setIsAnalyzing(false)
    setMessages(prev => [
      ...prev,
      {
        id: generateId(),
        role: 'assistant',
        text: 'Analysis cancelled by user.',
        timestamp: Date.now(),
      },
    ])
  }, [])


  const clearChat = useCallback(async () => {
    setMessages([])
    setActiveConversationId(null)
  }, [])

  const toggleGhostMode = useCallback(async () => {
    const enabling = !ghostMode
    if (enabling) {
      // entering ghost mode: save current active convo and clear chat
      setPrevActiveConversationId(activeConversationId)
      setGhostMode(true)
      setMessages([])
      setActiveConversationId(null)
      return
    }

    // disabling ghost mode: restore previous conversation if available
    setGhostMode(false)
    const restoreId = prevActiveConversationId
    setPrevActiveConversationId(null)
    if (restoreId) {
      try {
        await loadConversationChats(restoreId)
      } catch (err) {
        console.error('Failed to restore conversation after disabling ghost mode:', err)
        await loadConversations()
      }
    } else {
      await loadConversations()
    }
  }, [ghostMode, activeConversationId, prevActiveConversationId, loadConversationChats, loadConversations])

  return {
    messages,
    isAnalyzing,
    conversations,
    archivedConversations,
    activeConversationId,
    ghostMode,
    cancelAnalysis,
    selectConversation,
    renameConversation,
    togglePinConversation,
    archiveConversation,
    unarchiveConversation,
    deleteConversation,
    toggleGhostMode,
    sendMessage,
    clearChat,
  }
}
