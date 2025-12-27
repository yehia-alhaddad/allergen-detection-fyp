#!/usr/bin/env python3
"""
Quick test script for barcode detector
Run: python test_barcode.py <barcode_number>
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.barcode.barcode_detector import BarcodeDetector


def test_barcode(barcode: str):
    """Test barcode lookup."""
    print(f"\n{'='*70}")
    print(f"Testing Barcode: {barcode}")
    print(f"{'='*70}\n")
    
    detector = BarcodeDetector()
    
    # Look up product
    result = detector.lookup_allergens_by_barcode(barcode)
    
    if result:
        print("✅ Product Found!\n")
        print(f"Product Name: {result['name']}")
        print(f"Brand: {result['brand']}")
        print(f"Country: {result['country']}")
        print(f"\nAllergens Detected ({len(result['allergens'])}):")
        for allergen in result['allergens']:
            print(f"  • {allergen}")
        
        if result['allergen_text']:
            print(f"\nAllergen Statement: {result['allergen_text']}")
        
        if result['ingredients']:
            print(f"\nIngredients: {result['ingredients'][:200]}...")
        
        print(f"\nOpenFoodFacts Link: {result['url']}")
    else:
        print("❌ Product Not Found")
        print("\nPossible reasons:")
        print("1. Barcode is invalid or incorrect")
        print("2. Product not in OpenFoodFacts database")
        print("3. Network error (check internet connection)")
        print("\nYou can add this product to OpenFoodFacts:")
        print(f"https://world.openfoodfacts.org/contribute")


def test_common_products():
    """Test with some common product barcodes."""
    print(f"\n{'='*70}")
    print("Testing Common Products")
    print(f"{'='*70}\n")
    
    test_barcodes = {
        "4006381333931": "Hanuta Minis (German snack)",
        "5901234123457": "Example EAN-13",
        "8801046102025": "Thai product",
    }
    
    detector = BarcodeDetector()
    
    for barcode, description in test_barcodes.items():
        print(f"\nTesting: {description}")
        print(f"Barcode: {barcode}")
        result = detector.lookup_allergens_by_barcode(barcode)
        
        if result:
            print(f"✅ Found: {result['name']}")
            print(f"   Allergens: {', '.join(result['allergens']) if result['allergens'] else 'None'}")
        else:
            print(f"❌ Not found in database")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific barcode
        barcode = sys.argv[1]
        test_barcode(barcode)
    else:
        # Test common products
        test_common_products()
        
        print(f"\n{'='*70}")
        print("Usage:")
        print(f"  python test_barcode.py <barcode>")
        print(f"  python test_barcode.py 4006381333931")
        print(f"{'='*70}\n")
