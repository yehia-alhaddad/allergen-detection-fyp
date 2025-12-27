# -*- coding: utf-8 -*-
"""Test smart context analyzer on real OCR samples."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd() / "scripts"))

from ocr_text_cleaner import OCRTextCleaner, extract_allergen_mentions
from allergen_detection_pipeline import AllergenDetectionPipeline

# Test 5 different product samples
test_dir = Path("data/ocr_results/test_samples")
txt_files = sorted(list(test_dir.glob("*.txt")))[:5]

cleaner = OCRTextCleaner()
pipeline = AllergenDetectionPipeline()

print("\nTESTING REAL PRODUCT OCR SAMPLES")
print("=" * 80)

for txt_file in txt_files:
    print(f"\nFile: {txt_file.name}")
    print("-" * 80)
    
    ocr_text = txt_file.read_text(encoding='utf-8', errors='ignore')
    cleaned = cleaner.clean(ocr_text)
    
    # Dictionary detection
    dict_allergens = extract_allergen_mentions(cleaned)
    
    # Full pipeline
    report = pipeline.detect_allergens(ocr_text, ocr_source=txt_file.name)
    final_allergens = sorted(report['allergens'].keys())
    
    print(f"OCR length: {len(ocr_text)} chars")
    print(f"Cleaned (first 150): {cleaned[:150]}...")
    print(f"\nDictionary found: {sorted(dict_allergens.keys())}")
    print(f"Final detected: {final_allergens}")
    
    if final_allergens:
        print("\nDetected allergens:")
        for allergen, data in sorted(report['allergens'].items()):
            sources = data.get('sources', [])
            conf = data.get('confidence', 0)
            print(f"  - {allergen}: {conf:.2f} confidence ({', '.join(sources[:2])})")
    else:
        print("CHECK: NO ALLERGENS DETECTED")

print("\n" + "=" * 80)
