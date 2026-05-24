// NEK@N_NO_CODE
import { Request, Response } from 'express'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export async function saveChat(req: Request, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' })
      return
    }

    const { conversationId, role, text, biasData } = req.body

    if (!conversationId || !role || !text) {
      res.status(400).json({ error: 'Missing required fields' })
      return
    }

    if (!['user', 'assistant'].includes(role)) {
      res.status(400).json({ error: 'Invalid role' })
      return
    }

    // Verify conversation ownership
    const conversation = await prisma.conversation.findFirst({
      where: {
        id: conversationId,
        userId: req.user.userId,
      },
    })

    if (!conversation) {
      res.status(404).json({ error: 'Conversation not found' })
      return
    }

    const chat = await prisma.chat.create({
      data: {
        conversationId,
        userId: req.user.userId,
        role,
        text,
        biasData: biasData ? JSON.stringify(biasData) : null,
      },
    })

    res.status(201).json(chat)
  } catch (error) {
    console.error('Save chat error:', error)
    res.status(500).json({ error: 'Failed to save chat' })
  }
}

export async function getConversationChats(req: Request, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' })
      return
    }

    const { conversationId } = req.params

    // Verify conversation ownership
    const conversation = await prisma.conversation.findFirst({
      where: {
        id: conversationId,
        userId: req.user.userId,
      },
    })

    if (!conversation) {
      res.status(404).json({ error: 'Conversation not found' })
      return
    }

    const chats = await prisma.chat.findMany({
      where: { conversationId },
      orderBy: { createdAt: 'asc' },
    })

    res.json(chats)
  } catch (error) {
    console.error('Get chats error:', error)
    res.status(500).json({ error: 'Failed to fetch chats' })
  }
}

export async function deleteChat(req: Request, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' })
      return
    }

    const { id } = req.params

    const chat = await prisma.chat.findUnique({ where: { id } })

    if (!chat || chat.userId !== req.user.userId) {
      res.status(404).json({ error: 'Chat not found' })
      return
    }

    await prisma.chat.delete({ where: { id } })
    res.json({ message: 'Chat deleted' })
  } catch (error) {
    console.error('Delete chat error:', error)
    res.status(500).json({ error: 'Failed to delete chat' })
  }
}
