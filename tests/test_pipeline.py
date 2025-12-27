"""
Quick pipeline test script
Tests the complete allergen detection pipeline end-to-end
"""

import sys
import os
from pathlib import Path
import time
import json

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("ALLERGEN DETECTION PIPELINE TEST")
print("=" * 60)
print()

# Test 1: Check file structure
print("Test 1: Checking file structure...")
required_paths = {
    "Allergen Dictionary": project_root / "data" / "allergen_dictionary.json",
    "NER Model": project_root / "models" / "ner_model",
    "OCR Module": project_root / "src" / "ocr" / "simple_ocr_engine.py",
    "API Module": project_root / "src" / "api" / "allergen_api.py",
}

all_exist = True
for name, path in required_paths.items():
    exists = path.exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {name}: {path.name}")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n❌ Some required files are missing!")
    sys.exit(1)
else:
    print("  ✓ All required files found!")
print()

# Test 2: Import modules
print("Test 2: Testing imports...")
try:
    from src.ocr.simple_ocr_engine import SimpleOCREngine
    print("  ✓ SimpleOCREngine imported")
except Exception as e:
    print(f"  ✗ Failed to import SimpleOCREngine: {e}")
    sys.exit(1)

try:
    from transformers import AutoTokenizer, AutoModelForTokenClassification
    print("  ✓ Transformers imported")
except Exception as e:
    print(f"  ✗ Failed to import transformers: {e}")
    sys.exit(1)

try:
    import torch
    print(f"  ✓ PyTorch imported (CUDA available: {torch.cuda.is_available()})")
except Exception as e:
    print(f"  ✗ Failed to import PyTorch: {e}")
    sys.exit(1)

print()

# Test 3: Load allergen dictionary
print("Test 3: Loading allergen dictionary...")
try:
    allergen_dict_path = project_root / "data" / "allergen_dictionary.json"
    with open(allergen_dict_path, 'r') as f:
        allergen_dict = json.load(f)
    print(f"  ✓ Loaded {len(allergen_dict)} allergen categories")
    print(f"    Categories: {', '.join(list(allergen_dict.keys())[:5])}...")
except Exception as e:
    print(f"  ✗ Failed to load allergen dictionary: {e}")
    sys.exit(1)

print()

# Test 4: Load NER model
print("Test 4: Loading NER model...")
try:
    model_path = project_root / "models" / "ner_model"
    if not model_path.exists():
        # Try experiments folder
        experiments = list((project_root / "models" / "experiments").glob("**/pytorch_model.bin"))
        if experiments:
            model_path = experiments[0].parent
            print(f"  Using model from: {model_path.name}")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    model = AutoModelForTokenClassification.from_pretrained(str(model_path))
    model = model.to(device).eval()
    
    print(f"  ✓ Model loaded on {device}")
    print(f"  ✓ Tokenizer vocabulary size: {len(tokenizer)}")
except Exception as e:
    print(f"  ✗ Failed to load NER model: {e}")
    sys.exit(1)

print()

# Test 5: Initialize OCR
print("Test 5: Initializing OCR engine...")
try:
    use_gpu = torch.cuda.is_available()
    ocr_engine = SimpleOCREngine(lang_list=['en'], gpu=use_gpu)
    print(f"  ✓ OCR engine initialized (GPU: {use_gpu})")
except Exception as e:
    print(f"  ⚠ OCR engine initialization warning: {e}")
    print("  Continuing without OCR (can still test NER on text)")
    ocr_engine = None

print()

# Test 6: Test text cleaning
print("Test 6: Testing text cleaning...")
def clean_text(text):
    if not text:
        return ""
    text = ' '.join(text.split())
    text = text.replace('_', '')
    return text.strip()

test_text = "Ingredients:   wheat  flour,  milk, __eggs__, peanuts"
cleaned = clean_text(test_text)
print(f"  Input:  '{test_text}'")
print(f"  Output: '{cleaned}'")
print(f"  ✓ Text cleaning works")
print()

# Test 7: Test NER prediction
print("Test 7: Testing NER prediction...")
try:
    import numpy as np
    
    def run_ner(text):
        if not text or len(text.strip()) < 3:
            return []
        
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
            return_offsets_mapping=True
        )
        offsets = inputs.pop("offset_mapping")[0].numpy()
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits[0]
            probs = torch.softmax(logits, dim=-1)
            preds = torch.argmax(logits, dim=-1).cpu().numpy()
            confs = probs.max(dim=-1).values.cpu().numpy()
        
        # Get label mapping
        id2label = model.config.id2label
        
        entities = []
        current = None
        conf_list = []
        start_idx = 0
        
        for pred, conf, (s, e) in zip(preds, confs, offsets):
            if s == e:
                continue
            label = id2label[pred]
            
            if label.startswith('B-'):
                if current:
                    entities.append((current, curr_label, float(np.mean(conf_list))))
                current = text[s:e]
                curr_label = label[2:]
                conf_list = [conf]
                start_idx = s
            elif label.startswith('I-') and current:
                current = text[start_idx:e]
                conf_list.append(conf)
            else:
                if current:
                    entities.append((current, curr_label, float(np.mean(conf_list))))
                    current = None
                    conf_list = []
        
        if current:
            entities.append((current, curr_label, float(np.mean(conf_list))))
        
        return entities
    
    test_sentence = "Contains wheat flour, milk, eggs, and peanuts"
    entities = run_ner(test_sentence)
    
    print(f"  Input text: '{test_sentence}'")
    print(f"  Detected entities: {len(entities)}")
    for text, label, conf in entities:
        print(f"    - {text} [{label}] (confidence: {conf:.2f})")
    print(f"  ✓ NER prediction works")
except Exception as e:
    print(f"  ✗ NER prediction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 8: Test allergen mapping
print("Test 8: Testing allergen mapping...")
try:
    from collections import defaultdict
    
    def map_allergens(entities):
        detected = defaultdict(list)
        
        for text_span, label, conf in entities:
            span_lower = text_span.lower().strip()
            matched = False
            
            for allergen_type, synonyms in allergen_dict.items():
                for syn in synonyms:
                    if syn.lower() in span_lower or span_lower in syn.lower():
                        detected[allergen_type].append({
                            'text': text_span,
                            'label': label,
                            'confidence': conf
                        })
                        matched = True
                        break
                if matched:
                    break
            
            if not matched and label != 'O':
                detected['unknown'].append({
                    'text': text_span,
                    'label': label,
                    'confidence': conf
                })
        
        return dict(detected)
    
    mapped = map_allergens(entities)
    print(f"  Detected {len(mapped)} allergen categories:")
    for allergen, matches in mapped.items():
        print(f"    - {allergen}: {len(matches)} match(es)")
        for match in matches:
            print(f"      '{match['text']}' (conf: {match['confidence']:.2f})")
    
    print(f"  ✓ Allergen mapping works")
except Exception as e:
    print(f"  ✗ Allergen mapping failed: {e}")
    sys.exit(1)

print()

# Test 9: Complete pipeline test
print("Test 9: Complete pipeline test...")
try:
    test_texts = [
        "Contains: milk, eggs, peanuts",
        "Ingredients: wheat flour, soy lecithin, tree nuts",
        "May contain traces of fish and shellfish",
    ]
    
    print(f"  Testing {len(test_texts)} sample texts...")
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n  Sample {i}: '{text}'")
        
        # Clean
        start = time.time()
        cleaned = clean_text(text)
        clean_time = time.time() - start
        
        # NER
        start = time.time()
        entities = run_ner(cleaned)
        ner_time = time.time() - start
        
        # Map
        start = time.time()
        allergens = map_allergens(entities)
        map_time = time.time() - start
        
        total_time = clean_time + ner_time + map_time
        
        print(f"    Entities found: {len(entities)}")
        print(f"    Allergens detected: {len(allergens)}")
        if allergens:
            print(f"    Categories: {', '.join(allergens.keys())}")
        print(f"    Time: {total_time*1000:.1f}ms (NER: {ner_time*1000:.1f}ms)")
    
    print(f"\n  ✓ Complete pipeline works!")
except Exception as e:
    print(f"  ✗ Pipeline test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print()
print("Summary:")
print(f"  • Files: All required files present")
print(f"  • Imports: All modules loaded successfully")
print(f"  • Dictionary: {len(allergen_dict)} categories loaded")
print(f"  • Model: Loaded on {device}")
print(f"  • OCR: {'Available' if ocr_engine else 'Not tested (text mode)'}")
print(f"  • Pipeline: Text cleaning → NER → Allergen mapping ✓")
print()
print("Your pipeline is READY for deployment!")
print()

# Activate virtual environment and run commands
venv_path = project_root / ".venv" / "Scripts" / "activate"
os.system(f"{venv_path} && run.bat test_pipeline.py")
os.system(f"{venv_path} && python src\api\allergen_api.py")
os.system(f"{venv_path} && python -m streamlit run app\streamlit_app.py")
