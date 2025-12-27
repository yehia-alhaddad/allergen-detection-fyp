'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Upload, AlertCircle, CheckCircle, X } from 'lucide-react'
import Link from 'next/link'

export default function ScanImagePage() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<any>(null)
  const router = useRouter()

  const handleFileSelect = (file: File | null) => {
    if (!file) return
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }

    setSelectedFile(file)
    const reader = new FileReader()
    reader.onload = (e) => setPreview(e.target?.result as string)
    reader.readAsDataURL(file)
    setError('')
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    handleFileSelect(e.dataTransfer.files[0])
  }

  const handleSubmit = async () => {
    if (!selectedFile) return
    setLoading(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

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
                setSelectedFile(null)
                setPreview(null)
              }}
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
        <h1 className="text-3xl font-bold text-zinc-900 mb-2">Upload Image</h1>
        <p className="text-zinc-600 mb-8">Take a photo of the product label and upload it for instant allergen detection</p>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center gap-2">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {/* Drop Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-zinc-300 rounded-xl p-8 text-center cursor-pointer hover:border-blue-600 hover:bg-blue-50 transition mb-6"
        >
          {preview ? (
            <div className="relative">
              <img src={preview} alt="Preview" className="max-h-96 mx-auto rounded-lg" />
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedFile(null)
                  setPreview(null)
                }}
                className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600"
              >
                <X size={20} />
              </button>
            </div>
          ) : (
            <>
              <Upload className="mx-auto mb-4 text-zinc-400" size={48} />
              <p className="text-lg font-semibold text-zinc-900 mb-1">Click to upload or drag and drop</p>
              <p className="text-sm text-zinc-600">PNG, JPG, GIF up to 10MB</p>
            </>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={(e) => handleFileSelect(e.target.files?.[0] || null)}
          className="hidden"
        />

        {selectedFile && (
          <>
            <p className="text-sm text-zinc-600 mb-6">📸 {selectedFile.name}</p>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Scanning...' : 'Scan for Allergens'}
            </button>
          </>
        )}
      </div>
    </main>
  )
}
