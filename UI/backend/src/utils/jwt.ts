import jwt, { JsonWebTokenError } from 'jsonwebtoken'
import type { StringValue } from 'ms'

export interface JwtPayload {
  userId: string
  email: string
  name: string
}

const JWT_SECRET = process.env.JWT_SECRET || 'your_secret_key'
const JWT_EXPIRATION = (process.env.JWT_EXPIRATION || '24h') as StringValue

export function generateToken(payload: JwtPayload): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRATION })
}

export function verifyToken(token: string): JwtPayload {
  try {
    return jwt.verify(token, JWT_SECRET) as JwtPayload
  } catch (error) {
    if (error instanceof JsonWebTokenError) {
      throw new Error('Invalid or expired token')
    }
    throw error
  }
}
