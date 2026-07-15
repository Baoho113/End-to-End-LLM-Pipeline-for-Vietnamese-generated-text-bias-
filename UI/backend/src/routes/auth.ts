import { Router } from 'express'
import * as authController from '../controllers/authController'
import { authMiddleware } from '../middleware/auth'

const router = Router()

// Public routes
router.post('/register', authController.register)
router.post('/login', authController.login)

// Protected routes
router.get('/me', authMiddleware, authController.getCurrentUser)

export default router
