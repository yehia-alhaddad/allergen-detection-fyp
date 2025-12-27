"use client"
import { useState } from 'react'
import BarcodeScanner from '@/components/scan/BarcodeScanner'
import ScanResult from '@/components/scan/ScanResult'

export default function ScanBarcodePage() {
  const [barcode, setBarcode] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const lookup = async (code: string) => {
    setBarcode(code)
    setLoading(true)
    const res = await fetch('/api/barcode/lookup', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ barcode: code }) })
    const data = await res.json()
    setResult(data)
    setLoading(false)
  }

  return (
    <main className="space-y-6">
      <h1 className="text-2xl font-semibold">Scan Barcode</h1>
      <BarcodeScanner onDetected={lookup} />
      <div className="flex gap-2 items-center">
        <input value={barcode} onChange={e=>setBarcode(e.target.value)} className="border rounded px-3 py-2" placeholder="Enter barcode manually" />
        <button onClick={()=>lookup(barcode)} className="px-4 py-2 rounded bg-brand-600 text-white hover:bg-brand-700" disabled={!barcode}>Lookup</button>
      </div>
      {loading && <p>Looking up...</p>}
      {result && <div className="space-y-2">
        {result?.product?.name && <div className="font-semibold">{result.product.name}</div>}
        <ScanResult result={{ classification: result.classification, matches: result.matches || [] }} />
      </div>}
    </main>
  )
}
