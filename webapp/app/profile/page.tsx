'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Plus, Trash2, AlertCircle, Shield } from 'lucide-react'

interface Allergen {
  id?: string
  name: string
  synonyms?: string
  severity?: string
}

export default function ProfilePage() {
  const [user, setUser] = useState<any>(null)
  const [allergens, setAllergens] = useState<Allergen[]>([])
  const [loading, setLoading] = useState(true)
  const [isAdding, setIsAdding] = useState(false)
  const [newAllergen, setNewAllergen] = useState({ name: '', synonyms: '', severity: 'moderate' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const router = useRouter()

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch('/api/auth/session')
        if (res.ok) {
          const session = await res.json()
          setUser(session.user)
          // Load allergens
          const allergensRes = await fetch('/api/allergens/list')
          if (allergensRes.ok) {
            const data = await allergensRes.json()
            setAllergens(data.allergens || [])
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

  const handleAddAllergen = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newAllergen.name.trim()) {
      setError('Please enter an allergen name')
      return
    }

    setError('')
    setSuccess('')

    try {
      const res = await fetch('/api/allergens/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAllergen)
      })

      if (res.ok) {
        const data = await res.json()
        setAllergens([...allergens, data.allergen])
        setNewAllergen({ name: '', synonyms: '', severity: 'moderate' })
        setIsAdding(false)
        setSuccess('Allergen added successfully!')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        const data = await res.json()
        setError(data.error || 'Failed to add allergen')
      }
    } catch (err) {
      setError('An error occurred while adding allergen')
      console.error('Error:', err)
    }
  }

  const handleDeleteAllergen = async (id: string) => {
    if (!confirm('Are you sure you want to delete this allergen?')) return

    try {
      const res = await fetch(`/api/allergens/delete?id=${id}`, {
        method: 'DELETE'
      })

      if (res.ok) {
        setAllergens(allergens.filter(a => a.id !== id))
        setSuccess('Allergen deleted successfully!')
        setTimeout(() => setSuccess(''), 3000)
      } else {
        setError('Failed to delete allergen')
      }
    } catch (err) {
      setError('An error occurred while deleting allergen')
      console.error('Error:', err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!user) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="text-center">
            <Shield className="mx-auto mb-4 text-blue-600" size={48} />
            <h1 className="text-3xl font-bold text-zinc-900 mb-4">Create an Account</h1>
            <p className="text-zinc-600 mb-8 text-lg">
              Sign up to save your personal allergen profile and get personalized scanning results.
            </p>
            <Link href="/signup" className="inline-block px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-lg hover:shadow-lg transition-all">
              Sign Up Now
            </Link>
            <p className="text-zinc-600 mt-6">
              Already have an account? <Link href="/signin" className="text-blue-600 font-semibold hover:text-blue-700">Sign In</Link>
            </p>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-12">
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-zinc-900 mb-2">My Profile</h1>
        <p className="text-zinc-600 mb-8">Manage your account and allergens</p>

        {/* User Info */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 mb-8 border border-blue-200">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-zinc-600 mb-1">Email</p>
              <p className="text-lg font-semibold text-zinc-900">{user.email}</p>
            </div>
            <div>
              <p className="text-sm text-zinc-600 mb-1">Name</p>
              <p className="text-lg font-semibold text-zinc-900">{user.name || 'Not set'}</p>
            </div>
          </div>
        </div>

        {/* Allergens Section */}
        <h2 className="text-2xl font-bold text-zinc-900 mb-6 flex items-center gap-2">
          <Shield className="text-blue-600" size={28} />
          Your Allergens
        </h2>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center gap-2">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            ✓ {success}
          </div>
        )}

        {/* Allergen List */}
        {allergens.length > 0 ? (
          <div className="space-y-3 mb-8">
            {allergens.map((allergen) => (
              <div key={allergen.id} className="flex items-center justify-between bg-zinc-50 p-4 rounded-lg border border-zinc-200">
                <div className="flex-1">
                  <h3 className="font-semibold text-zinc-900">{allergen.name}</h3>
                  {allergen.synonyms && (
                    <p className="text-sm text-zinc-600">Also known as: {allergen.synonyms}</p>
                  )}
                  {allergen.severity && (
                    <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-semibold ${
                      allergen.severity === 'severe' ? 'bg-red-100 text-red-700' :
                      allergen.severity === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {allergen.severity.charAt(0).toUpperCase() + allergen.severity.slice(1)}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => handleDeleteAllergen(allergen.id || '')}
                  className="p-2 hover:bg-red-100 rounded-lg text-red-600 transition"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="mb-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-zinc-700">No allergens added yet. Add your allergens to get personalized scan results.</p>
          </div>
        )}

        {/* Add New Allergen */}
        {!isAdding ? (
          <button
            onClick={() => setIsAdding(true)}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
          >
            <Plus size={20} />
            Add Allergen
          </button>
        ) : (
          <form onSubmit={handleAddAllergen} className="bg-zinc-50 p-6 rounded-lg border border-zinc-200 space-y-4">
            <div>
              <label className="block text-sm font-semibold text-zinc-700 mb-2">Allergen Name *</label>
              <input
                type="text"
                value={newAllergen.name}
                onChange={(e) => setNewAllergen({ ...newAllergen, name: e.target.value })}
                placeholder="e.g., Peanuts, Milk, Shellfish"
                className="w-full px-4 py-2 border border-zinc-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-zinc-700 mb-2">Synonyms (optional)</label>
              <input
                type="text"
                value={newAllergen.synonyms}
                onChange={(e) => setNewAllergen({ ...newAllergen, synonyms: e.target.value })}
                placeholder="e.g., Arachis oil, Groundnuts"
                className="w-full px-4 py-2 border border-zinc-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-zinc-700 mb-2">Severity</label>
              <select
                value={newAllergen.severity}
                onChange={(e) => setNewAllergen({ ...newAllergen, severity: e.target.value })}
                className="w-full px-4 py-2 border border-zinc-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              >
                <option value="mild">Mild</option>
                <option value="moderate">Moderate</option>
                <option value="severe">Severe</option>
              </select>
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                className="flex-1 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
              >
                Add Allergen
              </button>
              <button
                type="button"
                onClick={() => setIsAdding(false)}
                className="flex-1 py-2 bg-zinc-300 text-zinc-900 font-semibold rounded-lg hover:bg-zinc-400 transition"
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        <div className="mt-12 pt-8 border-t border-zinc-200">
          <Link href="/dashboard" className="text-blue-600 font-semibold hover:text-blue-700">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    </main>
  )
}
