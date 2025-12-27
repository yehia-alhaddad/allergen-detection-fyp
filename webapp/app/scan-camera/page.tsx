'use client'

import { useState } from 'react'
import { AlertCircle, CheckCircle, RotateCcw } from 'lucide-react'
import Link from 'next/link'
import CameraCapture from '@/components/scan/CameraCapture'

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
        setError(data.error || 'Scan failed')
        return
      }

      setResult(data)
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
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-zinc-900 mb-8">Scan Results</h1>

          {result.classification === 'SAFE' ? (
            <div className="mb-8 p-6 bg-green-50 border-2 border-green-500 rounded-xl">
              <div className="flex items-center gap-3 mb-2">
                <CheckCircle className="text-green-600" size={28} />
                <h2 className="text-2xl font-bold text-green-700">Safe to Eat ✓</h2>
              </div>
              <p className="text-green-700">No concerning allergens were detected in this product.</p>
            </div>
          ) : (
            <div className="mb-8 p-6 bg-red-50 border-2 border-red-500 rounded-xl">
              <div className="flex items-center gap-3 mb-2">
                <AlertCircle className="text-red-600" size={28} />
                <h2 className="text-2xl font-bold text-red-700">Contains Allergens ⚠️</h2>
              </div>
              <p className="text-red-700">Potential allergens were detected:</p>
              <div className="mt-4 space-y-2">
                {result.matches && result.matches.map((match: any, i: number) => (
                  <div key={i} className="bg-white p-3 rounded-lg">
                    <p className="font-semibold text-red-700">{match.name || match}</p>
                  </div>
                ))}
              </div>
              <p className="text-sm text-red-600 mt-4">
                💡 <strong>Tip:</strong> Create an account and add your allergens for personalized scanning!
              </p>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-4 mb-8">
            <button
              onClick={() => {
                setResult(null)
                setError('')
              }}
              className="px-6 py-3 bg-zinc-200 text-zinc-900 font-semibold rounded-lg hover:bg-zinc-300 transition flex items-center justify-center gap-2"
            >
              <RotateCcw size={18} /> Scan Another
            </button>
            <Link href="/dashboard" className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition text-center">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-12">
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
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-2"></div>
            <p className="text-zinc-600">Analyzing image...</p>
          </div>
        )}
      </div>
    </main>
  )
}
