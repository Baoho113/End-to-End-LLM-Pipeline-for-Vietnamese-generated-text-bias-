import { Router } from 'express'
import * as chatController from '../controllers/chatController'
import { authMiddleware } from '../middleware/auth'

const router = Router()

// All chat routes require authentication
router.use(authMiddleware)

router.post('/', chatController.saveChat)
router.get('/:conversationId', chatController.getConversationChats)
router.delete('/:id', chatController.deleteChat)

export default router
