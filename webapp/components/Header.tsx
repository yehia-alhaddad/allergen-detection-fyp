'use client'

import Link from 'next/link'
import { Shield, Menu, X } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Header() {
  const [isOpen, setIsOpen] = useState(false)
  const [user, setUser] = useState<any>(null)
  const router = useRouter()

  useEffect(() => {
    // Check if user is logged in
    const checkAuth = async () => {
      try {
        const res = await fetch('/api/auth/session')
        if (res.ok) {
          const session = await res.json()
          setUser(session.user)
        }
      } catch (err) {
        // Not authenticated
      }
    }
    checkAuth()
  }, [])

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' })
      setUser(null)
      router.push('/')
      setIsOpen(false)
    } catch (err) {
      console.error('Logout failed:', err)
    }
  }

  return (
    <header className="bg-white border-b border-zinc-200 sticky top-0 z-50">
      <nav className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 font-bold text-xl text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
          <Shield size={28} className="text-blue-600" />
          <span>SafeEats</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          {user ? (
            <>
              <Link href="/dashboard" className="text-zinc-700 hover:text-blue-600 transition">
                Dashboard
              </Link>
              <Link href="/dashboard/history" className="text-zinc-700 hover:text-blue-600 transition">
                History
              </Link>
              <Link href="/dashboard/profile" className="text-zinc-700 hover:text-blue-600 transition">
                Profile
              </Link>
              <div className="flex items-center gap-3">
                <span className="text-sm text-zinc-600">{user.email}</span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-zinc-700 hover:bg-zinc-100 rounded-lg transition"
                >
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <Link href="/signin" className="text-zinc-700 hover:text-blue-600 transition">
                Sign In
              </Link>
              <Link href="/signup" className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-md transition">
                Sign Up
              </Link>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden p-2 hover:bg-zinc-100 rounded-lg transition"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden border-t border-zinc-200 bg-white">
          <div className="px-4 py-4 space-y-4">
            {user ? (
              <>
                <Link href="/dashboard" className="block text-zinc-700 hover:text-blue-600">
                  Dashboard
                </Link>
                <Link href="/dashboard/history" className="block text-zinc-700 hover:text-blue-600">
                  History
                </Link>
                <Link href="/dashboard/profile" className="block text-zinc-700 hover:text-blue-600">
                  Profile
                </Link>
                <hr />
                <p className="text-sm text-zinc-600">{user.email}</p>
                <button
                  onClick={handleLogout}
                  className="w-full px-4 py-2 text-zinc-700 hover:bg-zinc-100 rounded-lg transition text-left"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link href="/signin" className="block text-zinc-700 hover:text-blue-600">
                  Sign In
                </Link>
                <Link href="/signup" className="block px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-md transition text-center">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  )
}
