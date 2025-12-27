"""
Comprehensive image testing script.
Tests OCR → Cleaning → Detection pipeline on real product images.
"""

import sys
import json
from pathlib import Path
from PIL import Image
import easyocr

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from ocr_text_cleaner import OCRTextCleaner, extract_allergen_mentions
from allergen_detection_pipeline import AllergenDetectionPipeline

def test_image(image_path: str, expected_allergens: list):
    """Test full pipeline on a single image."""
    print("\n" + "=" * 80)
    print(f"TESTING: {Path(image_path).name}")
    print("=" * 80)
    
    # Step 1: OCR extraction
    print("\n[1] OCR EXTRACTION...")
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(image_path)
    ocr_text = "\n".join([text[1] for text in result])
    print(f"Extracted {len(ocr_text)} chars")
    print(f"Raw OCR (first 300 chars):\n{ocr_text[:300]}...\n")
    
    # Step 2: Text cleaning
    print("[2] TEXT CLEANING...")
    cleaner = OCRTextCleaner()
    cleaned = cleaner.clean(ocr_text)
    print(f"Cleaned (first 300 chars):\n{cleaned[:300]}...\n")
    
    # Step 3: Dictionary extraction
    print("[3] DICTIONARY DETECTION...")
    dict_allergens = extract_allergen_mentions(cleaned)
    print(f"Dictionary found: {sorted(dict_allergens.keys())}")
    for allergen, contexts in sorted(dict_allergens.items()):
        print(f"  • {allergen}: {contexts[0][:50] if contexts else 'N/A'}...")
    
    # Step 4: Full pipeline (includes NER)
    print("\n[4] FULL PIPELINE (Dictionary + NER)...")
    pipeline = AllergenDetectionPipeline()
    report = pipeline.detect_allergens(ocr_text, ocr_source=Path(image_path).name)
    
    final_allergens = sorted(report['allergens'].keys())
    print(f"Final detected: {final_allergens}")
    
    # Comparison
    print("\n" + "-" * 80)
    print("VALIDATION")
    print("-" * 80)
    print(f"Expected: {sorted(expected_allergens)}")
    print(f"Detected: {final_allergens}")
    
    expected_set = set(expected_allergens)
    detected_set = set(final_allergens)
    
    missing = expected_set - detected_set
    extra = detected_set - expected_set
    
    if missing:
        print(f"❌ MISSING: {missing}")
    if extra:
        print(f"⚠️  EXTRA: {extra}")
    
    if not missing and not extra:
        print("✅ PERFECT MATCH!")
        return True
    else:
        print("❌ MISMATCH")
        return False


def main():
    """Run comprehensive tests on all available images."""
    
    # Define test cases with expected allergens
    test_cases = [
        {
            "name": "mixed_nuts.jpg",
            "description": "Mixed nuts with peanuts, almonds, cashews, brazil nuts, walnuts",
            "expected": ['PEANUT', 'TREE_NUT', 'GLUTEN', 'SESAME', 'LUPIN', 'SOY', 'SULPHITES', 'MILK']
        },
        {
            "name": "milk_carton.jpg",
            "description": "Organic full cream milk carton",
            "expected": ['MILK']
        }
    ]
    
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "COMPREHENSIVE IMAGE TESTING" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Check if images exist
    test_dir = ROOT / "test_images"
    available_images = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
    
    if not available_images:
        print("\n⚠️  No test images found in test_images/")
        print("Please add images to test_images/ directory")
        return
    
    print(f"\nFound {len(available_images)} images to test")
    
    passed = 0
    failed = 0
    
    for img_path in available_images:
        # Find expected allergens if defined
        img_name = img_path.name
        expected = []
        for tc in test_cases:
            if tc["name"] in img_name or img_name in tc["name"]:
                expected = tc["expected"]
                break
        
        if not expected:
            print(f"\n⚠️  Skipping {img_name} - no expected allergens defined")
            continue
        
        result = test_image(str(img_path), expected)
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 80)


if __name__ == "__main__":
    main()
