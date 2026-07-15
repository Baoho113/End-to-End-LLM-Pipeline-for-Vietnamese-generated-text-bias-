import express, { Express, Request, Response } from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import { PrismaClient } from '@prisma/client'

// Import routes
import authRoutes from './routes/auth'
import conversationRoutes from './routes/conversations'
import chatRoutes from './routes/chats'

// Initialize environment variables
dotenv.config()

const app: Express = express()
const prisma = new PrismaClient()
const PORT = process.env.PORT || 3001
const CORS_ORIGIN = process.env.CORS_ORIGIN || 'http://localhost:3000'

// Middleware
app.use(express.json())
app.use(express.urlencoded({ extended: true }))
app.use(
  cors({
    origin: CORS_ORIGIN,
    credentials: true,
  })
)

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', timestamp: new Date() })
})

// API Routes
app.use('/api/auth', authRoutes)
app.use('/api/conversations', conversationRoutes)
app.use('/api/chats', chatRoutes)

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({ error: 'Route not found' })
})

// Error handler
app.use((err: any, req: Request, res: Response) => {
  console.error('Error:', err)
  res.status(500).json({ error: 'Internal server error' })
})

// Start server
async function main() {
  try {
    // Test database connection
    await prisma.$connect()
    console.log('✅ Database connected')

    app.listen(PORT, () => {
      console.log(`🚀 Server running on http://localhost:${PORT}`)
      console.log(`📝 API Documentation:`)
      console.log(`   - POST /api/auth/register - Register new user`)
      console.log(`   - POST /api/auth/login - Login user`)
      console.log(`   - GET /api/auth/me - Get current user`)
      console.log(`   - POST /api/conversations - Create conversation`)
      console.log(`   - GET /api/conversations - List conversations`)
      console.log(`   - GET /api/conversations/:id - Get conversation with chats`)
      console.log(`   - PATCH /api/conversations/:id - Update conversation`)
      console.log(`   - DELETE /api/conversations/:id - Delete conversation`)
      console.log(`   - POST /api/chats - Save chat message`)
      console.log(`   - GET /api/chats/:conversationId - Get chats in conversation`)
      console.log(`   - DELETE /api/chats/:id - Delete chat`)
    })
  } catch (error) {
    console.error('❌ Failed to start server:', error)
    await prisma.$disconnect()
    process.exit(1)
  }
}

// Handle graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully...')
  await prisma.$disconnect()
  process.exit(0)
})

process.on('SIGINT', async () => {
  console.log('SIGINT received, shutting down gracefully...')
  await prisma.$disconnect()
  process.exit(0)
})

main()
