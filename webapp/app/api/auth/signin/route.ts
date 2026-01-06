import { NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import argon2 from 'argon2'
import jwt from 'jsonwebtoken'

export async function POST(req: Request) {
  try {
    const body = await req.json()
    const { email, password } = body

    if (!email || !password) {
      return NextResponse.json({ error: 'Email and password required' }, { status: 400 })
    }

    // Find user
    const user = await prisma.user.findUnique({ where: { email } })
    if (!user) {
      return NextResponse.json({ error: 'Invalid credentials' }, { status: 401 })
    }

    // Verify password
    const valid = await argon2.verify(user.passwordHash, password)
    if (!valid) {
      return NextResponse.json({ error: 'Invalid credentials' }, { status: 401 })
    }

    // Create JWT token
    const secret = process.env.NEXTAUTH_SECRET || 'dev-secret'
    const token = jwt.sign({ id: user.id, email: user.email, name: user.name }, secret, {
      expiresIn: '30d'
    })

    // Set token in httpOnly cookie
    const response = NextResponse.json({ ok: true, user: { id: user.id, email: user.email, name: user.name } })
    response.cookies.set('next-auth.session-token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 30 * 24 * 60 * 60, // 30 days
      path: '/',
    })

    return response
  } catch (e) {
    console.error('Sign in error:', e)
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}
