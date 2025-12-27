import { NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import { auth } from '@/lib/auth'

export async function GET() {
  const session = await auth()
  if (!session?.user?.email) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  const user = await prisma.user.findUnique({ where: { email: session.user.email } })
  if (!user) return NextResponse.json({ allergens: [] })
  const items = await prisma.userAllergen.findMany({ where: { userId: user.id } })
  return NextResponse.json({
    allergens: items.map(i => ({
      name: i.name,
      synonyms: Array.isArray((i as any).synonyms)
        ? (i as any).synonyms as string[]
        : (typeof (i as any).synonyms === 'string' ? safeParseArray((i as any).synonyms as unknown as string) : []),
      severity: i.severity
    }))
  })
}

export async function POST(req: Request) {
  const session = await auth()
  if (!session?.user?.email) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  const user = await prisma.user.findUnique({ where: { email: session.user.email } })
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  const body = await req.json()
  const allergens: string[] = Array.isArray(body.allergens) ? body.allergens : []
  const synonyms: string[] = Array.isArray(body.synonyms) ? body.synonyms : []
  const custom = typeof body.customAllergen === 'string' && body.customAllergen ? [body.customAllergen] : []
  const all = [...allergens, ...custom]

  // Upsert: clear existing then add
  await prisma.userAllergen.deleteMany({ where: { userId: user.id } })
  for (const name of all) {
    await prisma.userAllergen.create({ data: { userId: user.id, name, synonyms: JSON.stringify(synonyms) } })
  }
  return NextResponse.json({ ok: true })
}

function safeParseArray(s: string): string[] {
  try { return JSON.parse(s || '[]') ?? [] } catch { return [] }
}
