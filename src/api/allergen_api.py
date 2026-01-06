"""
FastAPI endpoint for allergen detection service.
Wraps the complete pipeline into a production-ready REST API.
"""

import sys
import io
import os

# Disable slow huggingface metadata checks on Windows
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['HUGGINGFACE_HUB_CACHE'] = str(os.path.expanduser('~/.cache/huggingface'))

# Disable PyTorch JIT compilation to avoid slow imports on Windows
os.environ['TORCH_JIT'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

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

# Import heavy dependencies LAZILY during startup, not at module load time
# This allows the FastAPI server to start immediately without waiting for transformers/torch
import numpy as np
import cv2

from collections import defaultdict

# Lazy imports - will be loaded in startup_event
SimpleOCREngine = None
reconstruct_text = None
OCRTextCleaner = None
extract_allergen_mentions = None
enhance_allergen_detection = None
format_enhanced_for_response = None

# Note: StrictAllergenDetector will be imported in startup_event

# Initialize FastAPI app
app = FastAPI(
    title="Allergen Detection API",
    description="Detects allergens in product ingredient labels",
    version="1.0.0"
)

# Add CORS middleware to allow web frontend requests
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
allergen_dictionary = None
id2label = None
label2id = None
device = None
text_cleaner = None
torch = None  # Will be imported in startup
strict_detector = None  # New strict allergen detector

@app.on_event("startup")
async def startup_event():
    """Load models and components on startup."""
    global model, tokenizer, ocr_engine, allergen_dictionary, id2label, label2id, device, text_cleaner
    global torch
    global SimpleOCREngine, reconstruct_text, OCRTextCleaner, extract_allergen_mentions
    global strict_detector, enhance_allergen_detection, format_enhanced_for_response
    global init_db, save_detection_result

    # CRITICAL: Import torch and transformers INSIDE startup, not at module level
    # This allows server to start immediately without waiting for heavy imports
    print("[INFO] Loading torch and transformers libraries...")
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForTokenClassification
    except ImportError as e:
        print(f"[ERROR] Failed to import torch/transformers: {e}")
        return

    # Import OCR modules (these have slow pandas imports)
    print("[INFO] Loading OCR modules...")
    try:
        from src.ocr.simple_ocr_engine import SimpleOCREngine
        from src.ocr.layout_parser import reconstruct_text
    except ImportError as e:
        print(f"[ERROR] Failed to import OCR modules: {e}")
        return

    # Import text cleaner
    try:
        from pathlib import Path as _PathForImport
        import sys as _sys_for_import
        _root_dir = _PathForImport(__file__).parent.parent.parent
        _sys_for_import.path.insert(0, str(_root_dir / "scripts"))
        from ocr_text_cleaner import OCRTextCleaner, extract_allergen_mentions  # type: ignore
    except Exception as e:
        print(f"[WARN] Could not load text cleaner: {e}")
        OCRTextCleaner = None
        extract_allergen_mentions = None

    # Import enhanced detector functions for Gemini AI
    try:
        from src.allergen_detection.enhanced_detector import (
            enhance_allergen_detection as enhance_fn,
            format_enhanced_for_response as format_fn
        )
        enhance_allergen_detection = enhance_fn
        format_enhanced_for_response = format_fn
        print("[OK] Enhanced detector (Gemini AI) functions loaded")
    except Exception as e:
        print(f"[WARN] Could not load enhanced detector: {e}")
        enhance_allergen_detection = None
        format_enhanced_for_response = None

    # Import database helpers
    try:
        from src.db import init_db as _init_db, save_detection_result as _save_detection_result
        init_db = _init_db
        save_detection_result = _save_detection_result
        init_db()
        print("[OK] Database initialized")
    except Exception as e:
        print(f"[WARN] Database initialization failed: {e}")
        init_db = None
        save_detection_result = None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[INFO] Using device: {device}")

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

    print(f"[INFO] Loading NER model from {model_path}...")
    print("[INFO] Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    print("[INFO] Loading model...")
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    print(f"[INFO] Moving model to {device}...")
    try:
        # Set a timeout for GPU operations - if it hangs, use CPU instead
        import signal
        def timeout_handler(signum, frame):
            print("[WARN] GPU model.to(device) timed out, using CPU fallback")
            raise TimeoutError("GPU operation timeout")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(15)  # 15 second timeout
        try:
            model = model.to(device).eval()
            signal.alarm(0)  # Cancel alarm if successful
        except TimeoutError:
            print("[WARN] Falling back to CPU")
            device = torch.device("cpu")
            model = model.to(device).eval()
    except Exception as e:
        print(f"[WARN] Could not move model to {device}, using CPU: {e}")
        device = torch.device("cpu")
        model = model.to(device).eval()
    print(f"[OK] NER model loaded")

    # Initialize OCR
    try:
        print("[INFO] Initializing OCR engine...")
        ocr_engine = SimpleOCREngine(lang_list=["en"], gpu=torch.cuda.is_available())
        print("[OK] OCR engine initialized")
    except Exception as e:
        print(f"[WARN] OCR initialization failed: {e}")
        ocr_engine = None

    # Advanced cleaner
    if OCRTextCleaner is not None:
        try:
            print("[INFO] Loading text cleaner...")
            text_cleaner = OCRTextCleaner()
            print("[OK] Text cleaner loaded")
        except Exception as e:
            print(f"[WARN] Text cleaner initialization failed: {e}")
            text_cleaner = None

    # Initialize strict detector
    try:
        print("[INFO] Initializing strict allergen detector...")
        from src.allergen_detection.strict_detector import StrictAllergenDetector
        strict_detector = StrictAllergenDetector()
        print("[OK] Strict allergen detector initialized")
    except Exception as e:
        print(f"[WARN] Strict detector initialization failed: {e}")
        strict_detector = None

    print("[OK] API startup complete - ready for inference")

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
    
    print(f"[INFO] /detect called: file={file.filename}, use_ocr={use_ocr}")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        print(f"[DEBUG] Image saved to {tmp_path}")
        
        result = {
            "success": False,
            "error": None,
            "allergen_detection": {},
            "detected_allergens": {},
            "avg_confidence": 0.0,
            "timings": {}
        }
        
        try:
            # OCR
            print("[DEBUG] Starting OCR...")
            t0 = time.time()
            img = cv2.imread(tmp_path)
            if img is None:
                raise ValueError("Could not read image. Please try to upload a different image or ensure the image shows ingredient label clearly.")
            raw_text = ""
            segments = []
            if use_ocr and ocr_engine:
                print(f"[DEBUG] Using OCR engine to extract text...")
                # Prefer detailed boxes + layout reconstruction for human-like order
                items = ocr_engine.read_boxes(img)
                if items:
                    parsed = reconstruct_text(items)
                    raw_text = parsed.get("text", "")
                    segments = parsed.get("segments", [])
                else:
                    raw_text = ocr_engine.extract(img)
            result["timings"]["ocr"] = time.time() - t0

            # Clean
            print("[DEBUG] Cleaning text...")
            t0 = time.time()
            cleaned = clean_text(raw_text)
            result["timings"]["cleaning"] = time.time() - t0
            if not cleaned:
                raise ValueError("Image does not appear to contain ingredient text. Please try uploading a product image with visible ingredient labels or ingredient text.")
            print(f"[DEBUG] Text cleaned: length={len(cleaned)}")

            # Strict Allergen Detection (new explainable detection)
            print("[DEBUG] Running strict allergen detection...")
            t0 = time.time()
            if strict_detector is None:
                raise ValueError("Allergen detector not initialized")
            
            detection_result = strict_detector.detect(cleaned)
            result["timings"]["detection"] = time.time() - t0
            
            # Use basic formatting (offline mode - no Gemini)
            print("[INFO] Using basic formatting (Gemini AI disabled for offline mode)...")
            formatted = {}
            formatted['contains'] = [
                {
                    'allergen': a.name,
                    'evidence': a.evidence,
                    'keyword': a.matched_keyword,
                    'confidence': round(a.confidence, 2)
                }
                for a in detection_result['contains']
            ]
            formatted['may_contain'] = [
                {
                    'allergen': a.name,
                    'evidence': a.evidence,
                    'keyword': a.matched_keyword,
                    'confidence': round(a.confidence, 2)
                }
                for a in detection_result['may_contain']
            ]
            formatted['not_detected'] = [a.name for a in detection_result['not_detected']]
            formatted['summary'] = {
                'contains_count': len(detection_result['contains']),
                'may_contain_count': len(detection_result['may_contain']),
                'total_detected': len(detection_result['contains']) + len(detection_result['may_contain'])
            }
            result["allergen_detection"] = formatted
            
            # For backward compatibility, also provide old format
            allergen_detection = result["allergen_detection"]
            detected_allergens = {}
            for allergen in allergen_detection.get('contains', []) + allergen_detection.get('may_contain', []):
                allergen_name = allergen['allergen']
                detected_allergens[allergen_name] = [{
                    'text': allergen.get('evidence', ''),
                    'label': 'STRICT_DETECTOR',
                    'confidence': allergen.get('confidence', 0),
                    'category': allergen.get('category', 'UNKNOWN'),
                    'keyword': allergen.get('keyword', ''),
                    'cleaned_text': allergen.get('cleaned_trigger_phrase', ''),
                    'health_recommendation': allergen.get('health_recommendation', {})
                }]
            result["detected_allergens"] = detected_allergens

            # Persist detection result
            try:
                if save_detection_result is not None:
                    save_detection_result(
                        allergen_detection=result["allergen_detection"],
                        raw_text=raw_text,
                        cleaned_text=cleaned,
                        timings=result.get("timings", {}),
                        source="image",
                    )
            except Exception as e:
                print(f"[WARN] Failed to persist detection result: {e}")
            
            print(f"[DEBUG] Detection complete: contains={len(allergen_detection.get('contains', []))}, may_contain={len(allergen_detection.get('may_contain', []))}")

            # Timings and totals
            result["timings"]["total"] = sum(result["timings"].values())
            result["success"] = True
            print(f"[INFO] /detect success: took {result['timings']['total']:.2f}s")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        return JSONResponse(result)
    except Exception as e:
        print(f"[ERROR] /detect failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)

@app.post("/detect-text")
async def detect_allergens_from_text(text: str):
    """Detect allergens from provided text (no OCR)."""
    if strict_detector is None:
        raise HTTPException(status_code=503, detail="Allergen detector not loaded")

    try:
        result = {
            "success": False,
            "error": None,
            "allergen_detection": {},
            "detected_allergens": {},
            "avg_confidence": 0.0,
            "timings": {}
        }

        # Clean text
        t0 = time.time()
        cleaned = clean_text(text)
        result["timings"]["cleaning"] = time.time() - t0
        if not cleaned:
            raise ValueError("No text provided")

        # Strict Allergen Detection (new explainable detection)
        t0 = time.time()
        detection_result = strict_detector.detect(cleaned)
        result["timings"]["detection"] = time.time() - t0
        
        # Format results without Gemini enhancement (offline mode)
        formatted = {}
        formatted['contains'] = [
            {
                'allergen': a.name,
                'evidence': a.evidence,
                'keyword': a.matched_keyword,
                'confidence': round(a.confidence, 2)
            }
            for a in detection_result['contains']
        ]
        formatted['may_contain'] = [
            {
                'allergen': a.name,
                'evidence': a.evidence,
                'keyword': a.matched_keyword,
                'confidence': round(a.confidence, 2)
            }
            for a in detection_result['may_contain']
        ]
        formatted['not_detected'] = [a.name for a in detection_result['not_detected']]
        formatted['summary'] = {
            'contains_count': len(detection_result['contains']),
            'may_contain_count': len(detection_result['may_contain']),
            'total_detected': len(detection_result['contains']) + len(detection_result['may_contain'])
        }
        result["allergen_detection"] = formatted
        
        # For backward compatibility, also provide old format
        allergen_detection = result["allergen_detection"]
        detected_allergens = {}
        for allergen in allergen_detection.get('contains', []) + allergen_detection.get('may_contain', []):
            allergen_name = allergen['allergen']
            detected_allergens[allergen_name] = [{
                'text': allergen.get('evidence', ''),
                'label': 'STRICT_DETECTOR',
                'confidence': allergen.get('confidence', 0),
                'category': allergen.get('category', 'UNKNOWN'),
                'keyword': allergen.get('keyword', ''),
                'cleaned_text': allergen.get('cleaned_trigger_phrase', ''),
                'health_recommendation': allergen.get('health_recommendation', {})
            }]
        result["detected_allergens"] = detected_allergens
        result["timings"]["detection"] = time.time() - t0
        
        # For backward compatibility, also provide old format
        detected_allergens = {}
        for allergen in formatted['contains'] + formatted['may_contain']:
            allergen_name = allergen['allergen']
            detected_allergens[allergen_name] = [{
                'text': allergen['evidence'],
                'label': 'STRICT_DETECTOR',
                'confidence': allergen['confidence'],
                'category': 'CONTAINS' if allergen in formatted['contains'] else 'MAY_CONTAIN',
                'keyword': allergen['keyword']
            }]
        result["detected_allergens"] = detected_allergens

        # Persist detection result for text-only input
        try:
            if save_detection_result is not None:
                save_detection_result(
                    allergen_detection=result["allergen_detection"],
                    raw_text=result.get("raw_text", ""),
                    cleaned_text=result.get("cleaned_text", ""),
                    timings=result.get("timings", {}),
                    source="text",
                )
        except Exception as e:
            print(f"[WARN] Failed to persist detection result: {e}")
        
        confs = [allergen['confidence'] for allergen in formatted['contains'] + formatted['may_contain']]
        result["avg_confidence"] = float(np.mean(confs)) if confs else 0.0
        result["timings"]["total"] = sum(result["timings"].values())
        result["success"] = True
        print(f"[INFO] /detect-text success: contains={len(formatted['contains'])}, may_contain={len(formatted['may_contain'])}")
        return JSONResponse(result)
    except Exception as e:
        print(f"[ERROR] /detect-text failed: {type(e).__name__}: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
