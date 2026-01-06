'use client'

import Link from 'next/link'
import { HeartPulse, Menu, X } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'

export default function Header() {
  const [isOpen, setIsOpen] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [checking, setChecking] = useState(true)
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    // Check if user is logged in
    const checkAuth = async () => {
      try {
        const res = await fetch('/api/auth/session', { cache: 'no-store', credentials: 'include' })
        if (res.ok) {
          const session = await res.json()
          setUser(session.user)
        } else {
          setUser(null)
        }
      } catch (err) {
        // Not authenticated
        setUser(null)
      } finally {
        setChecking(false)
      }
    }
    checkAuth()
  }, [pathname])

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' })
      setUser(null)
      router.refresh()
      router.push('/')
      setIsOpen(false)
    } catch (err) {
      console.error('Logout failed:', err)
    }
  }

  return (
    <header className="bg-white border-b border-emerald-200 sticky top-0 z-50 shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 font-bold text-xl">
          <HeartPulse size={28} className="text-emerald-600" />
          <span className="bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-transparent">SafeEats</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-4">
          {!checking && user ? (
            <>
              <Link href="/history" className="text-gray-700 hover:text-emerald-600 transition font-medium">
                History
              </Link>
              <Link href="/profile" className="text-gray-700 hover:text-emerald-600 transition font-medium">
                Profile
              </Link>
              <div className="flex items-center gap-3 pl-3 border-l border-emerald-200">
                <span className="text-sm text-gray-600">{user.email}</span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-gray-700 hover:bg-emerald-50 rounded-lg transition"
                >
                  Logout
                </button>
                <Link
                  href="/dashboard"
                  className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-green-600 text-white rounded-lg shadow-sm hover:shadow-md transition"
                >
                  New Scan
                </Link>
              </div>
            </>
          ) : (
            <>
              <Link href="/signin" className="text-gray-700 hover:text-emerald-600 transition font-semibold">
                Sign In
              </Link>
              <Link href="/signup" className="px-6 py-2 bg-gradient-to-r from-emerald-600 to-green-600 text-white rounded-lg hover:shadow-md transition font-semibold">
                Create Account
              </Link>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden p-2 hover:bg-emerald-50 rounded-lg transition"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden border-t border-emerald-200 bg-white">
          <div className="px-4 py-4 space-y-4">
            {!checking && user ? (
              <>
                <Link href="/history" className="block text-gray-700 hover:text-emerald-600 font-medium" onClick={() => setIsOpen(false)}>
                  History
                </Link>
                <Link href="/profile" className="block text-gray-700 hover:text-emerald-600 font-medium" onClick={() => setIsOpen(false)}>
                  Profile
                </Link>
                <Link href="/dashboard" className="block px-6 py-2 bg-gradient-to-r from-emerald-600 to-green-600 text-white rounded-lg hover:shadow-md transition text-center" onClick={() => setIsOpen(false)}>
                  New Scan
                </Link>
                <hr className="border-emerald-200" />
                <p className="text-sm text-gray-600">{user.email}</p>
                <button
                  onClick={handleLogout}
                  className="w-full px-4 py-2 text-gray-700 hover:bg-emerald-50 rounded-lg transition text-left"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link href="/signin" className="block text-gray-700 hover:text-emerald-600 font-semibold" onClick={() => setIsOpen(false)}>
                  Sign In
                </Link>
                <Link href="/signup" className="block px-6 py-2 bg-gradient-to-r from-emerald-600 to-green-600 text-white rounded-lg hover:shadow-md transition text-center" onClick={() => setIsOpen(false)}>
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
