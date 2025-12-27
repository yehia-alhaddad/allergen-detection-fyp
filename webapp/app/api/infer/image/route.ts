import { NextResponse } from 'next/server'
import { rateLimit } from '@/lib/rateLimiter'
import { prisma } from '@/lib/db'
import { auth } from '@/lib/auth'
import { run_model_from_service, run_model_stub } from '@/lib/inference'
import { analyzeIngredients } from '@/lib/allergy'

export const runtime = 'nodejs'

export async function POST(req: Request) {
  const ip = (req.headers.get('x-forwarded-for') || 'local').split(',')[0].trim()
  if (!rateLimit(`image:${ip}`)) return NextResponse.json({ error: 'Rate limited' }, { status: 429 })

  const session = await auth()
  let user = null
  if (session?.user?.email) {
    user = await prisma.user.findUnique({ where: { email: session.user.email } })
  }

  const form = await req.formData().catch(() => null)
  const file = form?.get('file') as File | null
  if (!file) return NextResponse.json({ error: 'Missing image file' }, { status: 400 })

  const buffer = Buffer.from(await file.arrayBuffer())
  const base64 = buffer.toString('base64')

  let inference
  try {
    inference = await run_model_from_service(base64)
  } catch {
    inference = await run_model_stub(base64)
  }

  // Prefer cleaned text from API for downstream matching
  const pseudoText = (inference.cleanedText || inference.rawText || inference.labels.join(', ')).toString()
  let result = { classification: 'SAFE' as const, matches: [] as any[] }
  
  if (user) {
    // Logged-in users: personalized analysis
    const allergens = await prisma.userAllergen.findMany({ where: { userId: user.id } })
    const profile = allergens.map(a => ({
      name: a.name,
      synonyms: Array.isArray((a as any).synonyms)
        ? (a as any).synonyms as string[]
        : (typeof (a as any).synonyms === 'string' ? safeParseArray((a as any).synonyms as unknown as string) : [])
    }))
    result = analyzeIngredients(pseudoText, profile)
  } else {
    // Anonymous users: use ML API detected_allergens directly for higher accuracy
    const detected = inference.detectedAllergens || {}
    const keys = Object.keys(detected)
    if (keys.length > 0) {
      result = { classification: 'CAUTION', matches: keys.map(k => ({ name: k })) }
    }
  }

  // Save scan history (only for logged-in users)
  if (user) {
    await prisma.scanHistory.create({
      data: {
        userId: user.id,
        type: 'IMAGE',
        productName: `Product (${new Date().toISOString()})`,
        classification: result.classification,
        matchedAllergens: JSON.stringify(result.matches),
        inputMetadata: JSON.stringify({ labels: inference.labels, source: 'ml_inference' }),
        storeRawImage: false
      }
    })
  }

  return NextResponse.json({
    classification: result.classification,
    matches: result.matches,
    labels: inference.labels,
    rawText: inference.rawText,
    cleanedText: inference.cleanedText,
    segments: inference.segments,
  })
}

function safeParseArray(s: string): string[] {
  try { return JSON.parse(s || '[]') ?? [] } catch { return [] }
}
