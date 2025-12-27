export type MatchSource = 'ingredients' | 'may_contain' | 'ocr' | 'barcode'
export type Classification = 'SAFE' | 'CAUTION' | 'UNSAFE'

export interface UserAllergenProfile {
  name: string
  synonyms?: string[]
  severity?: string
}

export interface MatchResult {
  name: string
  source: MatchSource
  snippet?: string
  confidence?: number
}

const MAY_CONTAIN_PATTERNS = [
  /may\s+contain/i,
  /may\s+contain\s+traces\s+of/i,
  /produced\s+in\s+a\s+facility\s+that\s+also\s+processes/i,
]

function normalize(text: string) {
  return text.toLowerCase()
}

function wordBoundaryRegex(term: string) {
  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return new RegExp(`(^|[^a-z0-9])(${escaped})([^a-z0-9]|$)`, 'i')
}

export function analyzeIngredients(raw: string, profile: UserAllergenProfile[]): { matches: MatchResult[]; classification: Classification } {
  const text = normalize(raw)
  const matches: MatchResult[] = []

  // Detect may contain context
  const mayContain = MAY_CONTAIN_PATTERNS.some(p => p.test(text))

  for (const allergen of profile) {
    const terms = [allergen.name, ...(allergen.synonyms || [])]
    let directMatch = false
    let snippet: string | undefined

    for (const term of terms) {
      const rx = wordBoundaryRegex(term.toLowerCase())
      const m = text.match(rx)
      if (m) {
        directMatch = true
        snippet = text.substring(Math.max(0, m.index! - 30), Math.min(text.length, (m.index! + m[0].length) + 30))
        break
      }
    }

    if (directMatch) {
      matches.push({ name: allergen.name, source: mayContain ? 'may_contain' : 'ingredients', snippet, confidence: mayContain ? 0.6 : 0.9 })
    }
  }

  let classification: Classification = 'SAFE'
  if (matches.some(m => m.source === 'ingredients')) classification = 'UNSAFE'
  else if (matches.length > 0 || mayContain) classification = 'CAUTION'

  return { matches, classification }
}
