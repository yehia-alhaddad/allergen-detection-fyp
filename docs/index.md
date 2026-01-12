---
layout: default
title: SafeEats - AI Allergen Detection System
---

# SafeEats: AI-Powered Allergen Detection

**Real-time allergen detection from food labels using OCR and NER**

SafeEats is an intelligent system that detects allergens from packaged food images and ingredient lists. It combines:

- 📸 **EasyOCR** for text extraction from images
- 🧠 **BERT NER** for allergen entity recognition
- 🛡️ **Rule-based Strict Detection** for verified allergen classification
- 🌐 **FastAPI backend** for reliable inference
- ⚛️ **Next.js frontend** for mobile-friendly scanning

---

## Key Features

✅ **14 Allergen Categories** - Milk, peanuts, tree nuts, sesame, fish, shellfish, soy, wheat, eggs, mustard, sulfites, celery, lupin, mollusks

✅ **99%+ Detection Accuracy** - Hybrid approach combines ML with rule-based verification

✅ **Fast Inference** - 299ms median latency (p50) with GPU

✅ **Personalized Safety Profiles** - User-specific allergen tracking and recommendations

✅ **Multi-input Support** - Image upload, camera capture, or manual text entry

---

## Quick Start

### Backend Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn src.api.allergen_api:app --reload
```

### Frontend Setup
```bash
cd webapp
npm install
npm run dev
```

Visit `http://localhost:3000` to access the application.

---

## Documentation

- [Architecture & Design](./architecture.md)
- [API Documentation](./api.md)
- [Deployment Guide](./deployment.md)
- [Model Training](./training.md)
- [Troubleshooting](./troubleshooting.md)

---

## Project Structure

```
├── src/
│   ├── api/              # FastAPI server
│   ├── allergen_detection/  # Detection pipeline
│   ├── ocr/              # OCR engines
│   ├── ner/              # NER model
│   └── db/               # Database layer
├── webapp/               # Next.js frontend
├── models/               # Pre-trained models
├── data/                 # Allergen dictionary
├── notebooks/            # Analysis notebooks
└── tests/                # Test suite
```

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| NER F1-Score | 0.89 |
| Detection Recall | 97.4% |
| False Positive Rate | 2.2% |
| Median Latency (p50) | 299ms |
| p95 Latency | 520ms |

---

## License

This project is part of an Academic FYP submission.

## Contact

For questions or issues, please visit the [GitHub repository](https://github.com/yehia-alhaddad/allergen-detection-fyp).
