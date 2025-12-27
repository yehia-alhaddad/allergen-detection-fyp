# -*- coding: utf-8 -*-
"""Quick validation script - test API components without starting server."""
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

# Import API functions
from src.api.allergen_api import startup_event, clean_text, run_ner_prediction, map_to_standard_allergens, union_with_dictionary

async def test_api_logic():
    """Test API logic with sample texts."""
    print("\n" + "=" * 80)
    print("TESTING API LOGIC (without server)")
    print("=" * 80)
    
    # Initialize
    print("\n[1] Initializing API components...")
    await startup_event()
    print("✅ Components loaded\n")
    
    # Test cases
    test_cases = [
        {
            "name": "Milk Carton",
            "text": """Nutrition Information
Serving size: 250mL Servings per package: 4
Average qty per serving per 100mL
Energy 775kJ 310kJ
Protein 9.0g 3.6g
INGREDIENTS: Organic full cream milk
UNHOMOGENISED PASTEURISED FULL CREAM MILK""",
            "expected": ['MILK']
        },
        {
            "name": "Mixed Nuts",
            "text": """Ingredients: Mixed Nuts (98%) ( Peanuts, Almonds, Cashews, Peanuts Skin-On, Brazil Nuts, Walnuts )
Canola Oil, Salt (1%)
Contains: Peanuts, Almonds, Cashews, Peanuts, Brazil Nuts, Walnuts
May contain traces of: Cereals containing Gluten, Other Tree Nuts, Sesame Seeds, Lupins, Soy, Sulphites and Milk Products.""",
            "expected": ['GLUTEN', 'LUPIN', 'MILK', 'PEANUT', 'SESAME', 'SOY', 'SULPHITES', 'TREE_NUT']
        },
        {
            "name": "Clean Product",
            "text": "Ingredients: Water, Salt, Sugar, Citric Acid",
            "expected": []
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"[TEST] {test['name']}")
        print("-" * 80)
        
        # Clean
        cleaned = clean_text(test['text'])
        print(f"Cleaned: {cleaned[:100]}...")
        
        # NER
        entities = run_ner_prediction(cleaned)
        
        # Map
        mapped = map_to_standard_allergens(entities)
        
        # Union with dictionary
        merged = union_with_dictionary(cleaned, mapped)
        
        detected = sorted(merged.keys())
        expected = sorted(test['expected'])
        
        print(f"Expected: {expected}")
        print(f"Detected: {detected}")
        
        if detected == expected:
            print("✅ PASS\n")
            passed += 1
        else:
            print("❌ FAIL")
            print(f"   Missing: {set(expected) - set(detected)}")
            print(f"   Extra: {set(detected) - set(expected)}\n")
            failed += 1
    
    print("=" * 80)
    print(f"SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    return passed == len(test_cases)

if __name__ == "__main__":
    success = asyncio.run(test_api_logic())
    sys.exit(0 if success else 1)
