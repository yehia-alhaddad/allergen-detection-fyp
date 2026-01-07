import { NextResponse } from 'next/server'
import { z } from 'zod'
import { rateLimit } from '@/lib/rateLimiter'
import { prisma } from '@/lib/db'
import { auth } from '@/lib/auth'
import jwt from 'jsonwebtoken'
import { cookies } from 'next/headers'
import { analyzeIngredients } from '@/lib/allergy'

const Schema = z.object({ text: z.string().min(3) })

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

async function detectWithML(text: string): Promise<{ classification: string; matches: any[]; allergen_detection?: any }> {
  const ml_api_url = process.env.ML_API_URL || 'http://localhost:8000/detect-text'

  // Try primary URL, then fallback to /detect-text if the URL points to /detect or if the first call fails/422
  const urlsToTry = [ml_api_url]
  if (ml_api_url.endsWith('/detect')) {
    urlsToTry.push(ml_api_url.replace(/\/detect$/, '/detect-text'))
  } else if (!ml_api_url.endsWith('/detect-text')) {
    urlsToTry.push(`${ml_api_url.replace(/\/$/, '')}/detect-text`)
  }

  for (const url of urlsToTry) {
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })

      if (!res.ok) {
        console.error(`ML service error ${res.status} at ${url}`)
        continue
      }

      const data = await res.json()

      // Try new format first (allergen_detection)
      if (data.success && data.allergen_detection) {
        const allergenDet = data.allergen_detection
        const totalDetected = (allergenDet.contains?.length || 0) + (allergenDet.may_contain?.length || 0)

        if (totalDetected > 0) {
          return {
            classification: 'CAUTION',
            matches: [
              ...allergenDet.contains.map((a: any) => ({ name: a.allergen })),
              ...allergenDet.may_contain.map((a: any) => ({ name: a.allergen }))
            ],
            allergen_detection: allergenDet
          }
        }
      }

      // Fallback to old format (detected_allergens)
      if (data.success && data.detected_allergens) {
        const detected = data.detected_allergens as Record<string, any[]>
        const keys = Object.keys(detected)

        if (keys.length > 0) {
          return {
            classification: 'CAUTION',
            matches: keys.map(k => ({ name: k }))
          }
        }
      }
    } catch (err) {
      console.error(`ML service error at ${url}:`, err)
      continue
    }
  }

  return { classification: 'SAFE', matches: [] }
}

// Lightweight keyword fallback for common allergens when ML or profile matching finds nothing
const COMMON_ALLERGENS = [
  'peanut','peanuts','milk','dairy','lactose','wheat','gluten','soy','soya','egg','eggs','almond','hazelnut','cashew','pistachio','walnut','pecan','sesame','fish','shellfish','shrimp','prawn','crab','lobster','mustard','celery','sulfite','sulphite','mollusc','barley','rye'
]

// Map plural/variant allergen names to canonical singular form
const ALLERGEN_NORMALIZATION: Record<string, string> = {
  'peanuts': 'peanut',
  'eggs': 'egg',
  'soya': 'soy',
  'sulphite': 'sulfite',
  'molluscs': 'mollusc'
}

function normalizeAllergen(name: string): string {
  return ALLERGEN_NORMALIZATION[name] || name
}

function keywordScan(text: string) {
  const lower = text.toLowerCase()
  const found = COMMON_ALLERGENS.filter(term => lower.includes(term))
  // Normalize to canonical form and deduplicate
  const normalized = found.map(normalizeAllergen)
  const unique = Array.from(new Set(normalized))
  if (unique.length === 0) return { classification: 'SAFE', matches: [] as any[] }
  return {
    classification: 'CAUTION',
    matches: unique.map(name => ({ name })),
    allergen_detection: {
      contains: unique.map(name => ({ allergen: name, evidence: 'keyword', confidence: 0.5 })),
      may_contain: [],
      not_detected: []
    }
  }
}

export async function POST(req: Request) {
  const ip = (req.headers.get('x-forwarded-for') || 'local').split(',')[0].trim()
  if (!rateLimit(`ingredients:${ip}`)) return NextResponse.json({ error: 'Rate limited' }, { status: 429 })

  const session = await auth()
  let user = null
  const email = session?.user?.email || getUserEmailFromCookie()
  if (email) {
    user = await prisma.user.findUnique({ where: { email } })
  }

  const body = await req.json().catch(() => null)
  const parsed = Schema.safeParse(body)
  if (!parsed.success) return NextResponse.json({ error: 'Invalid input' }, { status: 400 })

  let result: { classification: string; matches: any[]; allergen_detection?: any } = { classification: 'SAFE', matches: [] }
  let allergenDetection: any = null

  // Always try ML first for broad coverage
  const mlResult = await detectWithML(parsed.data.text)

  if (user) {
    const allergens = await prisma.userAllergen.findMany({ where: { userId: user.id } })
    const profile = allergens.map(a => ({
      name: a.name,
      synonyms: Array.isArray((a as any).synonyms)
        ? (a as any).synonyms as string[]
        : (typeof (a as any).synonyms === 'string' ? safeParseArray((a as any).synonyms as unknown as string) : [])
    }))

    const personalized = analyzeIngredients(parsed.data.text, profile)

    // Merge ML matches + personalized matches
    const combinedMatches = mergeMatches(mlResult.matches || [], personalized.matches || [])

    // Build allergen detection payload, favoring ML structure when available
    allergenDetection = mlResult.allergen_detection ?? buildDetectionFromMatches(combinedMatches, profile)

    // Classification rules: ingredient hit => UNSAFE; any match => CAUTION; else SAFE
    const hasIngredientHit = personalized.matches.some(m => m.source === 'ingredients')
    const hasAnyMatch = combinedMatches.length > 0 || !!allergenDetection
    const classification = hasIngredientHit ? 'UNSAFE' : (hasAnyMatch ? 'CAUTION' : 'SAFE')

    result = {
      classification,
      matches: combinedMatches,
      allergen_detection: allergenDetection,
    }
  } else {
    // Anonymous users: use ML, and if empty fall back to keyword scan
    result = mlResult
    allergenDetection = mlResult.allergen_detection ?? null
  }

  // Always run keyword scan to catch obvious terms (in case ML/auth/profile misses)
  const keywordResult = keywordScan(parsed.data.text)
  if (keywordResult.matches.length > 0) {
    result.matches = mergeMatches(result.matches || [], keywordResult.matches)
    // Upgrade classification unless already UNSAFE
    if (result.classification === 'SAFE') result.classification = keywordResult.classification
    // Update allergenDetection to include keyword matches
    if (!allergenDetection || allergenDetection.contains?.length === 0) {
      allergenDetection = keywordResult.allergen_detection
    } else {
      // Merge keyword matches into existing allergenDetection
      allergenDetection.contains = [
        ...(allergenDetection.contains || []),
        ...(keywordResult.allergen_detection?.contains || [])
      ]
    }
  }

  // If still safe but we have any matches, set to CAUTION
  if ((result.matches?.length ?? 0) > 0 && result.classification === 'SAFE') {
    result.classification = 'CAUTION'
  }

  // Rebuild allergenDetection from final matches if still empty
  if (!allergenDetection || (!allergenDetection.contains && !allergenDetection.may_contain)) {
    allergenDetection = {
      contains: (result.matches || []).map(m => ({ allergen: m.name, evidence: m.source || 'detection', confidence: 0.7 })),
      may_contain: [],
      not_detected: []
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
    matches: result.matches,
    allergen_detection: allergenDetection ?? result.allergen_detection
  })
}

function mergeMatches(...lists: any[][]) {
  const merged: Record<string, any> = {}
  for (const list of lists) {
    for (const m of list || []) {
      const name = (m?.name || m?.allergen || m?.label || '').toString().toLowerCase()
      if (!name) continue
      merged[name] = merged[name] || m
    }
  }
  return Object.values(merged)
}

function buildDetectionFromMatches(matches: any[], profile: { name: string }[]) {
  const contains = matches.map(m => ({ allergen: m.name || m.allergen || m.label, evidence: m.snippet ?? m.source, confidence: m.confidence ?? 0.8 }))
  const may_contain: any[] = []
  const not_detected = (profile || [])
    .filter(p => !matches.some(m => (m.name || m.allergen || m.label || '').toLowerCase() === p.name.toLowerCase()))
    .map(p => ({ allergen: p.name, evidence: null, confidence: 0.1 }))
  return { contains, may_contain, not_detected }
}

function safeParseArray(s: string): string[] {
  try { return JSON.parse(s || '[]') ?? [] } catch { return [] }
}
