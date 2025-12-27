'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Camera, Upload, BarChart3, FileText, AlertCircle } from 'lucide-react'

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch('/api/auth/session')
        if (res.ok) {
          const session = await res.json()
          setUser(session.user)
        }
      } catch (err) {
        // User not logged in - that's okay!
      } finally {
        setLoading(false)
      }
    }
    checkAuth()
  }, [])

  return (
    <main className="max-w-7xl mx-auto px-4 py-12">
      {/* Welcome Section */}
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-zinc-900 mb-2">
          {user ? `Welcome back, ${user.name || user.email}! 👋` : 'Welcome to SafeEats! 👋'}
        </h1>
        <p className="text-lg text-zinc-600">Choose how you'd like to scan for allergens today</p>
      </div>

      {/* Scan Methods Grid */}
      <div className="grid md:grid-cols-2 gap-8 mb-16">
        {/* Image Upload */}
        <Link href="/scan-image">
          <div className="group bg-white rounded-2xl p-8 shadow-md hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 cursor-pointer h-full border-2 border-transparent hover:border-blue-400">
            <div className="bg-gradient-to-br from-blue-100 to-blue-200 w-16 h-16 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Upload className="text-blue-600" size={32} />
            </div>
            <h3 className="text-2xl font-bold text-zinc-900 mb-3">Upload Image</h3>
            <p className="text-zinc-600 mb-4 leading-relaxed">
              Take a photo of the product label and upload it. Our AI will instantly detect allergens listed on the packaging.
            </p>
            <div className="text-sm text-blue-600 font-semibold group-hover:translate-x-1 transition-transform">
              Start scanning →
            </div>
          </div>
        </Link>

        {/* Camera Capture */}
        <Link href="/scan-camera">
          <div className="group bg-white rounded-2xl p-8 shadow-md hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 cursor-pointer h-full border-2 border-transparent hover:border-purple-400">
            <div className="bg-gradient-to-br from-purple-100 to-purple-200 w-16 h-16 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Camera className="text-purple-600" size={32} />
            </div>
            <h3 className="text-2xl font-bold text-zinc-900 mb-3">Camera Capture</h3>
            <p className="text-zinc-600 mb-4 leading-relaxed">
              Use your device's camera for real-time scanning. Perfect for quick checks while shopping at the store.
            </p>
            <div className="text-sm text-purple-600 font-semibold group-hover:translate-x-1 transition-transform">
              Open camera →
            </div>
          </div>
        </Link>

        {/* Barcode Scan */}
        <Link href="/scan-barcode">
          <div className="group bg-white rounded-2xl p-8 shadow-md hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 cursor-pointer h-full border-2 border-transparent hover:border-pink-400">
            <div className="bg-gradient-to-br from-pink-100 to-pink-200 w-16 h-16 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <BarChart3 className="text-pink-600" size={32} />
            </div>
            <h3 className="text-2xl font-bold text-zinc-900 mb-3">Barcode Scan</h3>
            <p className="text-zinc-600 mb-4 leading-relaxed">
              Scan the product barcode (UPC/EAN code) to instantly look up ingredients and allergen information.
            </p>
            <div className="text-sm text-pink-600 font-semibold group-hover:translate-x-1 transition-transform">
              Scan barcode →
            </div>
          </div>
        </Link>

        {/* Text Input */}
        <Link href="/scan-text">
          <div className="group bg-white rounded-2xl p-8 shadow-md hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 cursor-pointer h-full border-2 border-transparent hover:border-orange-400">
            <div className="bg-gradient-to-br from-orange-100 to-orange-200 w-16 h-16 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <FileText className="text-orange-600" size={32} />
            </div>
            <h3 className="text-2xl font-bold text-zinc-900 mb-3">Paste Ingredients</h3>
            <p className="text-zinc-600 mb-4 leading-relaxed">
              Paste the ingredient list directly into the app for instant allergen detection and analysis.
            </p>
            <div className="text-sm text-orange-600 font-semibold group-hover:translate-x-1 transition-transform">
              Paste text →
            </div>
          </div>
        </Link>
      </div>

      {/* Quick Links */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-8 border border-blue-200 mb-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <h3 className="text-xl font-bold text-zinc-900 mb-2 flex items-center gap-2">
              <AlertCircle size={24} className="text-blue-600" />
              {user ? 'Personalize Your Profile' : 'Create an Account'}
            </h3>
            <p className="text-zinc-600">
              {user 
                ? 'Set up your allergen list for accurate, personalized results on every scan.' 
                : 'Sign up to save your allergen profile and track all your scans!'}
            </p>
          </div>
          {user ? (
            <Link href="/profile" className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all whitespace-nowrap">
              Manage Allergens
            </Link>
          ) : (
            <Link href="/signup" className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all whitespace-nowrap">
              Sign Up Now
            </Link>
          )}
        </div>
      </div>

      {/* History Link */}
      <div className="text-center">
        {user ? (
          <Link href="/history" className="text-blue-600 font-semibold hover:text-blue-700 text-lg">
            View Scan History →
          </Link>
        ) : (
          <p className="text-zinc-600 mb-4">
            <Link href="/signup" className="text-blue-600 font-semibold hover:text-blue-700">
              Sign up
            </Link>
            {' '}to save and track your scan history
          </p>
        )}
      </div>
    </main>
  )
}
