"""
Compare Baseline vs Robust Model on OCR-Noise Text.
Shows improvement from training on balanced data.
"""

import json
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForTokenClassification

# Test on real peanut product OCR (garbled)
TEST_OCR = """MulheluFUNMAULL SERVES PER PACK 20 SERVE SIZE 25g Avg: Per Avg Per Serve 100g 619kJ 2475kJ Energy Protien 6.5g 25.9g Fat; Total 121g 48.2g Saturated Fat 0.Tg 2.8g Carbohydrate 21g 8.5g Sugars 1.4g 5.4g Sodium S1mg 202mg Ingredients: Mixed Muts (989) Peanuts, Almonds Cashews; Peatats Skin-On Brazi Muts, Watuts) Canola Oil; Jalt (1%) Contains: Peanus Almonds, Cashews, Peanus Brazil Nuts Walnus May contain traces ot Cereak: containing Gluten; Other Tree Nus Sesame Seeds, Lupins Soy' Suphites and Mk Products"""

class ModelTester:
    """Test NER models on noisy text."""
    
    def __init__(self, model_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        # Load config
        config_path = Path(model_path) / "config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding='utf-8'))
            self.id2label = {int(k) if k.isdigit() else k: v for k, v in config.get('id2label', {}).items()}
        else:
            self.id2label = {}
    
    def extract_entities(self, text):
        """Extract allergens from text."""
        enc = self.tokenizer(
            text,
            return_offsets_mapping=True,
            truncation=True,
            max_length=512,
            add_special_tokens=True,
            return_tensors="pt"
        )
        
        input_ids = enc["input_ids"].to(self.device)
        attention_mask = enc["attention_mask"].to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0]
        
        pred_ids = probs.argmax(dim=-1).tolist()
        pred_labels = [self.id2label.get(i, "O") if isinstance(i, int) else i for i in pred_ids]
        
        # Extract allergen spans
        allergens = {}
        current_allergen = None
        current_span = ""
        
        for label in pred_labels:
            if label == "O":
                if current_allergen:
                    if current_allergen not in allergens:
                        allergens[current_allergen] = []
                    allergens[current_allergen].append(current_span.strip())
                current_allergen = None
                current_span = ""
            elif label.startswith("B-"):
                if current_allergen:
                    if current_allergen not in allergens:
                        allergens[current_allergen] = []
                    allergens[current_allergen].append(current_span.strip())
                current_allergen = label[2:]
                current_span = ""
            elif label.startswith("I-"):
                allergen_type = label[2:]
                if not current_allergen:
                    current_allergen = allergen_type
                current_span += " " + allergen_type.lower()
        
        return allergens


def main():
    root = Path(__file__).parent.parent
    
    print("=" * 80)
    print("COMPARING BASELINE vs ROBUST NER MODELS")
    print("=" * 80)
    print()
    print(f"Test OCR Input (garbled): {TEST_OCR[:100]}...")
    print()
    
    # Test baseline model
    baseline_path = root / "models" / "ner_model"
    if baseline_path.exists():
        print("[Test 1] Baseline Model (original training)")
        print(f"Path: {baseline_path}")
        baseline_tester = ModelTester(str(baseline_path))
        baseline_allergens = baseline_tester.extract_entities(TEST_OCR)
        print(f"Allergens detected: {len(baseline_allergens)}")
        for allergen in sorted(baseline_allergens.keys()):
            print(f"  ✓ {allergen}")
        print()
    else:
        print("[Test 1] Baseline model not found")
        print()
    
    # Test robust model
    robust_path = root / "models" / "ner_model_robust_v2" / "final_model"
    if robust_path.exists():
        print("[Test 2] Robust Model (trained on balanced data)")
        print(f"Path: {robust_path}")
        robust_tester = ModelTester(str(robust_path))
        robust_allergens = robust_tester.extract_entities(TEST_OCR)
        print(f"Allergens detected: {len(robust_allergens)}")
        for allergen in sorted(robust_allergens.keys()):
            print(f"  ✓ {allergen}")
        print()
    else:
        print("[Test 2] Robust model not found")
        print()
    
    # Summary
    print("=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    if baseline_path.exists() and robust_path.exists():
        baseline_count = len(baseline_allergens)
        robust_count = len(robust_allergens)
        improvement = robust_count - baseline_count
        
        print(f"Baseline: {baseline_count} allergens")
        print(f"Robust:   {robust_count} allergens")
        print(f"Improvement: {improvement:+d}")
        
        if improvement > 0:
            print(f"\n✅ Robust model detected {improvement} more allergens!")
        elif improvement == 0:
            print("\n→ Both models detected same allergens")
        else:
            print(f"\n⚠️  Baseline detected {-improvement} more allergens")
    
    print()


if __name__ == "__main__":
    main()
