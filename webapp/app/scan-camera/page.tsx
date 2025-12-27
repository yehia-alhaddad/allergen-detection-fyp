'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { AlertCircle, CheckCircle, StopCircle, RotateCcw } from 'lucide-react'
import Link from 'next/link'

export default function ScanCameraPage() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [cameraActive, setCameraActive] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<any>(null)
  const router = useRouter()

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        setCameraActive(true)
      }
    } catch (err) {
      setError('Could not access camera. Please check permissions.')
      console.error('Camera error:', err)
    }
  }

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks()
      tracks.forEach(track => track.stop())
      setCameraActive(false)
    }
  }

  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current) return

    const context = canvasRef.current.getContext('2d')
    if (!context) return

    canvasRef.current.width = videoRef.current.videoWidth
    canvasRef.current.height = videoRef.current.videoHeight
    context.drawImage(videoRef.current, 0, 0)

    canvasRef.current.toBlob(async (blob) => {
      if (!blob) return

      stopCamera()
      setLoading(true)
      setError('')

      try {
        const formData = new FormData()
        formData.append('file', blob, 'capture.jpg')

        const res = await fetch('/api/infer/image', {
          method: 'POST',
          body: formData
        })

        const data = await res.json()

        if (!res.ok) {
          setError(data.error || 'Scan failed')
          return
        }

        setResult(data)
      } catch (err) {
        setError('An error occurred while processing the image')
        console.error('Scan error:', err)
      } finally {
        setLoading(false)
      }
    }, 'image/jpeg', 0.9)
  }

  useEffect(() => {
    return () => {
      stopCamera()
    }
  }, [])

  if (result) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-zinc-900 mb-8">Scan Results</h1>

          {result.classification === 'SAFE' ? (
            <div className="mb-8 p-6 bg-green-50 border-2 border-green-500 rounded-xl">
              <div className="flex items-center gap-3 mb-2">
                <CheckCircle className="text-green-600" size={28} />
                <h2 className="text-2xl font-bold text-green-700">Safe to Eat ✓</h2>
              </div>
              <p className="text-green-700">No concerning allergens were detected in this product.</p>
            </div>
          ) : (
            <div className="mb-8 p-6 bg-red-50 border-2 border-red-500 rounded-xl">
              <div className="flex items-center gap-3 mb-2">
                <AlertCircle className="text-red-600" size={28} />
                <h2 className="text-2xl font-bold text-red-700">Contains Allergens ⚠️</h2>
              </div>
              <p className="text-red-700">Potential allergens were detected:</p>
              <div className="mt-4 space-y-2">
                {result.matches && result.matches.map((match: any, i: number) => (
                  <div key={i} className="bg-white p-3 rounded-lg">
                    <p className="font-semibold text-red-700">{match.name || match}</p>
                  </div>
                ))}
              </div>
              <p className="text-sm text-red-600 mt-4">
                💡 <strong>Tip:</strong> Create an account and add your allergens for personalized scanning!
              </p>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-4 mb-8">
            <button
              onClick={() => {
                setResult(null)
              }}
              className="px-6 py-3 bg-zinc-200 text-zinc-900 font-semibold rounded-lg hover:bg-zinc-300 transition"
            >
              Scan Another
            </button>
            <Link href="/dashboard" className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition text-center">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-12">
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-zinc-900 mb-2">Camera Capture</h1>
        <p className="text-zinc-600 mb-8">Point your camera at the product label to scan for allergens</p>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center gap-2">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {cameraActive ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full rounded-xl mb-6 bg-zinc-900"
            />
            <div className="flex gap-4">
              <button
                onClick={capturePhoto}
                disabled={loading}
                className="flex-1 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
              >
                {loading ? 'Processing...' : '📸 Capture & Scan'}
              </button>
              <button
                onClick={stopCamera}
                className="px-6 py-3 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-600 transition"
              >
                <StopCircle size={20} />
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="bg-zinc-100 rounded-xl h-96 flex items-center justify-center mb-6">
              <p className="text-zinc-600">Camera ready...</p>
            </div>
            <button
              onClick={startCamera}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
            >
              Open Camera
            </button>
          </>
        )}

        <canvas ref={canvasRef} className="hidden" />
      </div>
    </main>
  )
}
