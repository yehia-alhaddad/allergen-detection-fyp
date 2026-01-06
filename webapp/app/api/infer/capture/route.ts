import { NextResponse } from 'next/server'
import { rateLimit } from '@/lib/rateLimiter'
import { prisma } from '@/lib/db'
import { auth } from '@/lib/auth'
import jwt from 'jsonwebtoken'
import { cookies } from 'next/headers'
import { run_model_from_service, run_model_stub } from '@/lib/inference'
import { analyzeIngredients } from '@/lib/allergy'

function getUserEmailFromCookie() {
  const cookieStore = cookies()
  const token = cookieStore.get('next-auth.session-token')?.value
  if (!token) return null
  const secret = process.env.NEXTAUTH_SECRET || 'dev-secret'
  try {
    const decoded = jwt.verify(token, secret) as any
    return decoded?.email || null
  } catch {
    return null
  }
}

export async function POST(req: Request) {
  const ip = (req.headers.get('x-forwarded-for') || 'local').split(',')[0].trim()
  if (!rateLimit(`capture:${ip}`)) return NextResponse.json({ error: 'Rate limited' }, { status: 429 })

  const session = await auth()
  const email = session?.user?.email || getUserEmailFromCookie()
  if (!email) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  const user = await prisma.user.findUnique({ where: { email } })
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
  const profile = allergens.map((a: any) => ({
    name: a.name,
    synonyms: Array.isArray(a.synonyms)
      ? a.synonyms as string[]
      : (typeof a.synonyms === 'string' ? safeParseArray(a.synonyms as string) : [])
  }))
  let result = analyzeIngredients(pseudoText, profile)

  // Fallback to model-detected allergens if personalized analysis finds nothing
  if (result.matches.length === 0 && inference?.detectedAllergens) {
    const detectedKeys = Object.keys(inference.detectedAllergens || {})
    if (detectedKeys.length > 0) {
      result = {
        classification: result.classification === 'SAFE' ? 'CAUTION' : result.classification,
        matches: detectedKeys.map(k => ({ name: k, source: 'ocr' as const })),
      }
    }
  }

  const productName = typeof body?.fileName === 'string' && body.fileName.trim().length > 0
    ? body.fileName
    : `Product (${new Date().toISOString()})`

  // Save scan history
  await prisma.scanHistory.create({
    data: {
      userId: user.id,
      type: 'CAMERA',
      productName,
      classification: result.classification,
      matchedAllergens: JSON.stringify(result.matches),
      inputMetadata: JSON.stringify({ labels: inference.labels, source: 'ml_inference', fileName: body?.fileName }),
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
