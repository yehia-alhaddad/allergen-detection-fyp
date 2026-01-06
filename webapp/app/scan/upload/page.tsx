"use client"
import { useState } from 'react'
import EnhancedScanResult from '@/components/scan/EnhancedScanResult'

export default function ScanUploadPage() {
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploadedFile(file)
    setError(null)
    setLoading(true)

    const form = new FormData()
    form.append('file', file)

    try {
      const res = await fetch('/api/infer/image', { method: 'POST', body: form })
      const data = await res.json()

      if (!res.ok) {
        setError(data.error || 'Failed to analyze image')
        setLoading(false)
        return
      }

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
          reason: 'No matching terms found in ingredients or warning statements',
          confidence: 0.1
        }))
      }

      setResult(transformedResult)
    } catch (err) {
      setError('Network error or ML service unavailable')
      console.error('Upload error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="space-y-6 max-w-4xl mx-auto">
      <div className="rounded-2xl bg-white border border-emerald-100 p-8 shadow-lg">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Scan Product Label</h1>
        <p className="text-gray-600 mb-6">
          Upload a photo of a food product label to detect allergens
        </p>

        <div className="border-2 border-dashed border-emerald-200 rounded-xl p-8 text-center hover:border-emerald-500 hover:bg-emerald-50 transition-colors">
          <label className="cursor-pointer">
            <div className="space-y-3">
              <div className="text-4xl">📸</div>
              <div>
                <span className="font-semibold text-emerald-700 hover:text-emerald-800">
                  Click to upload
                </span>
                <span className="text-gray-600"> or drag and drop</span>
              </div>
              <p className="text-sm text-gray-500">
                PNG, JPG, GIF up to 10MB
              </p>
            </div>
            <input
              type="file"
              accept="image/*"
              onChange={onUpload}
              disabled={loading}
              className="hidden"
              aria-label="Upload product label image"
            />
          </label>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-red-700 font-semibold">Error</p>
          <p className="text-red-600 text-sm mt-1">{error}</p>
        </div>
      )}

      {loading && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-6">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-600"></div>
            <p className="text-emerald-700 font-semibold">Analyzing product label...</p>
          </div>
          <p className="text-sm text-emerald-700 mt-2">
            This may take 5-10 seconds as we extract text and detect allergens
          </p>
        </div>
      )}

      {result && (
        <EnhancedScanResult 
          result={result}
          imageFile={uploadedFile || undefined}
        />
      )}
    </main>
  )
}
