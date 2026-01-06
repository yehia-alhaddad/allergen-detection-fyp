"use client"
import { useEffect, useRef, useState } from 'react'
import { Rotate3D, AlertCircle } from 'lucide-react'

export default function CameraCapture({ onCapture }: { onCapture: (base64: string) => void }) {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('environment')
  const [loading, setLoading] = useState(false)
  const [cameraReady, setCameraReady] = useState(false)
  const [permissionState, setPermissionState] = useState<'unknown' | 'granted' | 'prompt' | 'denied'>('unknown')
  const [shouldAutoStart, setShouldAutoStart] = useState(false)
  const streamRef = useRef<MediaStream | null>(null)
  const isInitializedRef = useRef(false)

  const startCamera = async (mode: 'user' | 'environment' = facingMode) => {
    try {
      setLoading(true)
      setError(null)

      // Stop existing stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => t.stop())
      }

      // Request new stream
      const constraints: MediaStreamConstraints = {
        video: {
          facingMode: mode,
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        },
        audio: false
      }

      // Guard for browser support and secure context (mobile browsers require HTTPS or localhost)
      const supportsMediaDevices = typeof navigator !== 'undefined' && !!navigator.mediaDevices && !!navigator.mediaDevices.getUserMedia
      const isSecure = typeof window !== 'undefined' && (window.isSecureContext || location.protocol === 'https:' || location.hostname === 'localhost')

      if (!supportsMediaDevices) {
        setError('Camera not available in this context. Use HTTPS or localhost and a supported browser.')
        setCameraReady(false)
        setLoading(false)
        return
      }
      if (!isSecure) {
        setError('Camera requires a secure context (HTTPS) on mobile. Try opening via a secure tunnel or localhost.')
        setCameraReady(false)
        setLoading(false)
        return
      }

      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      streamRef.current = stream

      // Persist permission success to reduce future prompts
      try {
        localStorage.setItem('cameraPermissionGranted', 'true')
        setPermissionState('granted')
      } catch (_) {
        /* ignore storage failures */
      }

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await new Promise(resolve => {
          videoRef.current!.onloadedmetadata = () => {
            videoRef.current!.play()
            setCameraReady(true)
            resolve(null)
          }
        })
      }
    } catch (e: any) {
      const message = e?.name === 'NotAllowedError'
        ? 'Camera permission denied. Please allow camera access.'
        : e?.name === 'NotFoundError'
        ? 'No camera device found on this device.'
        : e?.message || 'Failed to access camera'
      setError(message)
      setCameraReady(false)
    } finally {
      setLoading(false)
    }
  }

  const toggleCamera = async () => {
    const newMode = facingMode === 'environment' ? 'user' : 'environment'
    setFacingMode(newMode)
    await startCamera(newMode)
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop())
      streamRef.current = null
    }
    setCameraReady(false)
  }

  const capture = () => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas || !cameraReady) return

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Flip image for front camera
    if (facingMode === 'user') {
      ctx.scale(-1, 1)
      ctx.drawImage(video, -canvas.width, 0)
    } else {
      ctx.drawImage(video, 0, 0)
    }

    const base64 = canvas.toDataURL('image/jpeg', 0.9).split(',')[1]
    onCapture(base64)
  }

  useEffect(() => {
    // Prevent double initialization in React strict mode
    if (isInitializedRef.current) return
    isInitializedRef.current = true

    const stored = (() => {
      try { return localStorage.getItem('cameraPermissionGranted') === 'true' } catch { return false }
    })()

    const checkPermission = async () => {
      if (typeof navigator === 'undefined' || !navigator.permissions) {
        setPermissionState(stored ? 'granted' : 'prompt')
        setShouldAutoStart(stored)
        return
      }
      try {
        const status = await navigator.permissions.query({ name: 'camera' as PermissionName })
        const state = status.state as PermissionState
        setPermissionState(state)
        if (state === 'granted' || stored) {
          setShouldAutoStart(true)
        }
        status.onchange = () => {
          const next = status.state as PermissionState
          setPermissionState(next)
        }
      } catch {
        setPermissionState(stored ? 'granted' : 'prompt')
        setShouldAutoStart(stored)
      }
    }

    checkPermission()

    return () => {
      stopCamera()
    }
  }, [])

  // Auto-start only when permission already granted/persisted
  useEffect(() => {
    if (shouldAutoStart && !cameraReady && !loading) {
      startCamera()
    }
  }, [shouldAutoStart])

  return (
    <div className="space-y-4">
      {/* Camera feed */}
      <div className="relative rounded-lg overflow-hidden bg-black aspect-video">
        <video
          ref={videoRef}
          className="w-full h-full object-cover"
          autoPlay
          playsInline
          muted
        />
        {!cameraReady && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            <div className="text-white text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-2"></div>
              <p className="text-sm">Initializing camera...</p>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex gap-3 flex-wrap">
        {!cameraReady && (
          <button
            onClick={() => startCamera()}
            disabled={loading}
            className="flex-1 px-6 py-3 rounded-lg bg-green-600 text-white font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            📷 Enable Camera
          </button>
        )}
        <button
          onClick={capture}
          disabled={!cameraReady || loading}
          className="flex-1 px-6 py-3 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          📸 Capture Photo
        </button>
        <button
          onClick={toggleCamera}
          disabled={loading || !cameraReady}
          className="px-4 py-3 rounded-lg bg-zinc-600 text-white hover:bg-zinc-700 disabled:opacity-50 transition flex items-center gap-2"
          title={`Switch to ${facingMode === 'environment' ? 'front' : 'back'} camera`}
        >
          <Rotate3D size={18} />
          {facingMode === 'environment' ? 'Front' : 'Back'}
        </button>
      </div>

      {/* Camera indicator */}
      <div className="text-xs text-zinc-500 text-center space-y-1">
        <div>{facingMode === 'environment' ? '📷 Back Camera' : '🤳 Front Camera'}</div>
        {permissionState === 'denied' && (
          <div className="text-red-600">Camera permission blocked. Enable in browser settings.</div>
        )}
        {permissionState === 'prompt' && !cameraReady && (
          <div className="text-amber-600">Tap “Enable Camera” to grant access. We remember once allowed.</div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-lg bg-red-50 border border-red-200 flex gap-3">
          <AlertCircle size={18} className="text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-red-800">Camera Error</p>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      <canvas ref={canvasRef} className="hidden" />
    </div>
  )
}
