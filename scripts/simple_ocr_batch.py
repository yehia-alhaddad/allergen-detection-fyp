"""
Simplified OCR extractor focused on quality over complexity.
Uses minimal preprocessing and relies on EasyOCR's built-in capabilities.
"""
from pathlib import Path
import sys
import cv2
import numpy as np

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from ocr.easyocr_extractor import EasyOCREngine
from ocr.ocr_postprocessor import clean_text, normalize_ocr_noise

def simple_preprocess(image: np.ndarray) -> np.ndarray:
    """Minimal preprocessing - just ensure grayscale and slight contrast boost."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Very light CLAHE - don't over-process
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    return enhanced

# Initialize with simpler settings
engine = EasyOCREngine(
    lang_list=['en'],
    gpu=False,
    contrast_ths=0.5,  # Less aggressive
    adjust_contrast=0.5,  # Less aggressive
    mag_ratio=1.0,  # No magnification distortion
)

RAW = ROOT / 'data' / 'raw'
OUT = ROOT / 'data' / 'ocr_results' / 'cleaned_text'
OUT.mkdir(parents=True, exist_ok=True)

images = sorted(RAW.glob('*.jpg'))
print(f"Found {len(images)} images")
print("Using SIMPLIFIED approach: minimal preprocessing + standard EasyOCR")
print()

written = 0
skipped = 0

for i, img_path in enumerate(images, start=1):
    try:
        img = cv2.imread(str(img_path))
        if img is None:
            skipped += 1
            continue
        
        # Try original image first (EasyOCR often works best on originals)
        raw_text = engine.extract(img)
        cleaned = normalize_ocr_noise(clean_text(raw_text))
        
        # If too short or poor, try with light preprocessing
        if len(cleaned) < 20:
            preprocessed = simple_preprocess(img)
            raw_text = engine.extract(preprocessed)
            cleaned = normalize_ocr_noise(clean_text(raw_text))
        
        # Save if we got anything useful
        if len(cleaned) >= 1:
            out_file = OUT / f"{img_path.stem}.txt"
            out_file.write_text(cleaned, encoding='utf-8')
            written += 1
        else:
            skipped += 1
        
        if i % 50 == 0:
            print(f"Processed {i}/{len(images)} | Written: {written} | Skipped: {skipped}")
    
    except Exception as e:
        print(f"Error on {img_path.name}: {e}")
        skipped += 1
        continue

print(f"\nDone!")
print(f"  Written: {written}")
print(f"  Skipped: {skipped}")
print(f"  Output: {OUT}")
