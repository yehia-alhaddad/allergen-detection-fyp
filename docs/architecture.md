---
layout: default
title: Architecture & Design
---

# SafeEats Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js/React)                 │
│  [Dashboard] [Upload] [Camera] [Text] [Profile] [History]  │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
    ┌─────▼─────┐            ┌─────▼──────┐
    │ Next.js   │            │ NextAuth   │
    │ API Routes│            │ (Auth/Sess)│
    └─────┬─────┘            └────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend                                │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ /detect-text │  │ /detect-image│  │ /health (Probe) │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└────┬──────────────────────────────────────────────────┬────┘
     │                                                  │
     ▼                                                  ▼
┌──────────────────────────────────────────────────────────────┐
│ Detection Pipeline (OCR → Clean → NER → Strict Detect)     │
│                                                              │
│ 1. EasyOCR (Lazy Init)        → Image text extraction       │
│ 2. OCRTextCleaner (150+ rules)→ Normalize & fix artifacts   │
│ 3. BERT NER (recall=0.87)     → Extract allergen entities   │
│ 4. StrictAllergenDetector     → Verify with dictionary      │
│ 5. Union Strategy             → Merge ML + dict results     │
│ 6. Gemini Enhancement (async) → Optional recommendations    │
└──────────────────────────────────────────────────────────────┘
     │                                                  │
     ▼                                                  ▼
┌──────────────────────────┐            ┌──────────────────────┐
│ Prisma ORM               │            │ Redis Cache (opt)    │
│ SQLite (dev)             │            │ Rate Limiting        │
│ PostgreSQL (prod)        │            │ Session Data         │
└──────────────────────────┘            └──────────────────────┘
```

## Component Details

### 1. Frontend Layer (Next.js 14)
- **Authentication**: NextAuth with credential/provider support
- **Pages**: Signup, signin, dashboard, scan (image/camera/text), profile, history
- **API Bridge**: `lib/inference.ts` orchestrates ML calls with health checks
- **Rate Limiting**: User-scoped request throttling
- **State Management**: Personalized allergen profiles + scan history

### 2. Backend API (FastAPI)
- **Entry Point**: `src/api/allergen_api.py` (623 LOC)
- **Lazy Loading**: Heavy imports (torch, transformers, OCR) deferred until startup
- **Endpoints**:
  - `POST /detect-text` - Text ingredient analysis
  - `POST /detect-image` - Image upload & OCR
  - `GET /health` - Service health probe
- **Middleware**: CORS (wide-open for dev), request logging

### 3. Detection Pipeline
**File**: `src/allergen_detection/strict_detector.py` (552 LOC)

#### Layer 1: OCR Extraction
- **Engine**: EasyOCR or fallback to Tesseract
- **Input**: Raw image bytes
- **Output**: Extracted text + layout info
- **Latency**: 210ms (3MP) to 410ms (high-res)

#### Layer 2: Text Cleaning
- **File**: `scripts/ocr_text_cleaner.py`
- **Rules**: 150+ normalization fixes
- **Examples**: 
  - Casing: `ALMONDS` → `almonds`
  - Ligatures: `ﬁ` → `fi`
  - Spacing: `may-contain` → `may contain`
  - Symbols: `0` (zero) → `O` (letter)
- **Impact**: +8.4% accuracy improvement on OCR outputs

#### Layer 3: NER Inference
- **Model**: BERT (fine-tuned for allergens)
- **Path**: `models/ner_model/` or `models/experiments/*/pytorch_model.bin`
- **Confidence Threshold**: 0.3–0.5 (tuned for recall)
- **Metrics**: 89% F1-score, 87% recall, 91% precision

#### Layer 4: Strict Detection
- **Dictionary Match**: Authoritative (confidence 1.0)
- **Word Boundaries**: Prevents partial matches
- **Exclusion List**: Rules for false positives
- **Precautionary Handling**: "May contain" classification

#### Layer 5: Union Strategy
- **Merge**: NER results ∪ Dictionary matches
- **Confidence Scoring**: Weighted average
- **Output**: Detected allergens with sources

#### Layer 6: Enhancement (Async)
- **Provider**: Gemini API (optional)
- **Purpose**: Enriched recommendations
- **Non-blocking**: Fallback to base results on timeout

### 4. Database Layer (Prisma)
- **Dev**: SQLite (`prisma/dev.db`)
- **Prod**: PostgreSQL
- **Tables**: 
  - Users (auth, profiles)
  - UserAllergens (personalization)
  - ScanHistory (records)
  - Results (cached)

---

## Data Flow: Image Upload

```
1. User uploads image
   ↓
2. Next.js calls /api/infer/image
   ↓
3. Rate limiter checks user quota
   ↓
4. FastAPI receives image bytes
   ↓
5. EasyOCR extracts text (210–410ms)
   ↓
6. OCRTextCleaner applies 150+ rules
   ↓
7. BERT NER inference (65ms)
   ↓
8. Strict detector verifies (18ms)
   ↓
9. Union strategy merges results
   ↓
10. Optional Gemini enhancement (parallel, async)
    ↓
11. Response: {
      allergens: [...],
      evidence: {source: "OCR/NER/Dict", text: "..."},
      confidence: 0.95,
      safetyStatus: "ALERT" | "CAUTION" | "SAFE"
    }
    ↓
12. Next.js stores in history + renders result UI
```

---

## Resilience & Fallbacks

| Component | Fallback |
|-----------|----------|
| EasyOCR fails | Tesseract backup |
| GPU unavailable | CPU inference (slower but works) |
| BERT timeout | Keyword-only matching |
| Gemini API timeout | Base results returned (no enrichment) |
| Database down | In-memory cache for session |
| Health probe fails | Frontend retries with backoff |

---

## Performance Characteristics

| Operation | Median (p50) | p95 | Notes |
|-----------|---|---|---|
| Image preprocessing | 45ms | 85ms | Byte conversion + normalization |
| OCR (3MP) | 210ms | 410ms | GPU accelerated |
| NER inference | 65ms | 120ms | Batch size 1 |
| Strict detection | 18ms | 25ms | Dictionary lookup |
| Total latency | 299ms | 520ms | Full pipeline |
| Text-only input | 85ms | 165ms | No OCR step |

---

## Security Measures

✅ **HTTPS/TLS** (production)
✅ **API Key authentication** (optional)
✅ **CORS hardening** (production)
✅ **Rate limiting** (user-scoped)
✅ **Input validation** (image size, text length)
✅ **Prisma parameterized queries** (SQL injection prevention)
✅ **NextAuth secure sessions** (CSRF protection)

---

## Deployment Architecture

```
┌──────────────────────────────────────────┐
│ Reverse Proxy (Nginx/Caddy)              │
│ [HTTPS Termination, Load Balance, Cache] │
└───────────┬──────────────────────────────┘
            │
      ┌─────┴─────┐
      │           │
   ┌──▼──┐    ┌──▼──┐
   │ App │    │ App │  (Horizontal scaling)
   └─────┘    └─────┘
      │           │
      └─────┬─────┘
            │
      ┌─────▼──────┐
      │ Database   │
      │(PostgreSQL)│
      └────────────┘
```

---

## Monitoring & Observability

- **Logging**: FastAPI middleware logs all requests
- **Health Checks**: `/health` endpoint for service readiness
- **Metrics**: Response times, error rates, queue depth
- **Alerts**: (Optional) Trigger on timeout/error thresholds
