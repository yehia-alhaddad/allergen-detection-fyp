import { NextResponse } from 'next/server'
import { z } from 'zod'
import { rateLimit } from '@/lib/rateLimiter'
import { prisma } from '@/lib/db'
import { auth } from '@/lib/auth'
import { analyzeIngredients } from '@/lib/allergy'

const Schema = z.object({ text: z.string().min(3) })

export async function POST(req: Request) {
  const ip = (req.headers.get('x-forwarded-for') || 'local').split(',')[0].trim()
  if (!rateLimit(`ingredients:${ip}`)) return NextResponse.json({ error: 'Rate limited' }, { status: 429 })

  const session = await auth()
  let user = null
  if (session?.user?.email) {
    user = await prisma.user.findUnique({ where: { email: session.user.email } })
  }

  const body = await req.json().catch(() => null)
  const parsed = Schema.safeParse(body)
  if (!parsed.success) return NextResponse.json({ error: 'Invalid input' }, { status: 400 })

  let result = { classification: 'SAFE', matches: [] as any[] }
  
  if (user) {
    // Logged-in users: personalized analysis
    const allergens = await prisma.userAllergen.findMany({ where: { userId: user.id } })
    const profile = allergens.map(a => ({
      name: a.name,
      synonyms: Array.isArray((a as any).synonyms)
        ? (a as any).synonyms as string[]
        : (typeof (a as any).synonyms === 'string' ? safeParseArray((a as any).synonyms as unknown as string) : [])
    }))
    result = analyzeIngredients(parsed.data.text, profile)
  } else {
    // Anonymous users: detect all common allergens
    const commonAllergens = ['peanut', 'tree nut', 'milk', 'eggs', 'fish', 'shellfish', 'wheat', 'soy', 'sesame']
    const text = parsed.data.text.toLowerCase()
    const matches = commonAllergens.filter(allergen => text.includes(allergen))
    if (matches.length > 0) {
      result = { classification: 'CAUTION', matches: matches.map(m => ({ name: m })) }
    }
  }

  // Save scan history (only for logged-in users)
  if (user) {
    await prisma.scanHistory.create({
      data: {
        userId: user.id,
        type: 'TEXT',
        productName: 'Ingredient Text',
        classification: result.classification,
        matchedAllergens: JSON.stringify(result.matches),
        inputMetadata: JSON.stringify({ textLength: parsed.data.text.length, source: 'text_input' }),
        storeRawImage: false
      }
    })
  }

  return NextResponse.json({
    classification: result.classification,
    matches: result.matches
  })
}

function safeParseArray(s: string): string[] {
  try { return JSON.parse(s || '[]') ?? [] } catch { return [] }
}
