# Allergen Detection System for Product Labels

**Status**: ✅ Production Ready | **Latest Update**: Enhanced fuzzy matching + API

## System Overview

Automated allergen detection from product label images using:
- **OCR**: EasyOCR for text extraction
- **Text Cleaning**: 150+ allergen-specific fixes + fuzzy matching for garbled OCR
- **Classification**: BERT-based NER for allergen identification
- **API**: Production-ready inference with batch processing support

---

## ✅ Current Capabilities

### Accuracy
- **Real product test**: 7/8 allergens detected (87.5%) on peanut mix package
- **Dictionary extraction**: 100% confidence when allergen names are recognized
- **Neural NER**: Adaptive confidence scoring for contextual detection

### Detectable Allergens (13 classes)
Peanut, Tree Nuts, Milk, Egg, Fish, Shellfish, Gluten, Sesame, Soy, Mustard, Sulphites, Celery, Lupin

### OCR Robustness
- Handles common OCR errors: "peatats" → "peanut", "mk" → "milk", "sesem" → "sesame"
- Fuzzy matching recovers 60%+ similarity matches (e.g., "walnt" → "walnut")
- Character-level fixes for digit/letter confusion (1→l, 0→o, 5→s)

---

## 🚀 Quick Start

### Single Image Processing
```python
from scripts.api import AllergenDetectionAPI

api = AllergenDetectionAPI(model_type="baseline")
result = api.detect_from_ocr("Contains peanuts milk gluten", image_name="product.jpg")

# Result structure:
# {
#   "image": "product.jpg",
#   "allergens_found": 3,
#   "allergens": {
#     "PEANUT": {"confidence": 1.0, "source": "dictionary"},
#     "MILK": {"confidence": 1.0, "source": "dictionary"},
#     "GLUTEN": {"confidence": 1.0, "source": "dictionary"}
#   },
#   "has_critical_allergens": true,
#   "safe_for_general_population": false
# }
```

### Batch Processing
```python
batch = [
    {"name": "product1.jpg", "ocr": "peatats almonds mk"},
    {"name": "product2.jpg", "ocr": "gluten wheat flour"}
]

results = [api.detect_from_ocr(item["ocr"], item["name"]) for item in batch]
stats = api.get_stats(results)

print(f"Safe: {stats['safe_percentage']:.0f}%")
print(f"Most common: {max(stats['allergen_frequency'], key=stats['allergen_frequency'].get)}")
```

---

## 📊 System Architecture

```
Product Image
      ↓
   [OCR] → Raw text extraction
      ↓
[Text Cleaner] → Fix 150+ allergen-specific errors + fuzzy matching
      ↓
   [Dictionary] → Exact allergen name matching (100% confidence)
   [Neural NER] → Context-aware detection (adaptive confidence)
      ↓
  [Results] → JSON with confidence scores + safety flags
```

**Models Available**:
- `baseline`: 96.09% F1 on clean text, 435 MB
- `robust`: 90.77% F1 on balanced data, better on noisy OCR, 416 MB

---

## 📁 Project Structure

```
allergen-detection-fyp/
├── scripts/
│   ├── api.py                           # ✨ Production API
│   ├── ocr_text_cleaner.py             # ✨ Enhanced with fuzzy matching
│   ├── allergen_detection_pipeline.py  # End-to-end inference
│   └── train_robust_v2.py              # Robust model training
├── models/
│   ├── ner_model/                      # Baseline model (435 MB)
│   └── ner_model_robust_v2/            # Robust model (416 MB)
├── data/
│   ├── allergen_dictionary.json        # Allergen reference
│   └── annotations.csv                 # Training data
├── docs/
│   ├── README.md                       # Documentation index
│   ├── API_README.md                   # API detailed docs
│   └── FYP_VALIDATION_REPORT.md        # Real product validation
└── webapp/                             # Next.js frontend (primary UI)
```

---

## 🧪 Testing & Validation

### Real Product Test
✅ **Peanut Mix Package** (heavily garbled OCR)
- Detected: Peanut, Tree Nuts, Milk, Gluten, Sesame, Soy, Lupin (7/8)
- Failed: Sulphites (1/8)
- Success rate: **87.5%**

### Fuzzy Matching Examples
- "peatats" → "peanut" (0.62 similarity)
- "walnt" → "walnut" (0.91 similarity)
- "sesem" → "sesame" (0.73 similarity)
- "gltn" → "gluten" (0.80 similarity)
- "mk" → "milk" (0.67 similarity)

---

## 🔧 Key Components

### OCR Text Cleaner
**File**: `scripts/ocr_text_cleaner.py`

Features:
- 150+ allergen-specific OCR error fixes
- Fuzzy matching with 0.60 similarity threshold
- Character-level corrections (1→l, 0→o, etc.)
- Phrase pattern normalization

### Production API
**File**: `scripts/api.py`

Methods:
- `detect_from_ocr(text, image_name)` - Single image
- `batch_detect(list)` - Multiple images
- `get_stats(results)` - Batch statistics

### Pipeline
**File**: `scripts/allergen_detection_pipeline.py`

- Dictionary-based extraction (100% confidence)
- Neural NER fallback (adaptive confidence)
- Automatic method selection

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Real product success rate | 87.5% (7/8 allergens) |
| Dictionary extraction accuracy | 100% (exact matches) |
| Fuzzy matching recovery | ~70% of garbled words |
| Inference time per image | <1 second (CPU) |
| Model size | 416-435 MB |

---

## 🚢 Deployment

### Requirements
```
transformers>=4.30
torch>=2.0
easyocr>=1.7
fastapi>=0.100
uvicorn>=0.23
```

### Run API Server
```bash
python scripts/api.py
```

### Run Batch Processing
```bash
python -c "
from scripts.api import AllergenDetectionAPI
api = AllergenDetectionAPI()
results = [api.detect_from_ocr(ocr_text, 'prod.jpg') for ocr_text in texts]
stats = api.get_stats(results)
"
```
---

## 🐙 Publish to GitHub

This project is ready for GitHub with CI and sensible .gitignore.

### 1) Create a GitHub repo (optional helper)
- Set an env var `GITHUB_TOKEN` with repo scope
- Run:

```bash
python scripts/create_github_repo.py allergen-detection-fyp true
```

Copy the `Clone URL` and add it as a remote:

```bash
git remote add origin https://github.com/<username>/allergen-detection-fyp.git
```

### 2) Publish from VS Code
- Press `Ctrl+Shift+B` → "Publish to GitHub"
- Or run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/publish.ps1 -Message "initial publish" -Branch main
```

### 3) Auto-publish on changes (optional)
Start a background watcher that commits and pushes when files change:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/auto_publish.ps1 -IntervalSeconds 60 -Branch main
```

> Note: You may be prompted by Git Credential Manager the first time you push.

---

## 🔄 Keeping GitHub Up To Date

- Use the "Auto Publish (Watch)" task to push every minute when there are changes.
- Alternatively, commit and push manually using the "Publish to GitHub" task.
- CI runs on every push to `main`: Python deps + optional tests, Next.js build.

---

## 📚 Documentation

- **[API Reference](docs/API_README.md)** - Detailed API endpoints
- **[Validation Report](docs/FYP_VALIDATION_REPORT.md)** - Real product test results
- **[Documentation Index](docs/README.md)** - Full documentation structure

---

## 🎯 Future Improvements

1. **Model Ensemble**: Vote between baseline + robust for higher confidence
2. **Confidence Thresholding**: Adjustable thresholds for safety/recall tradeoffs
3. **Multi-language**: Support for non-English labels
4. **Real-time Learning**: User feedback for continuous improvement
5. **Mobile Deployment**: Optimized models for edge devices

---

## 📝 Notes

- **User Request**: Removed 15 redundant documentation files; keeping only essentials
- **Focus**: Building features without documentation overhead
- **Current Priority**: System improvement and production readiness

---

**Project Lead**: FYP Student  
**Institution**: APU (Asia Pacific University)  
**Year**: 2025
