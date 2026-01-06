import { NextResponse } from 'next/server'
import jwt from 'jsonwebtoken'
import { cookies } from 'next/headers'

export async function GET() {
  try {
    const cookieStore = await cookies()
    const token = cookieStore.get('next-auth.session-token')?.value

    if (!token) {
      return NextResponse.json({ user: null }, { headers: { 'Cache-Control': 'no-store' } })
    }

    const secret = process.env.NEXTAUTH_SECRET || 'dev-secret'
    const decoded = jwt.verify(token, secret) as any
    return NextResponse.json({
      user: {
        id: decoded.id,
        email: decoded.email,
        name: decoded.name
      }
    }, { headers: { 'Cache-Control': 'no-store' } })
  } catch (err) {
    return NextResponse.json({ user: null }, { headers: { 'Cache-Control': 'no-store' } })
  }
}
