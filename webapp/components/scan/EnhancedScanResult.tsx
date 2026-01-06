'use client'

import { useEffect, useState } from 'react'
import Image from 'next/image'

// Enhanced interface supporting Gemini AI data
interface Allergen {
  allergen: string
  evidence: string  // Original evidence
  cleaned_trigger_phrase?: string  // AI-cleaned version
  keyword?: string
  confidence: number
  category?: 'CONTAINS' | 'MAY_CONTAIN'
  health_recommendation?: {
    severity: 'low' | 'moderate' | 'high' | 'critical'
    symptoms: string[]
    immediate_actions: string[]
    when_to_seek_help: string
    alternatives: string[]
    summary: string
  }
  subtypes?: string[]
  trigger_phrase?: string
  source_section?: 'ingredients' | 'warning_statement'
}

interface AllergenDetectionResult {
  contains: Allergen[]
  may_contain: Allergen[]
  not_detected: string[] | Array<{ allergen: string; reason?: string; confidence?: number }>
  image_src?: string
  summary?: {
    contains_count: number
    may_contain_count: number
    total_detected: number
  }
}

interface ScanResultProps {
  result: AllergenDetectionResult
  imageFile?: File
}

interface UserAllergen {
  id?: string
  name: string
  severity?: string
  synonyms?: string[]
}

const ALL_ALLERGENS = [
  'PEANUT',
  'TREE_NUT',
  'MILK',
  'EGG',
  'GLUTEN',
  'SOY',
  'FISH',
  'SHELLFISH',
  'SESAME',
  'MUSTARD',
  'CELERY',
  'SULPHITES',
  'LUPIN'
]

export default function EnhancedScanResult({ result, imageFile }: ScanResultProps) {
  const [showImageModal, setShowImageModal] = useState(false)
  const [imageSource, setImageSource] = useState<string>('')
  const [expandedHealthRecs, setExpandedHealthRecs] = useState<Set<string>>(new Set())
  const [userAllergens, setUserAllergens] = useState<UserAllergen[]>([])
  const [isAuthed, setIsAuthed] = useState<boolean>(true)

  // Fetch user allergens for personalization (if logged in)
  useEffect(() => {
    const fetchAllergens = async () => {
      try {
        const res = await fetch('/api/allergens/list')
        if (res.status === 401) {
          setIsAuthed(false)
          return
        }
        if (!res.ok) return
        const data = await res.json()
        setUserAllergens(data.allergens || [])
      } catch (err) {
        setIsAuthed(false)
      }
    }
    fetchAllergens()
  }, [])

  const getImageSource = async () => {
    if (result.image_src) {
      setImageSource(result.image_src)
    } else if (imageFile) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setImageSource(e.target?.result as string)
      }
      reader.readAsDataURL(imageFile)
    }
  }

  const handleImageClick = () => {
    getImageSource()
    setShowImageModal(true)
  }

  const toggleHealthRec = (allergen: string) => {
    const newSet = new Set(expandedHealthRecs)
    if (newSet.has(allergen)) {
      newSet.delete(allergen)
    } else {
      newSet.add(allergen)
    }
    setExpandedHealthRecs(newSet)
  }

  const getSafetyLevel = (): { label: string; color: string; bgColor: string } => {
    if (result.contains.length > 0) {
      return { label: 'UNSAFE', color: 'text-red-600', bgColor: 'bg-red-50 border-red-200' }
    }
    if (result.may_contain.length > 0) {
      return { label: 'CAUTION', color: 'text-amber-600', bgColor: 'bg-amber-50 border-amber-200' }
    }
    return { label: 'SAFE', color: 'text-green-600', bgColor: 'bg-green-50 border-green-200' }
  }

  const getSeverityColor = (severity?: string): { text: string; bg: string } => {
    switch (severity) {
      case 'critical':
        return { text: 'text-red-700', bg: 'bg-red-100' }
      case 'high':
        return { text: 'text-orange-700', bg: 'bg-orange-100' }
      case 'moderate':
        return { text: 'text-amber-700', bg: 'bg-amber-100' }
      case 'low':
        return { text: 'text-yellow-700', bg: 'bg-yellow-100' }
      default:
        return { text: 'text-gray-700', bg: 'bg-gray-100' }
    }
  }

  const detectedAllergens = result.contains.concat(result.may_contain)

  // Personalization logic
  const normalize = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, '').trim()

  const levenshtein = (a: string, b: string) => {
    const m = a.length
    const n = b.length
    if (m === 0) return n
    if (n === 0) return m
    const dp = Array.from({ length: m + 1 }, (_, i) => Array(n + 1).fill(0))
    for (let i = 0; i <= m; i++) dp[i][0] = i
    for (let j = 0; j <= n; j++) dp[0][j] = j
    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1
        dp[i][j] = Math.min(
          dp[i - 1][j] + 1,
          dp[i][j - 1] + 1,
          dp[i - 1][j - 1] + cost
        )
      }
    }
    return dp[m][n]
  }

  const isSimilar = (userTerm: string, detected: string) => {
    const u = normalize(userTerm)
    const d = normalize(detected)
    if (!u || !d) return false
    if (u === d) return true
    if (u.length > 2 && d.includes(u)) return true
    if (d.length > 2 && u.includes(d)) return true
    return levenshtein(u, d) <= 2
  }

  const userTerms = userAllergens.flatMap((a) => {
    const list: string[] = []
    if (a.name) list.push(a.name)
    if (Array.isArray(a.synonyms)) list.push(...a.synonyms)
    return list
  }).filter(Boolean)

  const personalizedMatches = detectedAllergens.filter((a) =>
    userTerms.some((term) => isSimilar(term, a.allergen))
  )
  const otherDetected = detectedAllergens.filter((a) =>
    !userTerms.some((term) => isSimilar(term, a.allergen))
  )

  const hasUserProfile = isAuthed && userAllergens.length > 0
  const hasPersonalizedHit = personalizedMatches.length > 0
  const hasAnyDetected = detectedAllergens.length > 0

  // Personalized safety card prioritizes the user's saved allergens and downgrades warnings
  const personalizedSafety = hasUserProfile
    ? hasPersonalizedHit
      ? { label: 'UNSAFE FOR YOU', color: 'text-red-700', bgColor: 'bg-red-50 border-red-200' }
      : hasAnyDetected
        ? { label: 'SAFE FOR YOU', color: 'text-amber-700', bgColor: 'bg-amber-50 border-amber-200' }
        : { label: 'SAFE FOR YOU', color: 'text-green-700', bgColor: 'bg-green-50 border-green-200' }
    : null

  const renderAllergenCard = (allergen: Allergen, isMayContain: boolean = false) => {
    const severity = allergen.health_recommendation?.severity
    const severityColor = getSeverityColor(severity)
    const isExpanded = expandedHealthRecs.has(allergen.allergen)

    return (
      <div
        key={allergen.allergen}
        className={`rounded-lg border ${isMayContain ? 'border-amber-100 bg-white' : 'border-red-100 bg-white'} p-4 space-y-3`}
      >
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h4 className={`font-bold ${isMayContain ? 'text-amber-700' : 'text-red-700'}`}>
              {allergen.allergen}
            </h4>
            {allergen.health_recommendation && (
              <div className={`text-xs font-semibold mt-1 px-2 py-1 rounded ${severityColor.bg} ${severityColor.text} w-fit`}>
                {severity?.toUpperCase()} RISK
              </div>
            )}
          </div>
          <div className="text-right">
            <div className="text-sm font-semibold text-gray-700">Confidence</div>
            <div className={`text-lg font-bold ${isMayContain ? 'text-amber-600' : 'text-red-600'}`}>
              {(allergen.confidence * 100).toFixed(0)}%
            </div>
          </div>
        </div>

        {/* Evidence - Direct OCR text */}
        <div className="space-y-2 border-t pt-3">
          <div className="text-sm">
            <span className="font-semibold text-gray-700">Evidence: </span>
            <span className="italic text-gray-800 bg-gray-50 px-2 py-1 rounded text-xs">
              "{allergen.evidence}"
            </span>
          </div>

          {allergen.keyword && (
            <div className="text-sm">
              <span className="font-semibold text-gray-700">Keyword: </span>
              <span className="inline-block px-2 py-1 rounded bg-blue-100 text-blue-700 text-xs">
                {allergen.keyword}
              </span>
            </div>
          )}
        </div>

        {/* Health Recommendation Button */}
        {allergen.health_recommendation && (
          <button
            onClick={() => toggleHealthRec(allergen.allergen)}
            className={`w-full text-left px-4 py-2 rounded-lg font-semibold transition-colors ${
              isExpanded
                ? 'bg-blue-600 text-white'
                : 'bg-blue-50 text-blue-700 hover:bg-blue-100'
            }`}
          >
            {isExpanded ? '▼' : '▶'} Health Recommendation & First Aid
          </button>
        )}

        {/* Expanded Health Recommendation */}
        {isExpanded && allergen.health_recommendation && (
          <div className="mt-4 space-y-4 p-4 rounded-lg bg-gradient-to-b from-blue-50 to-white border border-blue-200">
            {/* Summary */}
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-1">Summary:</p>
              <p className="text-sm text-gray-800">{allergen.health_recommendation.summary}</p>
            </div>

            {/* Symptoms */}
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-2">Symptoms to Watch For:</p>
              <ul className="space-y-1">
                {allergen.health_recommendation.symptoms.map((symptom, i) => (
                  <li key={i} className="text-sm text-gray-700 ml-4 list-disc">
                    {symptom}
                  </li>
                ))}
              </ul>
            </div>

            {/* Immediate Actions */}
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-2">Immediate Actions if Exposed:</p>
              <ol className="space-y-1">
                {allergen.health_recommendation.immediate_actions.map((action, i) => (
                  <li key={i} className="text-sm text-gray-700 ml-4 list-decimal">
                    {action}
                  </li>
                ))}
              </ol>
            </div>

            {/* When to Seek Help */}
            <div className="p-3 rounded-lg bg-red-50 border border-red-200">
              <p className="text-sm font-semibold text-red-700 mb-1">When to Seek Medical Help:</p>
              <p className="text-sm text-red-800">{allergen.health_recommendation.when_to_seek_help}</p>
            </div>

            {/* Alternatives */}
            {allergen.health_recommendation.alternatives.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-gray-700 mb-2">Safe Alternatives:</p>
                <ul className="space-y-1">
                  {allergen.health_recommendation.alternatives.map((alt, i) => (
                    <li key={i} className="text-sm text-gray-700 ml-4 list-disc">
                      {alt}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  // Safety badge
  const safety = personalizedSafety || getSafetyLevel()

  return (
    <div className="space-y-6">
      {/* Scanned Label Image (moved to top) */}
      {(imageFile || result.image_src) && (
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h3 className="text-lg font-bold text-gray-700 mb-4">Scanned Label Preview</h3>
          <div className="relative w-full bg-gray-100 rounded-lg overflow-hidden">
            <div
              className="relative w-full aspect-square cursor-pointer hover:opacity-80 transition-opacity"
              onClick={handleImageClick}
            >
              {imageFile ? (
                <img
                  src={URL.createObjectURL(imageFile)}
                  alt="Scanned product label"
                  className="w-full h-full object-contain p-4"
                />
              ) : result.image_src ? (
                <img
                  src={result.image_src}
                  alt="Scanned product label"
                  className="w-full h-full object-contain p-4"
                />
              ) : null}
            </div>
            <p className="text-xs text-center text-gray-500 p-2">
              Click to zoom / enlarge image for detailed verification
            </p>
          </div>
        </div>
      )}

      {/* Safety Badge - Only for non-authenticated users */}
      {!hasUserProfile && (
        <div className={`rounded-lg border p-6 flex flex-col gap-2 ${safety.bgColor}`}>
          <div className="flex items-center justify-between">
            <div>
              <h2 className={`text-2xl font-bold ${safety.color}`}>{safety.label}</h2>
              <p className="text-sm text-gray-700 mt-1">
                {safety.label === 'UNSAFE' && 'This product contains detected allergens.'}
                {safety.label === 'CAUTION' && 'This product may contain traces of allergens.'}
                {safety.label === 'SAFE' && 'No detected allergens found on this label.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Personalized Safety (for signed-in users) */}
      {isAuthed ? (
        <div className={`rounded-lg border p-6 space-y-3 shadow-sm ${
          personalizedMatches.length > 0
            ? 'border-red-200 bg-red-50'
            : hasAnyDetected
            ? 'border-amber-200 bg-amber-50'
            : 'border-green-200 bg-green-50'
        }`}>
          <div className="flex items-center justify-between">
            <h3 className={`text-lg font-bold ${
              personalizedMatches.length > 0
                ? 'text-red-900'
                : hasAnyDetected
                ? 'text-amber-900'
                : 'text-green-900'
            }`}>
              Your Safety Status
            </h3>
            <span className="text-xs px-3 py-1 rounded-full bg-white border">
              {userAllergens.length} allergens saved
            </span>
          </div>

          {userAllergens.length === 0 ? (
            <p className="text-sm text-gray-800">Add your allergens in Profile to get personalized risk flags.</p>
          ) : personalizedMatches.length > 0 ? (
            <div className="space-y-2">
              <p className="text-sm font-semibold text-red-700">
                ⚠️ Unsafe for you: {personalizedMatches.map((a) => a.allergen).join(', ')}
              </p>
              <p className="text-xs text-red-700">These match your saved allergens. We recommend avoiding this product.</p>
            </div>
          ) : (
            <div className="space-y-2">
              <p className={`text-sm font-semibold ${
                hasAnyDetected ? 'text-amber-700' : 'text-green-700'
              }`}>
                ✓ Safe for you: none of your saved allergens were detected.
              </p>
              {otherDetected.length > 0 && (
                <p className="text-xs text-amber-700">
                  Note: Other allergens are present on the label ({otherDetected.map((a) => a.allergen).join(', ')}). Review details below if interested.
                </p>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm text-gray-700">
          Sign in and add your allergens to see personalized safety warnings.
        </div>
      )}

      {/* SECTION A: CONTAINS (Confirmed Allergens) - Only show if allergens exist */}
      {result.contains.length > 0 && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-6">
          <h3 className="text-lg font-bold text-red-700 mb-4">
            CONTAINS - Confirmed Allergens ({result.contains.length})
          </h3>
          <div className="space-y-4">
            {result.contains.map((allergen, idx) => (
              renderAllergenCard(allergen, false)
            ))}
          </div>
        </div>
      )}

      {/* SECTION B: MAY CONTAIN / TRACES - Only show if allergens exist */}
      {result.may_contain.length > 0 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-6">
          <h3 className="text-lg font-bold text-amber-700 mb-4">
            MAY CONTAIN / TRACES - Cross-Contamination Risk ({result.may_contain.length})
          </h3>
          <div className="space-y-4">
            {result.may_contain.map((allergen, idx) => (
              <div
                key={idx}
                className="rounded-lg border border-amber-100 bg-white p-4 space-y-3"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-bold text-amber-700">{allergen.allergen}</h4>
                    {allergen.subtypes && allergen.subtypes.length > 0 && (
                      <p className="text-sm text-gray-600 mt-1">
                        Subtypes: {allergen.subtypes.join(', ')}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-gray-700">
                      Confidence
                    </div>
                    <div className="text-lg font-bold text-amber-600">
                      {(allergen.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>

                <div className="space-y-2 border-t pt-3">
                  <div className="text-sm">
                    <span className="font-semibold text-gray-700">Trigger Phrase: </span>
                    <span className="italic text-gray-800 bg-yellow-100 px-2 py-1 rounded">
                      "{allergen.trigger_phrase}"
                    </span>
                  </div>
                  <div className="text-sm">
                    <span className="font-semibold text-gray-700">Source: </span>
                    <span className="inline-block px-2 py-1 rounded bg-gray-200 text-gray-700">
                      {allergen.source_section === 'ingredients' ? 'Ingredients List' : 'Warning Statement'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Image Modal / Lightbox */}
      {showImageModal && imageSource && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75 p-4"
          onClick={() => setShowImageModal(false)}
        >
          <div
            className="relative max-w-2xl w-full bg-white rounded-lg overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setShowImageModal(false)}
              className="absolute top-2 right-2 bg-red-600 text-white rounded-full p-2 hover:bg-red-700 z-10"
            >
              ✕
            </button>
            <img
              src={imageSource}
              alt="Enlarged scanned label"
              className="w-full h-auto"
            />
            <p className="text-center text-gray-600 text-sm p-4">
              Verify allergen information against this scanned label
            </p>
          </div>
        </div>
      )}

      {/* Footer Note */}
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
        <p className="text-xs text-gray-600">
          <strong>Disclaimer:</strong> This tool provides automated allergen detection based on label text analysis.
          Always verify allergen information directly on the product label and consult medical professionals if needed.
          Not responsible for missed allergens or misidentification.
        </p>
      </div>
    </div>
  )
}
