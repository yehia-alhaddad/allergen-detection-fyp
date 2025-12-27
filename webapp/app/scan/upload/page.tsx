"use client"
import { useState } from 'react'
import ScanResult from '@/components/scan/ScanResult'

export default function ScanUploadPage() {
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const onUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    setLoading(true)
    const res = await fetch('/api/infer/image', { method: 'POST', body: form })
    const data = await res.json()
    setResult(data)
    setLoading(false)
  }

  return (
    <main className="space-y-6">
      <h1 className="text-2xl font-semibold">Upload Image</h1>
      <input type="file" accept="image/*" onChange={onUpload} aria-label="Upload image" />
      {loading && <p>Analyzing...</p>}
      {result && <ScanResult result={{ classification: result.classification, matches: result.matches || [] }} />}
    </main>
  )
}
