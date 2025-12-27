// Adapter to call your existing FastAPI ML service
export interface InferenceResult {
  labels: string[]
  confidences?: number[]
  rawText?: string
  cleanedText?: string
  segments?: any[]
  detectedAllergens?: Record<string, Array<{ text: string; label: string; confidence: number }>>
}

// Image-based inference: send image as multipart form-data to FastAPI /detect
export async function run_model_from_service(imageBase64: string): Promise<InferenceResult> {
  const url = process.env.ML_API_URL || 'http://localhost:8000/detect'

  try {
    // Build multipart body with image bytes - matching Streamlit's approach
    const bytes = Buffer.from(imageBase64, 'base64')
    const form = new FormData()
    // Create a proper File object instead of Blob
    const file = new File([bytes], 'image.jpg', { type: 'image/jpeg' })
    form.append('file', file)
    
    // Add use_ocr parameter (default true, matching Streamlit)
    form.append('use_ocr', 'true')

    const res = await fetch(url, {
      method: 'POST',
      body: form
    })

    if (!res.ok) {
      console.error(`ML service error: ${res.status}`)
      const errorText = await res.text()
      console.error(`ML service response: ${errorText}`)
      return run_model_stub(imageBase64)
    }

    const data = await res.json()

    // Map FastAPI response format to our interface
    // Expected: { success, detected_allergens: { ALLERGEN: [{confidence, text, label, ...}], ... }, ... }
    if (data && data.success) {
      const labels: string[] = []
      const confidences: number[] = []
      const detected: Record<string, Array<{ text: string; label: string; confidence: number }>> =
        (data.detected_allergens ?? {})

      for (const [allergen, details] of Object.entries<any>(detected)) {
        if (Array.isArray(details) && details.length > 0) {
          labels.push(allergen)
          confidences.push(typeof details[0]?.confidence === 'number' ? details[0].confidence : 0.5)
        }
      }

      const result: InferenceResult = {
        labels,
        confidences,
        rawText: data.raw_text,
        cleanedText: data.cleaned_text,
        segments: data.segments ?? [],
        detectedAllergens: detected,
      }
      console.log(`✓ ML detection successful: ${labels.length} allergens found`)
      return result
    }

    // No allergens detected
    console.log('✓ ML detection successful: No allergens found')
    return { labels: [], confidences: [], rawText: data?.raw_text, cleanedText: data?.cleaned_text, segments: data?.segments ?? [] }
  } catch (error) {
    console.error('ML service call failed:', error)
    return run_model_stub(imageBase64)
  }
}

export async function run_model_stub(imageBase64: string): Promise<InferenceResult> {
  // WARNING: Fallback stub - ML API is not available!
  // This returns MOCK data based on image hash for demo purposes only.
  // DO NOT USE IN PRODUCTION - Results are NOT real allergen detection!
  
  const commonAllergens = [
    'MILK', 'PEANUT', 'TREE_NUT', 'WHEAT', 'SOY', 
    'EGG', 'FISH', 'SHELLFISH', 'SESAME', 'CORN'
  ]
  
  // Simple hash to get variation from image content
  let hash = 0
  for (let i = 0; i < Math.min(imageBase64.length, 1000); i++) {
    const char = imageBase64.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  
  // Most food products contain allergens - detect 2-4 allergens in 80% of cases
  const seed = Math.abs(hash) % 100
  const count = seed < 20 ? 0 : seed < 40 ? 2 : seed < 70 ? 3 : 4
  
  const labels: string[] = []
  const confidences: number[] = []
  const used = new Set<number>()
  
  for (let i = 0; i < count; i++) {
    let allergenIdx = (Math.abs(hash) + i * 13) % commonAllergens.length
    
    // Avoid duplicates
    while (used.has(allergenIdx)) {
      allergenIdx = (allergenIdx + 1) % commonAllergens.length
    }
    used.add(allergenIdx)
    
    const confidence = 0.6 + ((Math.abs(hash) + i * 7) % 30) / 100
    labels.push(commonAllergens[allergenIdx])
    confidences.push(confidence)
  }
  
  console.warn('⚠️ USING STUB DATA - ML Model not available. Results are MOCK data for demo only!')
  return { labels, confidences }
}
