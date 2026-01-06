# Essential Scripts for Allergen Detection FYP

## Startup & Services
- **start-all-services.ps1** - Primary startup script: starts ML API + Next.js web with health checks
- **start-phone-tunnel.ps1** - LAN/HTTPS tunnel access for phone testing

## Core Pipeline
- **allergen_detection_pipeline.py** - Complete inference pipeline
- **ocr_text_cleaner.py** - Advanced OCR text cleaning utilities (150+ rules)

## Deployment & Maintenance
- **publish.ps1** - Publish to GitHub (used by VS Code task)

## Deprecated Scripts
See `../legacy/` folder for old startup scripts, training utilities, and test scripts no longer used.
