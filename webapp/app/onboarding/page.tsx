"use client"
import { useState } from 'react'

const COMMON = ['milk','eggs','peanuts','tree nuts','soy','wheat/gluten','fish','shellfish','sesame']

export default function OnboardingPage() {
  const [selected, setSelected] = useState<string[]>([])
  const [custom, setCustom] = useState('')
  const [synonyms, setSynonyms] = useState('')
  const [loading, setLoading] = useState(false)

  const toggle = (a: string) => setSelected(prev => prev.includes(a) ? prev.filter(x=>x!==a) : [...prev, a])

  const save = async () => {
    setLoading(true)
    const res = await fetch('/api/profile/allergens', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ allergens: selected, customAllergen: custom || null, synonyms: synonyms.split(',').map(s=>s.trim()).filter(Boolean) })
    })
    setLoading(false)
    if (res.ok) window.location.href = '/dashboard'
    else alert('Failed to save')
  }

  return (
    <main className="space-y-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-semibold">Set up your allergy profile</h1>
      <p className="text-zinc-600">Select common allergens and optionally add custom ones and synonyms.</p>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {COMMON.map(a => (
          <button key={a} onClick={()=>toggle(a)} className={`px-3 py-2 rounded border ${selected.includes(a) ? 'bg-brand-600 text-white' : 'hover:bg-zinc-50'}`}>{a}</button>
        ))}
      </div>
      <label className="block">
        <span className="text-sm">Custom allergen</span>
        <input value={custom} onChange={e=>setCustom(e.target.value)} className="mt-1 w-full border rounded px-3 py-2" placeholder="e.g., coconut" />
      </label>
      <label className="block">
        <span className="text-sm">Synonyms (comma-separated)</span>
        <input value={synonyms} onChange={e=>setSynonyms(e.target.value)} className="mt-1 w-full border rounded px-3 py-2" placeholder="e.g., casein, lactose" />
      </label>
      <div className="flex gap-2">
        <button onClick={save} disabled={loading} className="px-4 py-2 rounded bg-brand-600 text-white hover:bg-brand-700">{loading ? 'Saving...' : 'Save profile'}</button>
        <a href="/dashboard" className="px-4 py-2 rounded border">Skip</a>
      </div>
    </main>
  )
}
