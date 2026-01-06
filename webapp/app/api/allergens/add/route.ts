import { NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import jwt from 'jsonwebtoken'
import { cookies } from 'next/headers'
import { randomUUID } from 'crypto'

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

export async function POST(req: Request) {
  try {
    const decoded = getUserFromCookie()
    if (!decoded?.email) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

    const body = await req.json()
    const name = (body.name || '').trim()
    const synonyms = body.synonyms ? String(body.synonyms).trim() : ''
    const severity = body.severity || 'moderate'

    if (!name) return NextResponse.json({ error: 'Allergen name is required' }, { status: 400 })

    const user = await prisma.user.findUnique({ where: { email: decoded.email } })
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

    const created = await prisma.userAllergen.create({
      data: {
        id: randomUUID(),
        userId: user.id,
        name,
        synonyms: synonyms ? synonyms : '[]',
        severity,
      },
    })

    return NextResponse.json({
      allergen: {
        id: created.id,
        name: created.name,
        synonyms: safeParseArray(created.synonyms),
        severity: created.severity || 'moderate',
      },
    })
  } catch (err) {
    console.error('Add allergen failed:', err)
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
