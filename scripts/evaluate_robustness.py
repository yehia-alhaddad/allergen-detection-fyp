"""
Quick test: Compare baseline model vs. robustness on OCR-noisy text.
Don't retrain - just evaluate if dictionary+cleaner is enough for FYP.
"""

import json
from pathlib import Path
from ocr_text_cleaner import extract_allergen_mentions

# Load test data
test_data_path = Path(__file__).parent.parent / "data" / "ocr_results" / "all_ocr_texts.csv"

print("[Eval] Testing allergen extraction on real OCR data...")
print("=" * 80)

if test_data_path.exists():
    import csv
    
    allergen_counts = {}
    total = 0
    
    with open(test_data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 100:  # Test on first 100 samples
                break
            
            text = row.get('ocr_text', '')
            allergens = extract_allergen_mentions(text)
            
            for allergen in allergens:
                allergen_counts[allergen] = allergen_counts.get(allergen, 0) + 1
            
            if allergens and i < 3:
                print(f"\nSample {i+1}:")
                print(f"  Text (first 150 chars): {text[:150]}...")
                print(f"  Allergens found: {list(allergens.keys())}")
            
            total += 1
    
    print("\n" + "=" * 80)
    print(f"[Eval] Processed {total} OCR texts")
    print("\nAllergen Detection Summary (first 100 samples):")
    for allergen, count in sorted(allergen_counts.items(), key=lambda x: -x[1]):
        pct = 100 * count / total
        print(f"  {allergen:15} : {count:3} samples ({pct:5.1f}%)")
    
    coverage = len([c for c in allergen_counts.values() if c > 0]) / total * 100
    print(f"\nSamples with detected allergens: {len(allergen_counts)}/{total} ({coverage:.1f}%)")
else:
    print("[Eval] OCR data not found. Running on test text instead...")
    
    test_cases = [
        ("Peatats Mixed Muts", "peanuts, nuts"),
        ("Contains: Glu10n Cereak", "gluten, cereals"),
        ("Contains: Mk 5esame", "milk, sesame"),
        ("May contain: Tree Nus", "tree nuts"),
    ]
    
    for text, expected in test_cases:
        allergens = extract_allergen_mentions(text)
        print(f"\nText: {text}")
        print(f"  Expected: {expected}")
        print(f"  Detected: {', '.join(allergens.keys())}")

print("\n[Eval] Analysis complete!")
