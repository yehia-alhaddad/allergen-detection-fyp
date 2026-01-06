# Essential Scripts for Allergen Detection FYP

## Startup & Services
- **start-all-services.ps1** - Primary startup script: starts ML API + Next.js web with health checks
- **start-phone-tunnel.ps1** - LAN/HTTPS tunnel access for phone testing

## Data Processing & Training
- **allergen_detection_pipeline.py** - Complete inference pipeline
- **prepare_ner_training_data.py** - Prepare training data for NER model
- **train_robust_v2.py** - Train robust v2 NER model variant
- **compare_models.py** - Compare model performance
- **evaluate_robustness.py** - Evaluate model robustness

## Text Processing
- **ocr_text_cleaner.py** - Advanced OCR text cleaning utilities

## Deployment & Maintenance
- **create_validation_report.py** - Generate validation reports
- **create_github_repo.py** - GitHub repo creation helper
- **publish.ps1** - Publish to GitHub
- **auto_publish.ps1** - Auto-publish on interval (background task)

## Deprecated Scripts
See `../legacy/` folder for old startup scripts and test utilities no longer used.
