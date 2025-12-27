"use client"
import { useState } from 'react'
import IngredientInput from '@/components/scan/IngredientInput'
import ScanResult from '@/components/scan/ScanResult'

export default function ScanTextPage() {
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const analyze = async (text: string) => {
    setLoading(true)
    const res = await fetch('/api/ingredients/check', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) })
    const data = await res.json()
    setResult(data)
    setLoading(false)
  }

  return (
    <main className="space-y-6">
      <h1 className="text-2xl font-semibold">Paste Ingredient Text</h1>
      <IngredientInput onSubmit={analyze} />
      {loading && <p>Analyzing...</p>}
      {result && <ScanResult result={{ classification: result.classification, matches: result.matches || [] }} />}
    </main>
  )
}
