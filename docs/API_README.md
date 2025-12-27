# Allergen Detection API

## Overview

Production-ready REST API for detecting allergens in product ingredient labels using OCR and NER.

**Tech Stack:**
- Backend: FastAPI (Python 3.11+)
- OCR: EasyOCR (simple preprocessing)
- NER: BERT token classification (transformers)
- ML Framework: PyTorch with CUDA support

**Pipeline:** Image → OCR → Text Cleaning → NER Entity Extraction → Allergen Mapping → JSON Response

---

## Quick Start

### 1. Installation

```bash
cd allergen-detection-fyp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart

# Additional ML packages
pip install torch transformers easyocr
```

### 2. Run Server

```bash
# Development (with auto-reload)
python -m uvicorn src.api.allergen_api:app --reload --host 0.0.0.0 --port 8000

# Production (no reload)
python -m uvicorn src.api.allergen_api:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Access API

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/health

---

## API Endpoints

### `/health` — Health Check

**Method:** GET

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "ocr_available": true,
  "device": "cuda"
}
```

---

### `/detect` — Detect Allergens from Image

**Method:** POST

**Request:**
```bash
curl -X POST "http://localhost:8000/detect" \
  -F "file=@product_image.jpg" \
  -F "use_ocr=true"
```

**Parameters:**
- `file` (required): Product image (JPG/PNG)
- `use_ocr` (optional, default=true): Enable OCR extraction

**Response (Success):**
```json
{
  "success": true,
  "raw_text": "Ingredients: wheat flour, milk, eggs, soy lecithin, peanuts",
  "cleaned_text": "Ingredients wheat flour milk eggs soy lecithin peanuts",
  "detected_allergens": {
    "Peanuts": [
      {
        "text": "peanuts",
        "label": "ingredient",
        "confidence": 0.94
      }
    ],
    "Soy": [
      {
        "text": "soy lecithin",
        "label": "ingredient",
        "confidence": 0.87
      }
    ],
    "Milk": [
      {
        "text": "milk",
        "label": "ingredient",
        "confidence": 0.92
      }
    ]
  },
  "avg_confidence": 0.91,
  "timings": {
    "ocr": 1.23,
    "cleaning": 0.02,
    "ner": 0.34,
    "mapping": 0.01,
    "total": 1.60
  },
  "entities_found": [
    ["wheat", "ingredient", 0.88],
    ["milk", "ingredient", 0.92],
    ["eggs", "ingredient", 0.85],
    ["soy", "ingredient", 0.87],
    ["peanuts", "ingredient", 0.94]
  ]
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Could not read image"
}
```

---

### `/detect-text` — Detect Allergens from Text

**Method:** POST

**Request:**
```bash
curl -X POST "http://localhost:8000/detect-text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Ingredients: wheat, milk, peanuts"}'
```

**Parameters:**
- `text` (required): Ingredient list as string

**Response:**
```json
{
  "success": true,
  "raw_text": "Ingredients: wheat, milk, peanuts",
  "cleaned_text": "Ingredients wheat milk peanuts",
  "detected_allergens": {
    "Milk": [{"text": "milk", "label": "ingredient", "confidence": 0.92}],
    "Peanuts": [{"text": "peanuts", "label": "ingredient", "confidence": 0.94}]
  },
  "avg_confidence": 0.93,
  "timings": {
    "cleaning": 0.01,
    "ner": 0.32,
    "mapping": 0.01,
    "total": 0.34
  }
}
```

---

## Example Usage

### Python Client

```python
import requests
import json

API_URL = "http://localhost:8000"

# 1. Health check
response = requests.get(f"{API_URL}/health")
print(response.json())

# 2. Detect from image
with open("product.jpg", "rb") as f:
    response = requests.post(
        f"{API_URL}/detect",
        files={"file": f},
        data={"use_ocr": True}
    )
    result = response.json()
    
    if result["success"]:
        print(f"Allergens: {result['detected_allergens']}")
        print(f"Confidence: {result['avg_confidence']:.2f}")
        print(f"Processing time: {result['timings']['total']:.2f}s")
    else:
        print(f"Error: {result['error']}")

# 3. Detect from text
response = requests.post(
    f"{API_URL}/detect-text",
    json={"text": "Contains: milk, eggs, peanuts"}
)
print(response.json())
```

### cURL Examples

```bash
# Detect from image
curl -X POST "http://localhost:8000/detect" \
  -F "file=@label.jpg" \
  -F "use_ocr=true" | jq .

# Detect from text
curl -X POST "http://localhost:8000/detect-text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Contains milk and peanuts"}' | jq .

# Health check
curl "http://localhost:8000/health" | jq .
```

---

## Response Schema

### Success Response (Image)
```
{
  success: bool                    # Whether detection succeeded
  raw_text: string                # OCR extracted text
  cleaned_text: string            # Preprocessed text
  detected_allergens: {            # Mapped allergen categories
    "allergen_type": [
      {
        text: string              # Entity text span
        label: string             # NER label (ingredient, brand, etc)
        confidence: float         # Per-entity confidence [0-1]
      }
    ]
  }
  avg_confidence: float           # Average confidence across all entities
  timings: {
    ocr: float                    # OCR latency (seconds)
    cleaning: float               # Text cleaning latency
    ner: float                    # NER inference latency
    mapping: float                # Allergen mapping latency
    total: float                  # Total end-to-end latency
  }
  entities_found: [               # Raw NER output
    [text, label, confidence]
  ]
}
```

### Error Response
```
{
  success: false
  error: string                   # Error description
}
```

---

## Performance Characteristics

### Latency Breakdown (Average)

| Component | Time (sec) | % of Total |
|-----------|-----------|-----------|
| OCR       | 1.20      | 75%       |
| Cleaning  | 0.02      | 1%        |
| NER       | 0.34      | 21%       |
| Mapping   | 0.01      | 0.6%      |
| **Total** | **1.57**  | **100%**  |

### Resource Requirements

- **GPU Memory**: ~2GB (BERT model + OCR cache)
- **CPU**: 2+ cores recommended
- **Image Processing**: Handles up to 1920x1440 resolution
- **Max File Size**: 10MB (configurable)
- **Batch Processing**: Can handle 20-30 images/minute on single GPU

### Limits & Constraints

| Constraint | Value | Notes |
|-----------|-------|-------|
| Max image size | 1920x1440 | Larger images automatically resized |
| Max text length | 512 tokens | ~2000 characters for NER |
| Request timeout | 30s | Increase for larger batches |
| Concurrent requests | 100+ | Limited by available VRAM |
| Batch size | 1-50 | API processes 1 image at a time |

---

## Deployment Options

### Option 1: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install fastapi uvicorn
COPY . .
CMD ["uvicorn", "src.api.allergen_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t allergen-api .
docker run -p 8000:8000 allergen-api
```

### Option 2: Cloud Platforms

**AWS Lambda** (with API Gateway):
- Use containerized deployment
- Max memory: 10GB
- Max timeout: 15 minutes
- Cost: Pay per invocation

**Google Cloud Run**:
- Deploy Docker container
- Auto-scaling out of box
- Handles long-running OCR well
- Cost: Pay per second

**Heroku**:
- Simple `git push` deployment
- Limited to 30s requests (may timeout OCR)
- Free tier: dyno sleeps after 30 mins inactivity

**Azure App Service**:
- Windows/Linux support
- Always-on option available
- 1.5GB memory minimum

### Option 3: Kubernetes

For production at scale with multiple replicas.

---

## Error Handling

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Model not loaded (503) | Models didn't load on startup | Check model paths in startup_event() |
| Could not read image (400) | Invalid/corrupted image | Verify image file format (JPG/PNG) |
| No text extracted (400) | Image quality too low | Use preprocessing filters first |
| CUDA out of memory | Batch too large | Reduce concurrent requests or use CPU |
| Slow response (>10s) | OCR bottleneck | Consider using GPU or image compression |

---

## Testing

### Unit Tests

```python
# test_api.py
import pytest
from fastapi.testclient import TestClient
from src.api.allergen_api import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_detect_from_text():
    response = client.post(
        "/detect-text",
        json={"text": "Contains milk and peanuts"}
    )
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == True
    assert "detected_allergens" in result
```

Run tests:
```bash
pytest test_api.py -v
```

---

## Configuration

### Environment Variables

```bash
export MODEL_PATH="models/ner_model"
export ALLERGEN_DICT_PATH="data/allergen_dictionary.json"
export USE_GPU=True
export LOG_LEVEL=INFO
```

### API Settings (in allergen_api.py)

```python
# Modify these for your deployment
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
IMAGE_RESIZE_WIDTH = 1920
IMAGE_RESIZE_HEIGHT = 1440
NER_MAX_LENGTH = 512
BATCH_TIMEOUT = 30
```

---

## Troubleshooting

### Models Not Loading

```python
# Check model path
from pathlib import Path
model_path = Path("models/ner_model")
print(f"Model exists: {model_path.exists()}")
print(f"Files: {list(model_path.glob('*'))}")
```

### Slow OCR

```python
# Use GPU instead of CPU
ocr_engine = SimpleOCREngine(lang_list=["en"], gpu=True)
```

### Memory Issues

```python
# Reduce model precision (float16 instead of float32)
model = model.half()  # Reduces memory by ~50%
```

---

## Roadmap

- [ ] Batch processing endpoint (/batch-detect)
- [ ] Authentication & rate limiting
- [ ] Webhook support for async processing
- [ ] Confidence threshold customization
- [ ] Custom allergen dictionary upload
- [ ] Multi-language support
- [ ] Image preprocessing options
- [ ] Database logging

---

## License

MIT

## Support

For issues/questions:
- GitHub Issues: [link]
- Email: [your-email]
- Docs: http://localhost:8000/docs

