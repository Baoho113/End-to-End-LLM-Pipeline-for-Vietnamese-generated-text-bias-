// NEK@NDIDN_CODE
import { Request, Response } from 'express'
import { PrismaClient } from '@prisma/client'
import { hashPassword, comparePassword } from '../utils/password'
import { generateToken } from '../utils/jwt'

const prisma = new PrismaClient()

export async function register(req: Request, res: Response): Promise<void> {
  try {
    const { name, email, password, code } = req.body

    // Validate input
    if (!name || !email || !password || !code) {
      res.status(400).json({ error: 'Missing required fields' })
      return
    }

    // Validate invite code
    const EARLY_ACCESS_CODE = 'NEK@NDIDN_CODE' // This should ideally come from an environment variable
    if (code !== EARLY_ACCESS_CODE) {
      res.status(403).json({ error: 'Invalid early access code' })
      return
    }

    // Check if user exists
    const existingUser = await prisma.user.findUnique({ where: { email } })
    if (existingUser) {
      res.status(409).json({ error: 'Email already registered' })
      return
    }

    // Hash password and create user
    const hashedPassword = await hashPassword(password)
    const user = await prisma.user.create({
      data: {
        name,
        email,
        password: hashedPassword,
      },
    })

    // Generate token
    const token = generateToken({
      userId: user.id,
      email: user.email,
      name: user.name,
    })

    res.status(201).json({
      message: 'User registered successfully',
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
      },
    })
  } catch (error) {
    console.error('Registration error:', error)
    res.status(500).json({ error: 'Registration failed' })
  }
}

export async function login(req: Request, res: Response): Promise<void> {
  try {
    const { email, password } = req.body

    if (!email || !password) {
      res.status(400).json({ error: 'Missing email or password' })
      return
    }

    const user = await prisma.user.findUnique({ where: { email } })
    if (!user) {
      res.status(401).json({ error: 'Invalid email or password' })
      return
    }

    const isValidPassword = await comparePassword(password, user.password)
    if (!isValidPassword) {
      res.status(401).json({ error: 'Invalid email or password' })
      return
    }

    const token = generateToken({
      userId: user.id,
      email: user.email,
      name: user.name,
    })

    res.json({
      message: 'Login successful',
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
      },
    })
  } catch (error) {
    console.error('Login error:', error)
    res.status(500).json({ error: 'Login failed' })
  }
}

export async function getCurrentUser(req: Request, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ error: 'Not authenticated' })
      return
    }

    const user = await prisma.user.findUnique({
      where: { id: req.user.userId },
      select: {
        id: true,
        name: true,
        email: true,
        createdAt: true,
      },
    })

    res.json(user)
  } catch (error) {
    console.error('Get user error:', error)
    res.status(500).json({ error: 'Failed to fetch user' })
  }
}
