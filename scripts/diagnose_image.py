"""
Diagnostic script to test OCR extraction + allergen detection on an image.
Usage: python scripts/diagnose_image.py <path_to_image>
"""

import sys
import json
from pathlib import Path
from PIL import Image
import easyocr

# Add scripts to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from allergen_detection_pipeline import AllergenDetectionPipeline
from ocr_text_cleaner import OCRTextCleaner

def extract_ocr_from_image(image_path: str) -> str:
    """Extract text from image using EasyOCR."""
    print(f"\n[OCR] Loading image: {image_path}")
    reader = easyocr.Reader(['en'], gpu=False)
    
    result = reader.readtext(image_path)
    texts = [text[1] for text in result]
    ocr_text = "\n".join(texts)
    
    print(f"[OCR] Extracted {len(texts)} text regions")
    print(f"[OCR] Total characters: {len(ocr_text)}")
    return ocr_text

def diagnose(image_path: str):
    """Run full diagnostic on image allergen detection."""
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return
    
    print("=" * 80)
    print("ALLERGEN DETECTION DIAGNOSTIC")
    print("=" * 80)
    
    # Step 1: OCR extraction
    print("\n[STEP 1] OCR EXTRACTION")
    print("-" * 80)
    ocr_text = extract_ocr_from_image(str(image_path))
    print(f"\nRAW OCR TEXT (first 500 chars):\n{ocr_text[:500]}\n")
    
    # Step 2: Text cleaning
    print("\n[STEP 2] TEXT CLEANING")
    print("-" * 80)
    cleaner = OCRTextCleaner()
    cleaned_text = cleaner.clean(ocr_text)
    print(f"CLEANED TEXT (first 500 chars):\n{cleaned_text[:500]}\n")
    
    # Step 3: Dictionary extraction
    print("\n[STEP 3] DICTIONARY EXTRACTION")
    print("-" * 80)
    from ocr_text_cleaner import extract_allergen_mentions
    dict_allergens = extract_allergen_mentions(cleaned_text)
    print(f"Dictionary found {len(dict_allergens)} allergens:")
    for allergen, contexts in sorted(dict_allergens.items()):
        print(f"  ✓ {allergen}: {contexts[0][:60] if contexts else 'N/A'}...")
    
    # Step 4: Full pipeline detection
    print("\n[STEP 4] FULL PIPELINE DETECTION")
    print("-" * 80)
    pipeline = AllergenDetectionPipeline()
    report = pipeline.detect_allergens(ocr_text, ocr_source=image_path.name)
    
    print(f"Total allergens detected: {report['allergens_found']}")
    for allergen, data in sorted(report['allergens'].items()):
        sources = ", ".join(data.get('sources', []))
        conf = data.get('confidence', 0)
        print(f"  ✓ {allergen:15} | Confidence: {conf:.2f} | Sources: {sources}")
    
    # Step 5: Safety assessment
    print("\n[STEP 5] SAFETY ASSESSMENT")
    print("-" * 80)
    if report['allergens_found'] == 0:
        print("⚠️  NO ALLERGENS DETECTED - Product appears SAFE")
    else:
        print(f"✗ UNSAFE - {report['allergens_found']} allergens detected")
        print("Critical allergens:", [a for a in report['allergens'].keys() 
                                      if a in ['PEANUT', 'TREE_NUT', 'MILK', 'GLUTEN']])
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Image: {image_path}")
    print(f"OCR Text Length: {len(ocr_text)} chars")
    print(f"Cleaned Text Length: {len(cleaned_text)} chars")
    print(f"Dictionary Found: {len(dict_allergens)} allergens")
    print(f"Final Report: {report['allergens_found']} allergens")
    
    # Save full report
    report_path = ROOT / "results" / "diagnostic_report.json"
    with open(report_path, 'w') as f:
        json.dump({
            'image': str(image_path),
            'ocr_text': ocr_text,
            'cleaned_text': cleaned_text,
            'dict_allergens': dict_allergens,
            'final_report': report
        }, f, indent=2)
    print(f"\nFull report saved to: {report_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/diagnose_image.py <path_to_image>")
        print("Example: python scripts/diagnose_image.py product.jpg")
        sys.exit(1)
    
    diagnose(sys.argv[1])
