'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { AlertCircle, CheckCircle } from 'lucide-react'
import Link from 'next/link'

export default function ScanBarcodePagePage() {
  const [barcode, setBarcode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<any>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!barcode.trim()) {
      setError('Please enter a barcode')
      return
    }

    setLoading(true)
    setError('')

    try {
      const res = await fetch('/api/barcode/lookup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ barcode: barcode.trim() })
      })

      const data = await res.json()

      if (!res.ok) {
        setError(data.error || 'Barcode lookup failed')
        return
      }

      setResult(data)
      setBarcode('')
    } catch (err) {
      setError('An error occurred while looking up the barcode')
      console.error('Barcode error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (result) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-zinc-900 mb-8">Product: {result.productName || 'Unknown'}</h1>

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
              onClick={() => setResult(null)}
              className="px-6 py-3 bg-zinc-200 text-zinc-900 font-semibold rounded-lg hover:bg-zinc-300 transition"
            >
              Scan Another
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
        <h1 className="text-3xl font-bold text-zinc-900 mb-2">Barcode Scanner</h1>
        <p className="text-zinc-600 mb-8">Enter the barcode (UPC/EAN code) of the product to look up ingredients and allergen information</p>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center gap-2">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-zinc-700 mb-2">Barcode Number</label>
            <input
              type="text"
              value={barcode}
              onChange={(e) => setBarcode(e.target.value)}
              placeholder="Enter UPC or EAN code (e.g., 012345678901)"
              className="w-full px-4 py-3 border border-zinc-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent text-lg tracking-wide"
              disabled={loading}
              autoFocus
            />
            <p className="text-xs text-zinc-500 mt-2">Usually 8-14 digits, found on product packaging</p>
          </div>

          <button
            type="submit"
            disabled={loading || !barcode.trim()}
            className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Looking up...' : '🔍 Look Up Product'}
          </button>
        </form>

        <div className="mt-12 p-6 bg-blue-50 rounded-xl border border-blue-200">
          <h3 className="font-semibold text-zinc-900 mb-3">📍 How to find the barcode:</h3>
          <ul className="space-y-2 text-sm text-zinc-700">
            <li>• Look for the barcode on the back or bottom of the packaging</li>
            <li>• It appears as vertical black and white stripes with numbers below</li>
            <li>• UPC codes (US/Canada) typically have 12 digits</li>
            <li>• EAN codes (Europe/International) typically have 13 digits</li>
          </ul>
        </div>
      </div>
    </main>
  )
}
