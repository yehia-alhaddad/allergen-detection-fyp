# Allergen Detection System - Documentation Index

**Last Updated:** December 21, 2025

---

## 📚 Documentation Structure

### **Core Documentation**
- [README](../README.md) - Project overview and quick start
- [Training Readiness Assessment](training/TRAINING_READINESS_ASSESSMENT.md) - Full audit and training plan

### **API & Deployment**
- [API Documentation](API_README.md) - FastAPI endpoints reference
- [Deployment Package](DEPLOYMENT_PACKAGE_SUMMARY.md) - Deployment guide

### **Technical Guides**
- [System Architecture](SYSTEM_ARCHITECTURE.md) - System design and components
- [OCR Enhancement Guide](OCR_ENHANCEMENT_GUIDE.md) - OCR optimization strategies

### **Quick References**
- [Quick Start Guide](QUICK_START_NEXT_SESSION.md) - Get started fast
- [Quick Reference](Quick_Reference.md) - Common commands

---

## 📊 Results & Reports

Located in `../results/`:
- `training/` - Training metrics and iteration results
- `archive/` - Historical results

---

## 🧪 Testing

Located in `../tests/`:
- `unit/` - Unit tests
- `integration/` - Integration tests
- Test reports: `PIPELINE_TEST_REPORT.md`

---

## 🔄 Project Status

### Current Phase: **Model Training**
- ✅ OCR completed (10,083 images)
- ✅ Auto-annotations generated (2,983 samples)
- ✅ Train/val/test split ready
- 🔄 Training iteration 1 in progress

### Next Steps:
1. Complete iterative training (target F1 ≥ 65%)
2. Evaluate on test set
3. Deploy updated model to API

---

## 📁 Project Structure

```
allergen-detection-fyp/
├── configs/                # Configuration files
├── data/                   # Datasets and annotations
│   ├── raw/               # Raw images (10,083)
│   ├── ocr_results/       # OCR outputs
│   └── ner_training/      # Training data
├── docs/                   # Documentation (you are here)
│   └── training/          # Training-specific docs
├── models/                 # Trained models
│   └── ner_model/         # Current NER model
├── notebooks/              # Jupyter notebooks
├── results/                # Training results
│   ├── training/          # Iteration metrics
│   └── archive/           # Historical data
├── scripts/                # Automation scripts
├── src/                    # Source code
│   ├── api/               # FastAPI backend
│   ├── ner/               # NER components
│   ├── ocr/               # OCR engines
│   └── preprocessing/     # Image preprocessing
└── tests/                  # Test suites
    ├── unit/              # Unit tests
    └── integration/       # Integration tests
```

---

## 🔗 External Resources

- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [EasyOCR Documentation](https://github.com/JaidedAI/EasyOCR)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
