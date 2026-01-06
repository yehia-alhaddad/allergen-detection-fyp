import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import jwt from 'jsonwebtoken'
import { prisma } from '@/lib/db'

// Shared helper to decode our session cookie
function getUserFromCookie() {
  const cookieStore = cookies()
  const token = cookieStore.get('next-auth.session-token')?.value
  if (!token) return null
  const secret = process.env.NEXTAUTH_SECRET || 'dev-secret'
  try {
    const decoded = jwt.verify(token, secret) as any
    return decoded
  } catch (err) {
    return null
  }
}

export async function GET() {
  try {
    const decoded = getUserFromCookie()
    if (!decoded?.email) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

    const user = await prisma.user.findUnique({ where: { email: decoded.email } })
    if (!user) return NextResponse.json({ scans: [] })

    const scans = await prisma.scanHistory.findMany({
      where: { userId: user.id },
      orderBy: { createdAt: 'desc' },
      take: 50,
    })

    const formatted = scans.map((s) => ({
      id: s.id,
      type: s.type,
      productName: s.productName ?? undefined,
      classification: s.classification,
      matchedAllergens: safeParseJsonArray(s.matchedAllergens),
      createdAt: s.createdAt,
    }))

    return NextResponse.json({ scans: formatted })
  } catch (err) {
    console.error('History fetch failed:', err)
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}

export async function DELETE() {
  try {
    const decoded = getUserFromCookie()
    if (!decoded?.email) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

    const user = await prisma.user.findUnique({ where: { email: decoded.email } })
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

    const result = await prisma.scanHistory.deleteMany({ where: { userId: user.id } })
    return NextResponse.json({ cleared: result.count })
  } catch (err) {
    console.error('History clear failed:', err)
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}

function safeParseJsonArray(val: string | null) {
  if (!val) return []
  try {
    const parsed = JSON.parse(val)
    return Array.isArray(parsed) ? parsed : []
  } catch (err) {
    return []
  }
}
