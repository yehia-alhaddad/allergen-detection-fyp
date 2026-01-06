'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Clock, AlertCircle, CheckCircle } from 'lucide-react'

interface ScanResult {
  id: string
  type: string
  productName?: string
  classification: string
  matchedAllergens?: any
  createdAt: string
}

export default function HistoryPage() {
  const [user, setUser] = useState<any>(null)
  const [scans, setScans] = useState<ScanResult[]>([])
  const [loading, setLoading] = useState(true)
  const [clearing, setClearing] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch('/api/auth/session')
        if (res.ok) {
          const session = await res.json()
          setUser(session.user)
          // Load scan history
          const scansRes = await fetch('/api/history')
          if (scansRes.ok) {
            const data = await scansRes.json()
            setScans(data.scans || [])
          }
        } else {
          router.push('/signin')
        }
      } catch (err) {
        router.push('/signin')
      } finally {
        setLoading(false)
      }
    }
    checkAuth()
  }, [router])

  const getTypeIcon = (type: string) => {
    const icons: {[key: string]: string} = {
      'IMAGE': '📸',
      'CAMERA': '📹',
      'TEXT': '✍️'
    }
    return icons[type] || '🔍'
  }

  const getTypeLabel = (type: string) => {
    const labels: {[key: string]: string} = {
      'IMAGE': 'Image Upload',
      'CAMERA': 'Camera Capture',
      'TEXT': 'Text Input'
    }
    return labels[type] || type
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    )
  }

  if (!user) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="text-center">
            <Clock className="mx-auto mb-4 text-emerald-600" size={48} />
            <h1 className="text-3xl font-bold text-zinc-900 mb-4">Create an Account</h1>
            <p className="text-zinc-600 mb-8 text-lg">
              Sign up to save your allergen profile and track every scan in one place.
            </p>
            <Link href="/signup" className="inline-block px-8 py-4 bg-gradient-to-r from-emerald-600 to-green-600 text-white font-bold rounded-lg hover:shadow-lg transition-all">
              Sign Up Now
            </Link>
            <p className="text-zinc-600 mt-6">
              Already have an account? <Link href="/signin" className="text-emerald-700 font-semibold hover:text-emerald-800">Sign In</Link>
            </p>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-12">
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-zinc-900 mb-2 flex items-center gap-2">
          <Clock className="text-emerald-600" size={32} />
          Scan History
        </h1>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-8">
          <p className="text-zinc-600">All your product scans and results</p>
          {scans.length > 0 && (
            <button
              onClick={async () => {
                if (clearing) return
                const confirmed = window.confirm('Clear all saved scan history?')
                if (!confirmed) return
                setClearing(true)
                try {
                  const res = await fetch('/api/history', { method: 'DELETE' })
                  if (res.ok) {
                    setScans([])
                  }
                } finally {
                  setClearing(false)
                }
              }}
              className={`self-start md:self-auto px-4 py-2 rounded-lg border text-sm font-semibold transition ${
                clearing ? 'bg-zinc-100 text-zinc-500 border-zinc-200 cursor-not-allowed' : 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100'
              }`}
              disabled={clearing}
            >
              {clearing ? 'Clearing…' : 'Clear History'}
            </button>
          )}
        </div>

        {scans.length > 0 ? (
          <div className="space-y-4">
            {scans.map((scan) => (
              <div
                key={scan.id}
                className={`p-6 rounded-lg border-2 ${
                  scan.classification === 'SAFE'
                    ? 'bg-green-50 border-green-200'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{getTypeIcon(scan.type)}</span>
                      <h3 className="text-lg font-semibold text-zinc-900">
                        {scan.productName || getTypeLabel(scan.type)}
                      </h3>
                    </div>
                    <p className="text-sm text-zinc-600">
                      {getTypeLabel(scan.type)} • {new Date(scan.createdAt).toLocaleDateString()} at {new Date(scan.createdAt).toLocaleTimeString()}
                    </p>
                  </div>

                  <div
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold whitespace-nowrap ${
                      scan.classification === 'SAFE'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {scan.classification === 'SAFE' ? (
                      <>
                        <CheckCircle size={20} />
                        Safe
                      </>
                    ) : (
                      <>
                        <AlertCircle size={20} />
                        Contains Allergens
                      </>
                    )}
                  </div>
                </div>

                {scan.matchedAllergens && (
                  <div className="mt-4 pt-4 border-t border-opacity-20 border-current">
                    <p className="text-sm font-semibold text-zinc-700 mb-2">
                      {scan.classification === 'SAFE' ? 'Result: Safe' : 'Detected Allergens:'}
                    </p>
                    {typeof scan.matchedAllergens === 'string' ? (
                      <p className="text-sm text-zinc-700">
                        {scan.matchedAllergens}
                      </p>
                    ) : Array.isArray(scan.matchedAllergens) ? (
                      <div className="flex flex-wrap gap-2">
                        {scan.matchedAllergens.map((allergen: any, i: number) => {
                          const label =
                            typeof allergen === 'string'
                              ? allergen
                              : allergen?.name || allergen?.allergen || allergen?.label || JSON.stringify(allergen)
                          return (
                            <span key={i} className="px-3 py-1 bg-white rounded-full text-sm font-medium text-zinc-700">
                              {label}
                            </span>
                          )
                        })}
                      </div>
                    ) : null}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 bg-emerald-50 rounded-lg border border-emerald-200 text-center">
            <Clock className="mx-auto mb-3 text-emerald-600" size={32} />
            <p className="text-zinc-700 mb-4">No scans yet. Start scanning products to build your history.</p>
            <Link href="/dashboard" className="inline-block px-6 py-2 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition">
              Go to Dashboard
            </Link>
          </div>
        )}

        <div className="mt-12 pt-8 border-t border-zinc-200">
          <Link href="/dashboard" className="text-emerald-700 font-semibold hover:text-emerald-800">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    </main>
  )
}
