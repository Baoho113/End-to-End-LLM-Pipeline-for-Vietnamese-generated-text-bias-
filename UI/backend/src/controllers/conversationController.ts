import { Request, Response } from 'express'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export async function createConversation(req: Request, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' })
      return
    }

    const { title } = req.body

    const conversation = await prisma.conversation.create({
      data: {
        userId: req.user.userId,
        title: title || 'Untitled',
        pinned: false,
        archived: false,
      },
    })

    res.status(201).json(conversation)
  } catch (error) {
    console.error('Create conversation error:', error)
    res.status(500).json({ error: 'Failed to create conversation' })
  }
}

export async function listConversations(req: Request, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' })
      return
    }

    const archivedParam = req.query.archived
    const archived = archivedParam === 'true'

    const conversations = await prisma.conversation.findMany({
      where: {
        userId: req.user.userId,
        archived,
      },
      orderBy: [
        { pinned: 'desc' },
        { updatedAt: 'desc' },
      ],
      include: {
        _count: {
          select: { chats: true },
        },
      },
    })

    res.json(conversations)
  } catch (error) {
    console.error('List conversations error:', error)
    res.status(500).json({ error: 'Failed to fetch conversations' })
  }
}

export async function getConversation(req: Request, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' })
      return
    }

    const { id } = req.params

    const conversation = await prisma.conversation.findFirst({
      where: {
        id,
        userId: req.user.userId,
      },
      include: {
        chats: {
          orderBy: { createdAt: 'asc' },
        },
      },
    })

    if (!conversation) {
      res.status(404).json({ error: 'Conversation not found' })
      return
    }

    res.json(conversation)
  } catch (error) {
    console.error('Get conversation error:', error)
    res.status(500).json({ error: 'Failed to fetch conversation' })
  }
}

export async function updateConversation(req: Request, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' })
      return
    }

    const { id } = req.params
    const { title, pinned, archived } = req.body

    // Verify ownership
    const conversation = await prisma.conversation.findFirst({
      where: {
        id,
        userId: req.user.userId,
      },
    })

    if (!conversation) {
      res.status(404).json({ error: 'Conversation not found' })
      return
    }

    const updated = await prisma.conversation.update({
      where: { id },
      data: {
        ...(title !== undefined ? { title } : {}),
        ...(pinned !== undefined ? { pinned } : {}),
        ...(archived !== undefined ? { archived } : {}),
      },
    })

    res.json(updated)
  } catch (error) {
    console.error('Update conversation error:', error)
    res.status(500).json({ error: 'Failed to update conversation' })
  }
}

export async function deleteConversation(req: Request, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' })
      return
    }

    const { id } = req.params

    // Verify ownership
    const conversation = await prisma.conversation.findFirst({
      where: {
        id,
        userId: req.user.userId,
      },
    })

    if (!conversation) {
      res.status(404).json({ error: 'Conversation not found' })
      return
    }

    await prisma.conversation.delete({ where: { id } })
    res.json({ message: 'Conversation deleted' })
  } catch (error) {
    console.error('Delete conversation error:', error)
    res.status(500).json({ error: 'Failed to delete conversation' })
  }
}
