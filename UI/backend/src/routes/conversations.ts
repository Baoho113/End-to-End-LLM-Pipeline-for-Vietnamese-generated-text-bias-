import { Router } from 'express'
import * as conversationController from '../controllers/conversationController'
import { authMiddleware } from '../middleware/auth'

const router = Router()

// All conversation routes require authentication
router.use(authMiddleware)

router.post('/', conversationController.createConversation)
router.get('/', conversationController.listConversations)
router.get('/:id', conversationController.getConversation)
router.patch('/:id', conversationController.updateConversation)
router.delete('/:id', conversationController.deleteConversation)

export default router
