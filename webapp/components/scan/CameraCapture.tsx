"use client"
import { useEffect, useRef, useState } from 'react'

export default function CameraCapture({ onCapture }: { onCapture: (base64: string) => void }) {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        if (!videoRef.current) return
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      } catch (e: any) {
        setError(e?.message || 'Camera access denied')
      }
    })()
    return () => { videoRef.current?.srcObject && (videoRef.current.srcObject as MediaStream).getTracks().forEach(t => t.stop()) }
  }, [])

  const capture = () => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')!
    ctx.drawImage(video, 0, 0)
    const base64 = canvas.toDataURL('image/jpeg').split(',')[1]
    onCapture(base64)
  }

  return (
    <div className="space-y-2">
      <video ref={videoRef} className="w-full rounded border" autoPlay playsInline muted />
      <canvas ref={canvasRef} className="hidden" />
      <div className="flex gap-2">
        <button onClick={capture} className="px-4 py-2 rounded bg-brand-600 text-white hover:bg-brand-700">Capture</button>
      </div>
      {error && <p className="text-red-600" role="alert">{error}</p>}
    </div>
  )
}
