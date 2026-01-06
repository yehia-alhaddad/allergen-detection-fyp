import { NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import jwt from 'jsonwebtoken'
import { cookies } from 'next/headers'

function getUserFromCookie() {
  const cookieStore = cookies()
  const token = cookieStore.get('next-auth.session-token')?.value
  if (!token) return null
  const secret = process.env.NEXTAUTH_SECRET || 'dev-secret'
  try {
    return jwt.verify(token, secret) as any
  } catch (err) {
    return null
  }
}

export async function DELETE(req: Request) {
  try {
    const decoded = getUserFromCookie()
    if (!decoded?.email) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

    const { searchParams } = new URL(req.url)
    const id = searchParams.get('id')
    if (!id) return NextResponse.json({ error: 'Missing id' }, { status: 400 })

    const user = await prisma.user.findUnique({ where: { email: decoded.email } })
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

    await prisma.userAllergen.deleteMany({ where: { id, userId: user.id } })
    return NextResponse.json({ ok: true })
  } catch (err) {
    console.error('Delete allergen failed:', err)
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}
