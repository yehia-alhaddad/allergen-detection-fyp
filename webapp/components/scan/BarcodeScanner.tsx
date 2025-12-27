"use client"
import { useEffect, useRef, useState } from 'react'
import { BrowserMultiFormatReader } from '@zxing/browser'

export default function BarcodeScanner({ onDetected }: { onDetected: (code: string) => void }) {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [running, setRunning] = useState(false)

  useEffect(() => {
    const reader = new BrowserMultiFormatReader()
    let stopped = false

    async function start() {
      try {
        const devices = await reader.listVideoInputDevices()
        const deviceId = devices[0]?.deviceId
        if (!deviceId) throw new Error('No camera found')
        setRunning(true)
        await reader.decodeFromVideoDevice(deviceId, videoRef.current!, (result, err) => {
          if (stopped) return
          if (result) {
            onDetected(result.getText())
          }
        })
      } catch (e: any) {
        setError(e?.message || 'Scanner error')
      }
    }

    start()
    return () => { stopped = true; reader.reset() }
  }, [onDetected])

  return (
    <div className="space-y-2">
      <video ref={videoRef} className="w-full rounded border" autoPlay muted playsInline />
      {error && <p className="text-red-600" role="alert">{error}</p>}
      <p className="text-sm text-zinc-600">Point the camera at the barcode.</p>
    </div>
  )
}
