'use client'

import { useState } from 'react'
import { AlertCircle, ArrowLeft, RotateCcw } from 'lucide-react'
import Link from 'next/link'
import CameraCapture from '@/components/scan/CameraCapture'
import EnhancedScanResult from '@/components/scan/EnhancedScanResult'

export default function ScanCameraPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<any>(null)

  const handleCapture = async (base64: string) => {
    setLoading(true)
    setError('')

    try {
      const bytes = Buffer.from(base64, 'base64')
      const blob = new Blob([bytes], { type: 'image/jpeg' })
      const formData = new FormData()
      formData.append('file', blob, 'capture.jpg')

      const res = await fetch('/api/infer/image', {
        method: 'POST',
        body: formData
      })

      const data = await res.json()

      if (!res.ok) {
        const msg = typeof data?.error === 'string' ? data.error : 'Scan failed'
        setError(msg)
        return
      }

      // Transform API response to match EnhancedScanResult format
      const allergenDetection = data.allergen_detection || {}
      const transformedResult = {
        contains: (allergenDetection.contains || []).map((a: any) => ({
          allergen: a.allergen,
          evidence: a.evidence || a.matched_keyword || a.keyword || '',
          keyword: a.keyword || a.matched_keyword || '',
          trigger_phrase: a.evidence || a.matched_keyword || a.keyword || '',
          source_section: 'ingredients' as const,
          confidence: a.confidence || 0.9
        })),
        may_contain: (allergenDetection.may_contain || []).map((a: any) => ({
          allergen: a.allergen,
          evidence: a.evidence || a.matched_keyword || a.keyword || '',
          keyword: a.keyword || a.matched_keyword || '',
          trigger_phrase: a.evidence || a.matched_keyword || a.keyword || '',
          source_section: 'warning_statement' as const,
          confidence: a.confidence || 0.9
        })),
        not_detected: (allergenDetection.not_detected || []).map((a: any) => ({
          allergen: typeof a === 'string' ? a : a.name,
          reason: 'No matching terms found in ingredients or warning statements',
          confidence: 0.1
        }))
      }
      setResult(transformedResult)
    } catch (err) {
      setError('An error occurred while processing the image')
      console.error('Scan error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (result) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-12">
        <Link href="/dashboard" className="inline-flex items-center gap-2 text-zinc-600 hover:text-zinc-900 mb-6 font-medium">
          <ArrowLeft size={20} />
          Back to Dashboard
        </Link>
        <EnhancedScanResult result={result} />
        <div className="mt-6 grid md:grid-cols-2 gap-4">
          <button
            onClick={() => {
              setResult(null)
              setError('')
            }}
            className="px-6 py-3 bg-zinc-200 text-zinc-900 font-semibold rounded-lg hover:bg-zinc-300 transition flex items-center justify-center gap-2"
          >
            <RotateCcw size={18} /> Scan Another
          </button>
          <Link href="/dashboard" className="px-6 py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition text-center">
            Back to Dashboard
          </Link>
        </div>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-12">
      <Link href="/dashboard" className="inline-flex items-center gap-2 text-zinc-600 hover:text-zinc-900 mb-6 font-medium">
        <ArrowLeft size={20} />
        Back to Dashboard
      </Link>
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-zinc-900 mb-2">📱 Camera Scan</h1>
        <p className="text-zinc-600 mb-8">Point your camera at the product label and tap Capture to scan for allergens</p>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center gap-2">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        <div className="mb-8">
          <CameraCapture onCapture={handleCapture} />
        </div>

        {loading && (
          <div className="text-center py-6">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mb-2"></div>
            <p className="text-zinc-600">Analyzing image...</p>
          </div>
        )}
      </div>
    </main>
  )
}
