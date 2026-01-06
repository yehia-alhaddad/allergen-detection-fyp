"use client"
import { useState } from 'react'
import CameraCapture from '@/components/scan/CameraCapture'
import EnhancedScanResult from '@/components/scan/EnhancedScanResult'

export default function ScanCameraPage() {
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const onCapture = async (base64: string) => {
    setLoading(true)
    const bytes = Buffer.from(base64, 'base64')
    const blob = new Blob([bytes], { type: 'image/jpeg' })
    const formData = new FormData()
    formData.append('file', blob, 'capture.jpg')
    
    const res = await fetch('/api/infer/image', { 
      method: 'POST', 
      body: formData 
    })
    const data = await res.json()
    
    if (res.ok) {
      // Transform API response to match EnhancedScanResult format
      const allergenDetection = data.allergen_detection || {}
      const transformedResult = {
        contains: (allergenDetection.contains || []).map((a: any) => ({
          allergen: a.allergen,
          trigger_phrase: a.evidence || a.matched_keyword || '',
          source_section: 'ingredients' as const,
          confidence: a.confidence || 0.9
        })),
        may_contain: (allergenDetection.may_contain || []).map((a: any) => ({
          allergen: a.allergen,
          trigger_phrase: a.evidence || a.matched_keyword || '',
          source_section: 'warning_statement' as const,
          confidence: a.confidence || 0.9
        })),
        not_detected: (allergenDetection.not_detected || []).map((a: any) => ({
          allergen: typeof a === 'string' ? a : a.name,
          reason: 'No matching terms found',
          confidence: 0.1
        }))
      }
      setResult(transformedResult)
    }
    setLoading(false)
  }

  return (
    <main className="space-y-6">
      <h1 className="text-2xl font-semibold">Use Camera</h1>
      <CameraCapture onCapture={onCapture} />
      {loading && <p>Analyzing...</p>}
      {result && <EnhancedScanResult result={result} />}
    </main>
  )
}
