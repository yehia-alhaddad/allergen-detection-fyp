import { NextResponse } from 'next/server'
import { rateLimit } from '@/lib/rateLimiter'
import { prisma } from '@/lib/db'
import { auth } from '@/lib/auth'
import { run_model_from_service, run_model_stub } from '@/lib/inference'
import { analyzeIngredients } from '@/lib/allergy'

export async function POST(req: Request) {
  const ip = (req.headers.get('x-forwarded-for') || 'local').split(',')[0].trim()
  if (!rateLimit(`capture:${ip}`)) return NextResponse.json({ error: 'Rate limited' }, { status: 429 })

  const session = await auth()
  if (!session?.user?.email) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  const user = await prisma.user.findUnique({ where: { email: session.user.email } })
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const body = await req.json().catch(() => null)
  const base64 = body?.image as string | undefined
  if (!base64) return NextResponse.json({ error: 'Missing image' }, { status: 400 })

  let inference
  try {
    inference = await run_model_from_service(base64)
  } catch {
    inference = await run_model_stub(base64)
  }

  const pseudoText = inference.labels.join(', ')
  const allergens = await prisma.userAllergen.findMany({ where: { userId: user.id } })
  const profile = allergens.map(a => ({
    name: a.name,
    synonyms: Array.isArray((a as any).synonyms)
      ? (a as any).synonyms as string[]
      : (typeof (a as any).synonyms === 'string' ? safeParseArray((a as any).synonyms as unknown as string) : [])
  }))
  const result = analyzeIngredients(pseudoText, profile)

  // Save scan history
  await prisma.scanHistory.create({
    data: {
      userId: user.id,
      type: 'CAMERA',
      productName: `Product (${new Date().toISOString()})`,
      classification: result.classification,
      matchedAllergens: JSON.stringify(result.matches),
      inputMetadata: JSON.stringify({ labels: inference.labels, source: 'ml_inference' }),
      storeRawImage: false
    }
  })

  return NextResponse.json({
    classification: result.classification,
    matches: result.matches,
    labels: inference.labels,
  })
}

function safeParseArray(s: string): string[] {
  try { return JSON.parse(s || '[]') ?? [] } catch { return [] }
}
