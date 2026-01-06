'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Upload, AlertCircle, X, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import EnhancedScanResult from '@/components/scan/EnhancedScanResult'

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

      // Transform API response to match EnhancedScanResult format
      const allergenDetection = data.allergen_detection || {}
      
      const transformedResult = {
        contains: (allergenDetection.contains || []).map((a: any) => ({
          allergen: a.allergen,
          evidence: a.evidence || a.matched_keyword || '',
          keyword: a.keyword || a.matched_keyword || '',
          trigger_phrase: a.evidence || a.matched_keyword || '',
          source_section: 'ingredients' as const,
          confidence: a.confidence || 0.9
        })),
        may_contain: (allergenDetection.may_contain || []).map((a: any) => ({
          allergen: a.allergen,
          evidence: a.evidence || a.matched_keyword || '',
          keyword: a.keyword || a.matched_keyword || '',
          trigger_phrase: a.evidence || a.matched_keyword || '',
          source_section: 'warning_statement' as const,
          confidence: a.confidence || 0.9
        })),
        not_detected: (allergenDetection.not_detected || []).map((a: any) => ({
          allergen: typeof a === 'string' ? a : a.name,
          reason: 'No matching terms found in ingredients or warning statements',
          confidence: 0.1
        }))
      }

      setResult(transformedResult)
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
        <Link href="/dashboard" className="inline-flex items-center gap-2 text-zinc-600 hover:text-zinc-900 mb-6 font-medium">
          <ArrowLeft size={20} />
          Back to Dashboard
        </Link>
        <EnhancedScanResult 
          result={result}
          imageFile={selectedFile || undefined}
        />
        <div className="mt-6 grid md:grid-cols-2 gap-4">
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
          <Link href="/dashboard" className="px-6 py-3 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition text-center">
            Back to Dashboard
          </Link>
        </div>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-12">      <Link href="/dashboard" className="inline-flex items-center gap-2 text-zinc-600 hover:text-zinc-900 mb-6 font-medium">
        <ArrowLeft size={20} />
        Back to Dashboard
      </Link>      <div className="bg-white rounded-2xl shadow-lg p-8">
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
          className="border-2 border-dashed border-zinc-300 rounded-xl p-8 text-center cursor-pointer hover:border-emerald-600 hover:bg-emerald-50 transition mb-6"
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
              className="w-full py-3 bg-gradient-to-r from-emerald-600 to-green-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Scanning...' : 'Scan for Allergens'}
            </button>
          </>
        )}
      </div>
    </main>
  )
}
