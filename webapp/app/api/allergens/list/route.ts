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

export async function GET() {
  try {
    const decoded = getUserFromCookie()
    if (!decoded?.email) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

    const user = await prisma.user.findUnique({ where: { email: decoded.email } })
    if (!user) return NextResponse.json({ allergens: [] })

    const items = await prisma.userAllergen.findMany({ where: { userId: user.id }, orderBy: { createdAt: 'desc' } })
    return NextResponse.json({
      allergens: items.map((i) => ({
        id: i.id,
        name: i.name,
        synonyms: safeParseArray(i.synonyms),
        severity: i.severity || 'moderate',
      })),
    })
  } catch (err) {
    console.error('Allergen list failed:', err)
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}

function safeParseArray(val: string | null): string[] {
  if (!val) return []
  try {
    const parsed = JSON.parse(val)
    return Array.isArray(parsed) ? parsed : []
  } catch (e) {
    return []
  }
}
