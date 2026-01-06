'use client'

import { useState } from 'react'
import { AlertCircle, ArrowLeft, Sparkles } from 'lucide-react'
import Link from 'next/link'
import EnhancedScanResult from '@/components/scan/EnhancedScanResult'

export default function ScanTextPage() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<any>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim()) {
      setError('Please enter some text')
      return
    }

    setLoading(true)
    setError('')

    try {
      const res = await fetch('/api/ingredients/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text.trim() })
      })

      const data = await res.json()

      if (!res.ok) {
        setError(data.error || 'Text analysis failed')
        return
      }

      // Transform API response to match EnhancedScanResult format
      const allergenDetection = data.allergen_detection || {}
      
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
          reason: 'No allergen mention found in text',
          confidence: 0.1
        }))
      }

      setResult(transformedResult)
    } catch (err) {
      setError('An error occurred while analyzing the text')
      console.error('Analysis error:', err)
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
              setText('')
            }}
            className="px-6 py-3 bg-zinc-200 text-zinc-900 font-semibold rounded-lg hover:bg-zinc-300 transition"
          >
            Analyze Another
          </button>
          <Link href="/dashboard" className="px-6 py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition text-center">
            Back to Dashboard
          </Link>
        </div>
      </main>
    )
  }

  return (
    <main className="max-w-5xl mx-auto px-4 py-12">
      <Link href="/dashboard" className="inline-flex items-center gap-2 text-emerald-700 hover:text-emerald-900 mb-6 font-medium">
        <ArrowLeft size={20} />
        Back to Dashboard
      </Link>

      <div className="bg-gradient-to-br from-emerald-50 via-white to-blue-50 rounded-3xl border border-emerald-100 shadow-xl p-10">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6 mb-8">
          <div>
            <p className="inline-flex items-center gap-2 px-3 py-1 text-sm font-semibold text-emerald-800 bg-emerald-100 rounded-full">
              <Sparkles size={16} className="text-emerald-600" /> Text Scan
            </p>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mt-3">Paste Ingredients</h1>
            <p className="text-zinc-600 mt-2 max-w-2xl">Drop any ingredient list or product description and we will run the same allergen pipeline as camera and upload scans.</p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center gap-2">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-zinc-800 mb-2">Ingredients</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste the full ingredients list here..."
              rows={8}
              className="w-full px-4 py-3 border border-emerald-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none bg-white shadow-inner"
              disabled={loading}
            />
            <p className="text-xs text-zinc-500 mt-2">Supports any format - ingredient lists, product descriptions, etc.</p>
          </div>

          <button
            type="submit"
            disabled={loading || !text.trim()}
            className="w-full py-3 bg-gradient-to-r from-emerald-600 to-green-600 text-white font-semibold rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : '🔍 Check for Allergens'}
          </button>
        </form>

        <div className="mt-12 grid md:grid-cols-2 gap-4">
          <div className="p-6 bg-white rounded-xl border border-emerald-100 shadow-sm">
            <h3 className="font-semibold text-zinc-900 mb-3">💡 Example ingredients:</h3>
            <div className="text-sm text-zinc-700 bg-emerald-50 p-4 rounded-lg font-mono text-xs leading-relaxed border border-emerald-100">
              Wheat flour, sugar, eggs, milk, butter, baking powder, vanilla extract, salt
            </div>
          </div>
          <div className="p-6 bg-white rounded-xl border border-emerald-100 shadow-sm">
            <h3 className="font-semibold text-zinc-900 mb-3">Tips</h3>
            <ul className="text-sm text-zinc-700 space-y-2">
              <li className="flex gap-2"><span className="text-emerald-600">•</span> Include warning statements ("may contain")</li>
              <li className="flex gap-2"><span className="text-emerald-600">•</span> Paste full label text for best recall</li>
              <li className="flex gap-2"><span className="text-emerald-600">•</span> Supports multi-line and bullet formats</li>
            </ul>
          </div>
        </div>
      </div>
    </main>
  )
}
