"use client"
import { useState } from 'react'

export default function IngredientInput({ onSubmit }: { onSubmit: (text: string) => void }) {
  const [text, setText] = useState('')
  return (
    <div className="space-y-2">
      <textarea value={text} onChange={e=>setText(e.target.value)} className="w-full h-32 border rounded p-2" placeholder="Paste ingredient list here" />
      <button onClick={()=>onSubmit(text)} className="px-4 py-2 rounded bg-brand-600 text-white hover:bg-brand-700">Analyze</button>
    </div>
  )
}
