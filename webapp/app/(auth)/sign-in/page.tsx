"use client"
import { useState } from 'react'
import { signIn } from 'next-auth/react'
import Link from 'next/link'

export default function SignInPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    const res = await signIn('credentials', { email, password, redirect: false })
    setLoading(false)
    if (res?.error) setError(res.error)
    else window.location.href = '/dashboard'
  }

  return (
    <main className="max-w-sm mx-auto space-y-6">
      <h1 className="text-2xl font-semibold">Sign in</h1>
      <form onSubmit={onSubmit} className="space-y-4" aria-label="Sign in form">
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
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
      <p className="text-sm text-zinc-600">No account? <Link className="underline" href="/\(auth\)/sign-up">Sign up</Link></p>
    </main>
  )
}
