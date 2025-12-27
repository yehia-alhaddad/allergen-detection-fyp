"""
Production Allergen Detection API.
Simple interface for batch/single image processing.
"""

import json
import torch
from pathlib import Path
from typing import Dict, List, Any
import sys
sys.path.insert(0, str(Path(__file__).parent))
from allergen_detection_pipeline import AllergenDetectionPipeline


class AllergenDetectionAPI:
    """Production API for allergen detection from product images."""
    
    def __init__(self, model_type: str = "baseline"):
        """
        Args:
            model_type: "baseline" or "robust"
        """
        self.model_type = model_type
        root = Path(__file__).parent.parent
        
        if model_type == "robust":
            model_dir = root / "models" / "ner_model_robust_v2" / "final_model"
        else:
            model_dir = root / "models" / "ner_model"
        
        self.pipeline = AllergenDetectionPipeline(model_dir=str(model_dir))
    
    def detect_from_ocr(self, ocr_text: str, image_name: str = "unknown") -> Dict[str, Any]:
        """
        Detect allergens from OCR text.
        
        Args:
            ocr_text: Raw OCR output from image
            image_name: Source image filename
        
        Returns:
            {
                "image": str,
                "allergens_found": int,
                "allergens": {allergen_name: {confidence, source}},
                "safe": bool (no common allergens found)
            }
        """
        report = self.pipeline.detect_allergens(ocr_text, ocr_source=image_name)
        
        # Check for critical allergens
        critical_allergens = {"PEANUT", "TREE_NUT", "FISH", "SHELLFISH", "MILK", "EGG"}
        found_critical = any(a in report['allergens'] for a in critical_allergens)
        
        return {
            "image": image_name,
            "allergens_found": report['allergens_found'],
            "allergens": {
                allergen: {
                    "confidence": float(data.get('confidence', 0)),
                    "source": data.get('sources', ['unknown'])[0],
                    "detected": True
                }
                for allergen, data in report['allergens'].items()
            },
            "has_critical_allergens": found_critical,
            "safe_for_general_population": not found_critical
        }
    
    def batch_detect(self, ocr_texts: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Process multiple images.
        
        Args:
            ocr_texts: [{"image": "file.jpg", "ocr": "text..."}, ...]
        
        Returns:
            List of detection results
        """
        results = []
        for item in ocr_texts:
            result = self.detect_from_ocr(
                item.get("ocr", ""),
                item.get("image", "unknown")
            )
            results.append(result)
        
        return results
    
    def get_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics from batch results.
        """
        total = len(results)
        allergen_counts = {}
        critical_count = sum(1 for r in results if r['has_critical_allergens'])
        
        for result in results:
            for allergen in result['allergens']:
                allergen_counts[allergen] = allergen_counts.get(allergen, 0) + 1
        
        return {
            "total_images": total,
            "images_with_allergens": sum(1 for r in results if r['allergens_found'] > 0),
            "images_with_critical_allergens": critical_count,
            "allergen_frequency": allergen_counts,
            "safe_percentage": (total - critical_count) / max(total, 1) * 100
        }


def main():
    """Example usage."""
    print("[API] Initializing Allergen Detection API...")
    api = AllergenDetectionAPI(model_type="baseline")
    
    # Test OCR
    test_ocr = """MulheluFUNMAULL SERVES PER PACK 20 Mixed Muts (989) Peanuts, 
    Almonds Cashews; Peatats Contains: Peanus Brazil Nuts May contain traces ot 
    Cereak: containing Gluten; Other Tree Nus Sesame Seeds, Lupins Soy' Suphites 
    and Mk Products"""
    
    print("[API] Processing OCR text...")
    result = api.detect_from_ocr(test_ocr, image_name="test_product.jpg")
    
    print("\n[API] Results:")
    print(json.dumps(result, indent=2))
    
    print(f"\n[API] Detected {result['allergens_found']} allergens")
    print(f"[API] Safe for general population: {result['safe_for_general_population']}")


if __name__ == "__main__":
    main()
