"""
FastAPI endpoint for allergen detection service.
Wraps the complete pipeline into a production-ready REST API.
"""

import sys
import io
import os

# Configure stdout/stderr for UTF-8 on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import time
import tempfile
from pathlib import Path
from typing import Optional, Dict
import numpy as np
import torch
import cv2
from transformers import AutoTokenizer, AutoModelForTokenClassification
from collections import defaultdict

from src.ocr.simple_ocr_engine import SimpleOCREngine
from src.ocr.layout_parser import reconstruct_text
from src.barcode.barcode_detector import BarcodeDetector

# Add access to scripts for advanced cleaning
from pathlib import Path as _PathForImport
import sys as _sys_for_import
_root_dir = _PathForImport(__file__).parent.parent.parent
_sys_for_import.path.insert(0, str(_root_dir / "scripts"))
try:
    from ocr_text_cleaner import OCRTextCleaner, extract_allergen_mentions  # type: ignore
except Exception:
    OCRTextCleaner = None
    extract_allergen_mentions = None

# Initialize FastAPI app
app = FastAPI(
    title="Allergen Detection API",
    description="Detects allergens in product ingredient labels",
    version="1.0.0"
)

# Add CORS middleware to allow Streamlit frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (load once at startup)
model = None
tokenizer = None
ocr_engine = None
barcode_detector = None
allergen_dictionary = None
id2label = None
label2id = None
device = None
text_cleaner = None

@app.on_event("startup")
async def startup_event():
    """Load models and components on startup."""
    global model, tokenizer, ocr_engine, barcode_detector, allergen_dictionary, id2label, label2id, device, text_cleaner

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load paths
    root_dir = Path(__file__).parent.parent.parent
    data_dir = root_dir / "data"
    models_dir = root_dir / "models"

    # Load allergen dictionary
    allergen_path = data_dir / "allergen_dictionary.json"
    with open(allergen_path, 'r') as f:
        allergen_dictionary = json.load(f)

    # Load label mapping
    label_mapping_path = data_dir / "ner_training" / "label_mapping.json"
    with open(label_mapping_path, 'r') as f:
        label_mapping = json.load(f)
    id2label = {int(k): v for k, v in label_mapping.get("id_to_label", {}).items()}
    label2id = label_mapping.get("label_to_id", {})

    # Load NER model
    model_path = models_dir / "ner_model"
    if not model_path.exists():
        experiments = list((models_dir / "experiments").glob("**/pytorch_model.bin"))
        if experiments:
            model_path = experiments[0].parent

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    model = model.to(device).eval()

    # Initialize OCR
    try:
        ocr_engine = SimpleOCREngine(lang_list=["en"], gpu=torch.cuda.is_available())
    except Exception:
        ocr_engine = None

    # Advanced cleaner
    if OCRTextCleaner is not None:
        try:
            text_cleaner = OCRTextCleaner()
        except Exception:
            text_cleaner = None

    # Initialize barcode detector
    try:
        barcode_detector = BarcodeDetector()
        print("[OK] Barcode detector initialized")
    except Exception as e:
        print(f"[WARNING] Barcode detector failed: {e}")
        barcode_detector = None

    print("[OK] API startup complete")

def clean_text(text: str) -> str:
    """Use robust cleaner when available, fallback to basic normalization."""
    if not text:
        return ""
    base = ' '.join(text.split()).replace('_', '').strip()
    if text_cleaner is not None:
        try:
            return text_cleaner.clean(base)
        except Exception:
            return base
    return base

def run_ner_prediction(text: str):
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

    # Group contiguous high-confidence tokens of the same label
    entities = []
    curr_label = None
    start_idx = None
    conf_list = []

    CONF_THRESHOLD = 0.50  # recall-oriented
    for pred, conf, (s, e) in zip(preds, confs, offsets):
        if s == e:
            continue
        label = id2label.get(int(pred))
        high = conf >= CONF_THRESHOLD
        if high and label:
            if curr_label == label and start_idx is not None:
                conf_list.append(conf)
                end_idx = e
            else:
                if curr_label and start_idx is not None and conf_list:
                    span = text[start_idx:end_idx]
                    entities.append((span, curr_label, float(np.mean(conf_list))))
                curr_label = label
                start_idx = s
                end_idx = e
                conf_list = [conf]
        else:
            if curr_label and start_idx is not None and conf_list:
                span = text[start_idx:end_idx]
                entities.append((span, curr_label, float(np.mean(conf_list))))
            curr_label = None
            start_idx = None
            conf_list = []

    if curr_label and start_idx is not None and conf_list:
        span = text[start_idx:end_idx]
        entities.append((span, curr_label, float(np.mean(conf_list))))

    return entities

def map_to_standard_allergens(entities):
    detected = defaultdict(list)
    
    for text_span, label, conf in entities:
        span_lower = text_span.lower().strip()
        matched = False
        
        for allergen_type, synonyms in allergen_dictionary.items():
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

UPPER_TO_LOWER_ALLERGEN = {
    'PEANUT': 'peanut',
    'TREE_NUT': 'tree_nut',
    'MILK': 'milk',
    'GLUTEN': 'gluten',
    'SESAME': 'sesame',
    'SOY': 'soy',
    'FISH': 'fish',
    'SHELLFISH': 'shellfish',
    'EGG': 'egg',
    'MUSTARD': 'mustard',
    'SULPHITES': 'sulfites',
    'CELERY': 'celery',
    'LUPIN': 'lupin',
}

def union_with_dictionary(cleaned_text: str, mapped_from_ner: dict) -> dict:
    """Union dictionary-based findings with NER-mapped results."""
    result = {k: list(v) for k, v in (mapped_from_ner or {}).items()}
    if extract_allergen_mentions is None:
        return result
    try:
        dict_hits = extract_allergen_mentions(cleaned_text)
    except Exception:
        dict_hits = {}
    for up_key, contexts in (dict_hits or {}).items():
        # Keep uppercase keys for consistency with test expectations
        items = result.get(up_key, [])
        for ctx in contexts:
            items.append({'text': ctx, 'label': 'DICTIONARY', 'confidence': 1.0})
        result[up_key] = items
    return result

@app.post("/detect-barcode")
async def detect_barcode(file: UploadFile = File(...)):
    """Detect allergens using barcode scanning (fast path, no OCR needed)."""
    if barcode_detector is None:
        raise HTTPException(status_code=503, detail="Barcode detector not available")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Try quick barcode detection
        result = barcode_detector.quick_detect(tmp_path)
        
        if result:
            # Success - return allergen info from OpenFoodFacts
            detected_allergens = {}
            for allergen in result.get('allergens', []):
                detected_allergens[allergen] = [{
                    'text': result.get('allergen_text', ''),
                    'label': 'BARCODE_LOOKUP',
                    'confidence': 0.95  # High confidence for API data
                }]
            
            return JSONResponse({
                "success": True,
                "source": "barcode",
                "barcode": result['barcode'],
                "product_name": result['name'],
                "brand": result['brand'],
                "detected_allergens": detected_allergens,
                "allergen_count": len(detected_allergens),
                "raw_text": result.get('ingredients', ''),
                "api_url": result.get('url', '')
            })
        else:
            # No barcode found - return empty result
            return JSONResponse({
                "success": True,
                "source": "barcode",
                "barcode": None,
                "message": "No barcode detected in image. Use /detect endpoint with OCR instead.",
                "detected_allergens": {}
            })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "ocr_available": ocr_engine is not None,
        "device": str(device)
    }

@app.post("/detect")
async def detect_allergens(file: UploadFile = File(...), use_ocr: bool = True):
    """Detect allergens in product image."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        result = {
            "success": False,
            "error": None,
            "raw_text": "",
            "cleaned_text": "",
            "detected_allergens": {},
            "avg_confidence": 0.0,
            "timings": {},
            "entities_found": []
        }
        
        try:
            # OCR
            t0 = time.time()
            img = cv2.imread(tmp_path)
            if img is None:
                raise ValueError("Could not read image")
            raw_text = ""
            segments = []
            if use_ocr and ocr_engine:
                # Prefer detailed boxes + layout reconstruction for human-like order
                items = ocr_engine.read_boxes(img)
                if items:
                    parsed = reconstruct_text(items)
                    raw_text = parsed.get("text", "")
                    segments = parsed.get("segments", [])
                else:
                    raw_text = ocr_engine.extract(img)
            result["timings"]["ocr"] = time.time() - t0
            result["raw_text"] = raw_text
            result["segments"] = segments

            # Clean
            t0 = time.time()
            cleaned = clean_text(raw_text)
            result["cleaned_text"] = cleaned
            result["timings"]["cleaning"] = time.time() - t0
            if not cleaned:
                raise ValueError("No text extracted from image")

            # NER
            t0 = time.time()
            entities = run_ner_prediction(cleaned)
            result["entities_found"] = entities
            result["timings"]["ner"] = time.time() - t0

            # Mapping + Union
            t0 = time.time()
            mapped = map_to_standard_allergens(entities)
            merged = union_with_dictionary(cleaned, mapped)
            result["detected_allergens"] = merged
            result["timings"]["mapping"] = time.time() - t0

            # Confidence and totals
            confs = [d['confidence'] for v in merged.values() for d in v]
            result["avg_confidence"] = float(np.mean(confs)) if confs else 0.0
            result["timings"]["total"] = sum(result["timings"].values())
            result["success"] = True
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)

@app.post("/detect-text")
async def detect_allergens_from_text(text: str):
    """Detect allergens from provided text (no OCR)."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        result = {
            "success": False,
            "error": None,
            "raw_text": text,
            "cleaned_text": "",
            "detected_allergens": {},
            "avg_confidence": 0.0,
            "timings": {}
        }

        # Clean
        t0 = time.time()
        cleaned = clean_text(text)
        result["cleaned_text"] = cleaned
        result["timings"]["cleaning"] = time.time() - t0
        if not cleaned:
            raise ValueError("No text provided")

        # NER
        t0 = time.time()
        entities = run_ner_prediction(cleaned)
        result["timings"]["ner"] = time.time() - t0

        # Mapping + Union
        t0 = time.time()
        mapped = map_to_standard_allergens(entities)
        merged = union_with_dictionary(cleaned, mapped)
        result["detected_allergens"] = merged
        result["timings"]["mapping"] = time.time() - t0

        confs = [d['confidence'] for v in merged.values() for d in v]
        result["avg_confidence"] = float(np.mean(confs)) if confs else 0.0
        result["timings"]["total"] = sum(result["timings"].values())
        result["success"] = True
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
