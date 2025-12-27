"""
Batch OCR extractor for all images.
- Parallel processing with checkpoints
- Uses SimpleOCREngine (EasyOCR) with GPU if available
- Outputs consolidated CSV for downstream annotation
"""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional
import cv2
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))  # ensure src is importable
from src.ocr.simple_ocr_engine import SimpleOCREngine
from src.ocr.ocr_postprocessor import clean_text, normalize_ocr_noise

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
OCR_OUT = DATA / "ocr_results"
CHECKPOINT = OCR_OUT / "all_ocr_texts_checkpoint.json"
OUTPUT_CSV = OCR_OUT / "all_ocr_texts.csv"
OUTPUT_FAILED = OCR_OUT / "failed_images.txt"


def load_checkpoint() -> Dict[str, Dict]:
    if CHECKPOINT.exists():
        try:
            return json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_checkpoint(cache: Dict[str, Dict]):
    CHECKPOINT.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def process_image(img_path: Path, engine: SimpleOCREngine) -> Optional[Dict]:
    image = cv2.imread(str(img_path))
    if image is None:
        return None

    text, conf = engine.extract_with_confidence(image)
    text = normalize_ocr_noise(clean_text(text))

    if not text.strip():
        return None

    quality = float(min(1.0, max(conf, len(text) / 120)))  # simple heuristic
    return {
        "image_name": img_path.stem,
        "text": text,
        "confidence": float(conf),
        "quality": quality,
        "text_length": len(text),
    }


def main(max_workers: int = 8, checkpoint_every: int = 200):
    OCR_OUT.mkdir(parents=True, exist_ok=True)

    use_gpu = True
    try:
        import torch
        use_gpu = torch.cuda.is_available()
    except Exception:
        use_gpu = False

    engine = SimpleOCREngine(lang_list=["en"], gpu=use_gpu)

    images = sorted(RAW.glob("*.jpg"))
    if not images:
        print(f"No images found in {RAW}")
        return

    cache = load_checkpoint()
    done = set(cache.keys())

    to_process = [img for img in images if img.stem not in done]
    print(f"Found {len(images)} images, {len(done)} cached, {len(to_process)} to process")
    print(f"GPU: {use_gpu}")

    results: List[Dict] = []
    failed: List[str] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(process_image, img, engine): img for img in to_process}
        for idx, future in enumerate(tqdm(as_completed(future_map), total=len(future_map), desc="OCR")):
            img = future_map[future]
            try:
                output = future.result()
                if output:
                    cache[output["image_name"]] = output
                    results.append(output)
                else:
                    failed.append(img.name)
            except Exception as e:
                failed.append(img.name)

            if (idx + 1) % checkpoint_every == 0:
                save_checkpoint(cache)

    # Save final checkpoint and outputs
    save_checkpoint(cache)

    df = pd.DataFrame(cache.values())
    df.sort_values("image_name", inplace=True)
    df.to_csv(OUTPUT_CSV, index=False)

    if failed:
        OUTPUT_FAILED.write_text("\n".join(sorted(set(failed))), encoding="utf-8")

    print(f"Saved OCR CSV: {OUTPUT_CSV} ({len(df)} rows)")
    print(f"Checkpoint: {CHECKPOINT}")
    if failed:
        print(f"Failed images: {len(failed)} (see {OUTPUT_FAILED})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8, help="Number of parallel workers")
    parser.add_argument("--checkpoint-every", type=int, default=200, help="Save checkpoint every N images")
    args = parser.parse_args()
    main(max_workers=args.workers, checkpoint_every=args.checkpoint_every)
