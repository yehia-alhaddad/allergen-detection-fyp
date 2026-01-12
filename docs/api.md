---
layout: default
title: API Documentation
---

# SafeEats API Documentation

## Base URL

**Development**: `http://localhost:8000`
**Production**: `https://api.safeeats.app` (example)

---

## Endpoints

### 1. Health Check

```
GET /health
```

**Purpose**: Service readiness probe (used by load balancers & frontends)

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-12T10:30:45Z",
  "models_loaded": true,
  "ocr_engine": "easyocr",
  "gpu_available": true
}
```

**Status Codes**:
- `200 OK` - Service healthy
- `503 Service Unavailable` - Models not loaded

---

### 2. Detect Text Input

```
POST /detect-text
```

**Purpose**: Analyze ingredient list (text)

**Request**:
```json
{
  "cleaned_text": "Contains: milk, eggs, and tree nuts",
  "user_id": "uuid-optional"
}
```

**Response**:
```json
{
  "detected_allergens": [
    {
      "allergen": "milk",
      "confidence": 0.99,
      "source": "dictionary",
      "evidence": "Contains: milk"
    },
    {
      "allergen": "eggs",
      "confidence": 0.96,
      "source": "ner",
      "evidence": "eggs"
    },
    {
      "allergen": "tree nuts",
      "confidence": 0.94,
      "source": "dictionary",
      "evidence": "tree nuts"
    }
  ],
  "allergen_detection": {
    "high_confidence": ["milk", "eggs", "tree nuts"],
    "recommendations": ["Store allergen separately"]
  },
  "processing_time_ms": 85
}
```

**Status Codes**:
- `200 OK` - Success
- `400 Bad Request` - Invalid input (empty text, wrong format)
- `422 Unprocessable Entity` - Text too long (>5000 chars)
- `503 Service Unavailable` - NER model not loaded

---

### 3. Detect Image Upload

```
POST /detect-image
```

**Purpose**: Extract text from food label image and analyze

**Request** (multipart/form-data):
```
Content-Type: multipart/form-data

file: <image.jpg>          (JPEG, PNG, max 10MB)
user_id: uuid-optional
```

**Response** (same as `/detect-text`):
```json
{
  "detected_allergens": [...],
  "allergen_detection": {...},
  "processing_time_ms": 350,
  "ocr_text": "Ingredients: ...",
  "image_quality_score": 0.92
}
```

**Status Codes**:
- `200 OK` - Success
- `400 Bad Request` - No file, wrong format
- `413 Payload Too Large` - File >10MB
- `503 Service Unavailable` - OCR model not loaded

---

### 4. Detect Image Capture (Camera)

```
POST /detect-image-capture
```

**Purpose**: Fast inference from mobile camera capture (base64 encoded)

**Request**:
```json
{
  "image_base64": "data:image/jpeg;base64,...",
  "user_id": "uuid-optional"
}
```

**Response**: Same as `/detect-image`

**Status Codes**: Same as `/detect-image`

---

## Error Responses

All errors return standard format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "CODE",
  "timestamp": "2024-01-12T10:30:45Z"
}
```

### Common Errors

| Code | HTTP | Meaning | Solution |
|------|------|---------|----------|
| `INVALID_INPUT` | 400 | Empty or malformed text | Verify input format |
| `TEXT_TOO_LONG` | 422 | >5000 characters | Reduce text length |
| `INVALID_FILE` | 400 | Not an image | Use JPEG or PNG |
| `FILE_TOO_LARGE` | 413 | >10MB | Compress image |
| `MODEL_NOT_LOADED` | 503 | Model failed to init | Restart service |
| `OCR_FAILED` | 500 | OCR extraction error | Try clearer image |
| `NER_TIMEOUT` | 504 | Model inference timeout | Retry with simpler text |

---

## Rate Limiting

**Per User**:
- 30 requests / minute for authenticated users
- 10 requests / minute for anonymous users

**Response Headers**:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 28
X-RateLimit-Reset: 1705066245
```

**Exceeds Limit**:
```
HTTP 429 Too Many Requests

{
  "detail": "Rate limit exceeded. Retry after 45 seconds."
}
```

---

## Authentication (Optional)

For production deployments with user tracking:

```
Authorization: Bearer <jwt_token>
```

Obtained via NextAuth during user signup/signin.

---

## Examples

### cURL: Text Detection

```bash
curl -X POST http://localhost:8000/detect-text \
  -H "Content-Type: application/json" \
  -d '{
    "cleaned_text": "Contains: peanuts, milk, sesame"
  }'
```

### cURL: Image Detection

```bash
curl -X POST http://localhost:8000/detect-image \
  -F "file=@product_label.jpg"
```

### Python: Text Detection

```python
import requests

response = requests.post(
    "http://localhost:8000/detect-text",
    json={"cleaned_text": "Contains: milk, tree nuts"}
)
print(response.json())
```

### TypeScript/Next.js: (from `lib/inference.ts`)

```typescript
const response = await fetch("/api/infer/text", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ cleaned_text: "Contains: peanuts" })
});
const data = await response.json();
```

---

## Response Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `allergen` | string | Allergen name (lowercase, canonical) |
| `confidence` | float | 0.0–1.0 confidence score |
| `source` | string | `dictionary`, `ner`, or `fusion` |
| `evidence` | string | Text snippet where allergen found |
| `safetyStatus` | string | `ALERT`, `CAUTION`, or `SAFE` |
| `processing_time_ms` | int | Total latency in milliseconds |

---

## Supported Allergens

1. Milk
2. Peanuts
3. Tree Nuts
4. Sesame
5. Fish
6. Shellfish
7. Soy
8. Wheat
9. Eggs
10. Mustard
11. Sulfites
12. Celery
13. Lupin
14. Mollusks

---

## Testing the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Smoke Test (Text)
```bash
curl -X POST http://localhost:8000/detect-text \
  -H "Content-Type: application/json" \
  -d '{"cleaned_text": "Contains milk and peanuts"}'
```

### Smoke Test (Image)
```bash
curl -X POST http://localhost:8000/detect-image \
  -F "file=@test_images/snickers.jpg"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Connection refused` | Ensure FastAPI is running on port 8000 |
| `Model not loaded` | Check GPU/CUDA availability; restart service |
| `OCR timeout` | Image may be too large; reduce resolution |
| `NER timeout` | Text too long; submit in batches |
| `Rate limit exceeded` | Wait before retrying; upgrade to paid tier |

---

## Version History

### v1.0.0 (Current)
- ✅ Text & image detection
- ✅ 14 allergen categories
- ✅ 97.4% recall, 2.2% false positive rate
- ✅ 299ms median latency

### Future (v1.1)
- Batch detection
- Webhook notifications
- Usage analytics dashboard
