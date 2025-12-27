"use client"
import { useState } from 'react'

export default function SignUpPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name })
    })
    setLoading(false)
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      setError(data?.error || 'Registration failed')
    } else {
      window.location.href = '/onboarding'
    }
  }

  return (
    <main className="max-w-sm mx-auto space-y-6">
      <h1 className="text-2xl font-semibold">Create your account</h1>
      <form onSubmit={onSubmit} className="space-y-4" aria-label="Sign up form">
        <label className="block">
          <span className="text-sm">Name</span>
          <input type="text" required value={name} onChange={e=>setName(e.target.value)} className="mt-1 w-full border rounded px-3 py-2" aria-label="Name" />
        </label>
        <label className="block">
          <span className="text-sm">Email</span>
          <input type="email" required value={email} onChange={e=>setEmail(e.target.value)} className="mt-1 w-full border rounded px-3 py-2" aria-label="Email" />
        </label>
        <label className="block">
          <span className="text-sm">Password</span>
          <input type="password" required value={password} onChange={e=>setPassword(e.target.value)} className="mt-1 w-full border rounded px-3 py-2" aria-label="Password" />
        </label>
        {error && <p className="text-red-600" role="alert">{error}</p>}
        <button disabled={loading} className="w-full px-4 py-2 rounded bg-brand-600 text-white hover:bg-brand-700" aria-busy={loading}>
          {loading ? 'Creating account...' : 'Sign up'}
        </button>
      </form>
    </main>
  )
}
