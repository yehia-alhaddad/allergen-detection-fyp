## Project Facts
- FastAPI ML API at src/api/allergen_api.py; lazy-imports torch/transformers/OCR inside startup_event to speed cold start—keep heavy imports out of module scope.
- Pipeline: image -> EasyOCR (src/ocr/simple_ocr_engine.py + layout_parser) -> OCRTextCleaner from scripts/ocr_text_cleaner.py (150+ fixes + fuzzy) -> BERT NER (models/ner_model, optional models/ner_model_robust_v2/final_model) -> dictionary union (data/allergen_dictionary.json) -> strict + enhanced detectors.
- Gemini enhancement optional: src/allergen_detection/enhanced_detector.py + src/utils/gemini_ai.py (GEMINI_API_KEY). Fallback uses built-in recommendations/cleaning if Gemini missing.
- Web frontend: Next.js 14 app router (webapp/) with NextAuth + Prisma (SQLite dev, Postgres prod). ML calls go through lib/inference.ts; default endpoint ML_API_URL=http://localhost:8000/detect-text.
- Do not use legacy/ scripts; current orchestration lives in scripts/ and src/. Docker is intentionally removed.

## Run/Debug
- Preferred: VS Code task "Start All Services (Robust)" (PowerShell) to start FastAPI + webapp with checks.
- Manual API dev: python -m uvicorn src.api.allergen_api:app --reload --host 0.0.0.0 --port 8000 (env: venv + requirements.txt). GPU optional; will fall back to CPU.
- Manual webapp dev: cd webapp && npm install && npm run dev (uses .env.local; run npx prisma migrate dev --name init on first setup).
- Acceptance smoke: manual flows in webapp/README.md (sign-up, onboarding, scan text). API quick checks: /health, /detect-text with sample payload.

## Implementation Patterns
- Keep detection unioned: dictionary hits are authoritative (confidence 1.0) and merged with NER outputs via union_with_dictionary in allergen_api.py; maintain uppercase allergen keys to satisfy tests.
- NER thresholds tuned for recall (0.3–0.5); avoid raising unless you adjust tests in tests/test_api_text.py and peers.
- Enhanced detector is async/parallel per allergen; errors should fall back to default recommendations, not fail the main response.
- OCRTextCleaner is imported via sys.path injection from scripts/; if you relocate, update path injection in allergen_api.py startup.
- Model discovery: primary path models/ner_model, fallback to models/experiments/**/pytorch_model.bin; robust model optional.
- Database init is best-effort (src/db); API must still run if DB unavailable—preserve try/except semantics.

## Web ↔ ML Contract
- Frontend expects ML_API_URL /detect-text JSON with cleaned_text, detected_allergens/allergen_detection. If you change API shape, update webapp/lib/inference.ts and scan components (webapp/components/scan/*).
- Auth/session handled by NextAuth; API CORS is wide-open for dev (allow_origins ["*"]). Harden before production.

## Data/Artifacts
- Allergen dictionary at data/allergen_dictionary.json; label mapping at data/ner_training/label_mapping.json. Large models live in models/; avoid committing new checkpoints unless necessary.
- Results/live cache under results/, data/ocr_results/—mind paths when writing tests.

## What to Avoid
- Modifying legacy/ or Docker instructions—deprecated. Keep startup scripts in scripts/ and VS Code tasks aligned.
- Blocking API startup with heavy imports or long GPU ops; keep lazy load/timeout pattern intact.