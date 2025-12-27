export default function ScanResult({ result }: { result: { classification: string; matches: { name: string; source: string; snippet?: string }[] } }) {
  const badgeClass = result.classification === 'UNSAFE' ? 'bg-red-600' : result.classification === 'CAUTION' ? 'bg-yellow-500' : 'bg-green-600'
  return (
    <div className="space-y-3">
      <div className={`inline-block px-3 py-1 rounded text-white ${badgeClass}`}>{result.classification}</div>
      {result.matches?.length > 0 ? (
        <ul className="space-y-2">
          {result.matches.map((m, i) => (
            <li key={i} className="rounded border p-3">
              <div className="font-semibold">{m.name} <span className="text-xs text-zinc-600">({m.source})</span></div>
              {m.snippet && <div className="text-sm text-zinc-700">...{m.snippet}...</div>}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-zinc-600">No matches found. Always verify labels and consult medical advice when needed.</p>
      )}
    </div>
  )
}
