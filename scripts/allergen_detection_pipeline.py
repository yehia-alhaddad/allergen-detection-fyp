"""
End-to-End Allergen Detection Pipeline.
Image → OCR → Clean → NER → Allergen Report

Handles multiple detection methods:
1. Dictionary-based cleaning + keyword extraction (fast, rule-based)
2. BERT NER model (neural, learned from data)
3. Confidence scoring & multi-pass detection
"""

import json
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from transformers import AutoTokenizer, AutoModelForTokenClassification
from PIL import Image
import sys

# Add scripts to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from ocr_text_cleaner import OCRTextCleaner, extract_allergen_mentions

class AllergenDetectionPipeline:
    """Complete allergen detection from image to report."""
    
    def __init__(self, model_dir: str = None, use_gpu: bool = True):
        self.root = ROOT
        self.device = torch.device("cuda" if (use_gpu and torch.cuda.is_available()) else "cpu")

        # Primary (baseline) model
        self.model_dir = Path(model_dir) if model_dir else self.root / "models" / "ner_model"
        print(f"[Pipeline] Loading baseline model from {self.model_dir}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        self.model = AutoModelForTokenClassification.from_pretrained(self.model_dir).to(self.device)
        self.model.eval()

        # Optional robust model (ensemble)
        self.robust_model_dir = self.root / "models" / "ner_model_robust_v2" / "final_model"
        self.robust_tokenizer = None
        self.robust_model = None
        if self.robust_model_dir.exists():
            print(f"[Pipeline] Loading robust model from {self.robust_model_dir}")
            self.robust_tokenizer = AutoTokenizer.from_pretrained(self.robust_model_dir)
            self.robust_model = AutoModelForTokenClassification.from_pretrained(self.robust_model_dir).to(self.device)
            self.robust_model.eval()

        # Load label map from baseline model
        config_path = self.model_dir / "config.json"
        config = json.loads(config_path.read_text(encoding='utf-8'))
        self.id2label = {int(k): v for k, v in config.get('id2label', {}).items()}

        # Initialize cleaner
        self.cleaner = OCRTextCleaner()

        print(f"[Pipeline] Ready on device: {self.device}")
        print(f"[Pipeline] Found {len(self.id2label)} allergen classes")
    
    def run_ner_model(self, text: str, tokenizer, model, confidence_threshold: float = 0.6, source: str = "ner") -> Dict[str, List[Dict]]:
        """
        Run BERT NER model on text and extract entities with confidence scores.
        Returns: allergen → [{"span": str, "confidence": float, "position": int}, ...]
        """
        # Tokenize
        enc = tokenizer(
            text,
            return_offsets_mapping=True,
            truncation=True,
            max_length=512,
            add_special_tokens=True,
            return_tensors="pt"
        )
        
        input_ids = enc["input_ids"].to(self.device)
        attention_mask = enc["attention_mask"].to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits  # [1, seq_len, num_labels]
            probs = torch.softmax(logits, dim=-1)[0]  # [seq_len, num_labels]
        
        # Extract spans with confidence
        pred_ids = probs.argmax(dim=-1).tolist()
        pred_labels = [self.id2label.get(i, "O") for i in pred_ids]
        token_confs = probs.max(dim=-1).values.tolist()
        offsets = enc["offset_mapping"][0].tolist()
        
        found = {}
        current_span = None
        
        for i, (lab, off, conf) in enumerate(zip(pred_labels, offsets, token_confs)):
            start, end = off
            if start == 0 and end == 0:  # Skip special tokens
                continue
            
            if lab == "O":
                if current_span is not None:
                    allergen = current_span[0]
                    conf_sum = current_span[2]
                    count = current_span[3]
                    start_pos = current_span[5]
                    end_pos = current_span[6]
                    avg_conf = conf_sum / max(count, 1)
                    if avg_conf >= confidence_threshold:
                        if allergen not in found:
                            found[allergen] = []
                        found[allergen].append({
                            "span": text[start_pos:end_pos],
                            "confidence": float(avg_conf),
                            "position": start_pos
                        })
                    current_span = None
            else:
                if lab.startswith("B-") or current_span is None:
                    if current_span is not None:
                        allergen, span_text, conf_sum, count, _, _, _ = current_span
                        avg_conf = conf_sum / max(count, 1)
                        if avg_conf >= confidence_threshold:
                            if allergen not in found:
                                found[allergen] = []
                            found[allergen].append({
                                "span": span_text,
                                "confidence": float(avg_conf),
                                "position": _
                            })
                    
                    allergen = lab.split("-")[1] if "-" in lab else lab
                    current_span = [allergen, text[start:end], conf, 1, lab, start, end]
                elif current_span and (lab == f"I-{current_span[0]}" or lab.startswith("I-")):
                    # Extend span
                    allergen = current_span[0]
                    current_span[1] += text[start:end]
                    current_span[2] += conf
                    current_span[3] += 1
                    current_span[6] = end  # Update end position
        
        # Finalize last span
        if current_span is not None:
            allergen = current_span[0]
            span_text = current_span[1]
            conf_sum = current_span[2]
            count = current_span[3]
            start = current_span[5]
            avg_conf = conf_sum / max(count, 1)
            if avg_conf >= confidence_threshold:
                if allergen not in found:
                    found[allergen] = []
                found[allergen].append({
                    "span": span_text,
                    "confidence": float(avg_conf),
                    "position": start
                })
        
        return found
    
    def detect_allergens(self, text: str, ocr_source: str = "unknown") -> Dict:
        """
        Complete allergen detection using multiple methods (dictionary + ensemble NER).
        Always prioritize dictionary hits and union all model outputs to avoid false negatives.
        """
        original_text = text
        cleaned_text = self.cleaner.clean(text)

        # Method 1: Dictionary-based keyword extraction (recall-first)
        dict_allergens = extract_allergen_mentions(cleaned_text)

        allergen_keyword_map = {
            'PEANUT': ['peanut', 'groundnut', 'arachis'],
            'TREE_NUT': ['almond', 'walnut', 'cashew', 'hazelnut', 'pecan', 'pistachio', 'brazil nut', 'macadamia', 'coconut', 'nut'],
            'MILK': ['milk', 'dairy', 'lactose', 'casein', 'whey', 'cream', 'butter', 'cheese', 'yogurt'],
            'GLUTEN': ['gluten', 'wheat', 'barley', 'rye', 'cereal', 'flour', 'bread', 'pasta', 'noodle', 'oat'],
            'SESAME': ['sesame', 'tahini', 'hummus'],
            'SOY': ['soy', 'soya', 'soybean'],
            'FISH': ['fish', 'anchovy', 'salmon', 'tuna', 'cod'],
            'SHELLFISH': ['shellfish', 'shrimp', 'prawn', 'crab', 'lobster', 'clam', 'oyster', 'mussel', 'scallop'],
            'EGG': ['egg', 'albumen', 'mayonnaise'],
            'MUSTARD': ['mustard', 'dijon'],
            'SULPHITES': ['sulphite', 'sulfite', 'so2', 'preservative'],
            'CELERY': ['celery', 'celeriac'],
            'LUPIN': ['lupin'],
        }

        # Method 2: Baseline NER (lower threshold for recall)
        ner_allergens_baseline = self.run_ner_model(
            cleaned_text,
            tokenizer=self.tokenizer,
            model=self.model,
            confidence_threshold=0.3,
            source="baseline_ner",
        )

        # Method 3: Robust NER (if available)
        ner_allergens_robust = {}
        if self.robust_model and self.robust_tokenizer:
            ner_allergens_robust = self.run_ner_model(
                cleaned_text,
                tokenizer=self.robust_tokenizer,
                model=self.robust_model,
                confidence_threshold=0.3,
                source="robust_ner",
            )

        # Combine results (union, prioritize dictionary, keep max confidence)
        all_allergens = {}

        def add_allergen(source: str, allergen: str, contexts: List[str], confidence: float):
            if allergen not in all_allergens:
                all_allergens[allergen] = {
                    "sources": [],
                    "contexts": [],
                    "method": "union",
                    "confidence": float(confidence),
                }
            all_allergens[allergen]["sources"].append(source)
            # merge contexts without duplicates
            all_allergens[allergen]["contexts"] = list({*all_allergens[allergen]["contexts"], *contexts})
            all_allergens[allergen]["confidence"] = max(all_allergens[allergen]["confidence"], float(confidence))

        # Add dictionary findings (confidence = 1.0, rule-based)
        for allergen, contexts in dict_allergens.items():
            add_allergen("dictionary", allergen, contexts, 1.0)

        # Add baseline NER findings
        for allergen, detections in ner_allergens_baseline.items():
            avg_conf = np.mean([d["confidence"] for d in detections]) if detections else 0.0
            # Filter spurious labels if no keyword evidence in text
            if allergen in allergen_keyword_map:
                if (not any(k in cleaned_text for k in allergen_keyword_map[allergen])) and (allergen not in dict_allergens):
                    continue
            add_allergen("baseline_ner", allergen, [d["span"] for d in detections], avg_conf)

        # Add robust NER findings
        for allergen, detections in ner_allergens_robust.items():
            avg_conf = np.mean([d["confidence"] for d in detections]) if detections else 0.0
            if allergen in allergen_keyword_map:
                if (not any(k in cleaned_text for k in allergen_keyword_map[allergen])) and (allergen not in dict_allergens):
                    continue
            add_allergen("robust_ner", allergen, [d["span"] for d in detections], avg_conf)

        # Build report
        report = {
            "ocr_source": ocr_source,
            "original_length": len(original_text),
            "cleaned_length": len(cleaned_text),
            "allergens_found": len(all_allergens),
            "allergens": all_allergens,
            "timestamp": str(Path.cwd()),
            "model_confidence_threshold": 0.2,
            "detectors_used": [
                src for src in ["dictionary", "baseline_ner", "robust_ner" if self.robust_model else None] if src
            ],
        }

        return report
    
    def format_report(self, report: Dict) -> str:
        """Pretty-print allergen report."""
        output = []
        output.append("\n" + "=" * 80)
        output.append("ALLERGEN DETECTION REPORT")
        output.append("=" * 80)
        output.append(f"OCR Source: {report['ocr_source']}")
        output.append(f"Text Length: {report['original_length']} -> {report['cleaned_length']} (cleaned)")
        output.append(f"Allergens Detected: {report['allergens_found']}")
        
        if report['allergens_found'] == 0:
            output.append("\n[OK] NO ALLERGENS DETECTED")
        else:
            output.append("\n[!] ALLERGENS FOUND:")
            for allergen, data in sorted(report['allergens'].items()):
                confidence = data.get('confidence', 0.0)
                sources = ", ".join(data.get('sources', []))
                output.append(f"\n  [{confidence:.1%}] {allergen}")
                output.append(f"       Sources: {sources}")
                if data.get('contexts'):
                    for ctx in data['contexts'][:2]:
                        output.append(f"       Context: ...{ctx}...")
        
        output.append("\n" + "=" * 80)
        return "\n".join(output)


def main():
    # Test on the problematic OCR text
    test_ocr_text = """MulheluFUNMAULL SERVES PER PACK 20 SERVE SIZE 25g Avg: Per Avg Per Serve 100g 619kJ 2475kJ Energy Protien 6.5g 25.9g Fat; Total 121g 48.2g Saturated Fat 0.Tg 2.8g Carbohydrate 21g 8.5g Sugars 1.4g 5.4g Sodium S1mg 202mg Ingredients: Mixed Muts (989) Peanuts, Almonds Cashews; Peatats Skin-On Brazi Muts, Watuts) Canola Oil; Jalt (1%) Contains: Peanus Almonds, Cashews, Peanus Brazil Nuts Walnus May contain traces ot Cereak: containing Gluten; Other Tree Nus Sesame Seeds, Lupins Soy' Suphites and Mk Products"""
    
    print("[Main] Initializing pipeline...")
    pipeline = AllergenDetectionPipeline()
    
    print("[Main] Running detection...")
    report = pipeline.detect_allergens(test_ocr_text, ocr_source="test_image.jpg")
    
    print(pipeline.format_report(report))
    
    # Save report
    report_path = ROOT / "results" / "allergen_report_test.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\n[Main] Report saved to {report_path}")


if __name__ == "__main__":
    main()
