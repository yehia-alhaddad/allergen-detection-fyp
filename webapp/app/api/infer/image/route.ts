import { NextResponse } from 'next/server'
import { rateLimit } from '@/lib/rateLimiter'
import { prisma } from '@/lib/db'
import { auth } from '@/lib/auth'
import jwt from 'jsonwebtoken'
import { cookies } from 'next/headers'
import { run_model_from_service, run_model_stub } from '@/lib/inference'
import { analyzeIngredients } from '@/lib/allergy'

export const runtime = 'nodejs'

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
  if (!rateLimit(`image:${ip}`)) return NextResponse.json({ error: 'Rate limited' }, { status: 429 })

  const session = await auth()
  let user = null
  const email = session?.user?.email || getUserEmailFromCookie()
  if (email) {
    user = await prisma.user.findUnique({ where: { email } })
  }

  const form = await req.formData().catch(() => null)
  const file = form?.get('file') as File | null
  if (!file) return NextResponse.json({ error: 'Missing image file' }, { status: 400 })

  const buffer = Buffer.from(await file.arrayBuffer())
  const base64 = buffer.toString('base64')

  let inference
  try {
    inference = await run_model_from_service(base64)
    if (inference && inference.serviceAvailable === false) {
      return NextResponse.json({ error: 'ML service unavailable. Please start the ML API.' }, { status: 503 })
    }
    if (inference && inference.error && (inference.serviceAvailable ?? true)) {
      // Service reachable but returned error - pass through the specific error message
      return NextResponse.json({ error: inference.error }, { status: 400 })
    }
  } catch (e) {
    console.error('Inference route error:', e)
    return NextResponse.json({ error: 'Inference failed. Check ML API.' }, { status: 500 })
  }

  // Prefer cleaned text from API for downstream matching
  const pseudoText = (inference.cleanedText || inference.rawText || inference.labels.join(', ')).toString()
  let result: { classification: 'SAFE' | 'CAUTION' | 'UNSAFE', matches: any[] } = { classification: 'SAFE', matches: [] }
  
  if (user) {
    // Logged-in users: personalized analysis
    const allergens = await prisma.userAllergen.findMany({ where: { userId: user.id } })
    const profile = allergens.map((a: any) => ({
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

  // Fallback: if personalized analysis found nothing but the model detected allergens, surface them for history display
  if (result.matches.length === 0 && inference?.detectedAllergens) {
    const detectedKeys = Object.keys(inference.detectedAllergens || {})
    if (detectedKeys.length > 0) {
      result = {
        classification: result.classification === 'SAFE' ? 'CAUTION' : result.classification,
        matches: detectedKeys.map(k => ({ name: k })),
      }
    }
  }

  // Save scan history (only for logged-in users)
  if (user) {
    const productName = file?.name?.trim() ? file.name : `Product (${new Date().toISOString()})`

    await prisma.scanHistory.create({
      data: {
        userId: user.id,
        type: 'IMAGE',
        productName,
        classification: result.classification,
        matchedAllergens: JSON.stringify(result.matches),
        inputMetadata: JSON.stringify({ labels: inference.labels, source: 'ml_inference', fileName: file?.name }),
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
    allergen_detection: inference.allergenDetection,
  })
}

function safeParseArray(s: string): string[] {
  try { return JSON.parse(s || '[]') ?? [] } catch { return [] }
}
