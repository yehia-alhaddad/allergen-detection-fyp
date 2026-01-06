"use client"
import { useState } from 'react'
import IngredientInput from '@/components/scan/IngredientInput'
import EnhancedScanResult from '@/components/scan/EnhancedScanResult'

export default function ScanTextPage() {
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const analyze = async (text: string) => {
    setLoading(true)
    const res = await fetch('/api/ingredients/check', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) })
    const data = await res.json()
    
    // Transform API response to match EnhancedScanResult format
    if (data.allergen_detection) {
      const allergenDetection = data.allergen_detection
      const transformedResult = {
        contains: (allergenDetection.contains || []).map((a: any) => ({
          allergen: a.allergen,
          trigger_phrase: a.evidence || a.keyword || '',
          source_section: 'ingredients' as const,
          confidence: a.confidence || 0.9
        })),
        may_contain: (allergenDetection.may_contain || []).map((a: any) => ({
          allergen: a.allergen,
          trigger_phrase: a.evidence || a.keyword || '',
          source_section: 'warning_statement' as const,
          confidence: a.confidence || 0.9
        })),
        not_detected: (allergenDetection.not_detected || []).map((a: any) => ({
          allergen: typeof a === 'string' ? a : a.name,
          reason: 'No allergen mention found',
          confidence: 0.1
        }))
      }
      setResult(transformedResult)
    } else {
      setResult(data)
    }
    
    setLoading(false)
  }

  return (
    <main className="space-y-6">
      <h1 className="text-2xl font-semibold">Paste Ingredient Text</h1>
      <IngredientInput onSubmit={analyze} />
      {loading && <p>Analyzing...</p>}
      {result && <EnhancedScanResult result={result} />}
    </main>
  )
}
