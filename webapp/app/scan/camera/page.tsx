"use client"
import { useState } from 'react'
import CameraCapture from '@/components/scan/CameraCapture'
import ScanResult from '@/components/scan/ScanResult'

export default function ScanCameraPage() {
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const onCapture = async (base64: string) => {
    setLoading(true)
    const res = await fetch('/api/infer/capture', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ image: base64 }) })
    const data = await res.json()
    setResult(data)
    setLoading(false)
  }

  return (
    <main className="space-y-6">
      <h1 className="text-2xl font-semibold">Use Camera</h1>
      <CameraCapture onCapture={onCapture} />
      {loading && <p>Analyzing...</p>}
      {result && <ScanResult result={{ classification: result.classification, matches: result.matches || [] }} />}
    </main>
  )
}
