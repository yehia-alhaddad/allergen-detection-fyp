"""
Prepare training data for NER model using full OCR outputs.
- Consumes consolidated OCR CSV from batch_ocr_all_images.py
- Builds annotation template and summary stats
"""

import json
from pathlib import Path
from typing import List
import pandas as pd

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
OCR_CSV = DATA / "ocr_results" / "all_ocr_texts.csv"
NER_DIR = DATA / "ner_training"
ANNOTATIONS_CSV = DATA / "annotations.csv"

NER_DIR.mkdir(parents=True, exist_ok=True)

LABELS = [
    "GLUTEN", "MILK", "EGG", "PEANUT", "TREE_NUT", "SOY", "FISH",
    "SHELLFISH", "SESAME", "MUSTARD", "CELERY", "SULFITES"
]


def attach_metadata(ocr_df: pd.DataFrame, meta_df: pd.DataFrame) -> pd.DataFrame:
    meta_df = meta_df.rename(columns={"filename": "source"})
    ocr_df["product_name"] = ""
    ocr_df["allergens"] = ""
    for _, row in meta_df.iterrows():
        fname = str(row.get("source", ""))
        allergens = str(row.get("allergens", ""))
        product = str(row.get("product_name", ""))
        matches = ocr_df[ocr_df["image_name"].str.contains(Path(fname).stem, na=False)]
        ocr_df.loc[matches.index, "allergens"] = allergens
        ocr_df.loc[matches.index, "product_name"] = product
    return ocr_df


def build_annotation_template(df: pd.DataFrame, top_n: int = 500, min_len: int = 20) -> List[dict]:
    template = []
    df = df[df["text"].astype(str).str.len() >= min_len]
    df = df.sort_values(["quality", "text_length"], ascending=False)
    for _, row in df.head(top_n).iterrows():
        allergens_list = [a.strip() for a in str(row.get("allergens", "")).split(",") if a.strip()]
        template.append({
            "text": str(row["text"]),
            "image_name": str(row["image_name"]),
            "product_name": str(row.get("product_name", "")),
            "declared_allergens": allergens_list,
            "entities": []
        })
    return template


def main():
    print("=" * 80)
    print("NER TRAINING DATA PREPARATION (FULL DATA)")
    print("=" * 80)

    if not OCR_CSV.exists():
        raise FileNotFoundError(f"Missing OCR CSV at {OCR_CSV}. Run batch_ocr_all_images.py first.")

    ocr_df = pd.read_csv(OCR_CSV)
    print(f"Loaded OCR results: {len(ocr_df)} rows from {OCR_CSV}")

    if ANNOTATIONS_CSV.exists():
        meta_df = pd.read_csv(ANNOTATIONS_CSV)
        ocr_df = attach_metadata(ocr_df, meta_df)
        print(f"Attached metadata from annotations.csv ({len(meta_df)} rows)")

    # Filter unusable text
    ocr_df = ocr_df[ocr_df["text"].astype(str).str.len() >= 5]
    ocr_df["text_length"] = ocr_df["text"].astype(str).str.len()

    # Save trimmed CSV for annotation
    trimmed_csv = NER_DIR / "ocr_texts_for_annotation.csv"
    ocr_df.to_csv(trimmed_csv, index=False)
    print(f"Saved trimmed OCR data to {trimmed_csv}")

    # Build annotation template
    template = build_annotation_template(ocr_df, top_n=500, min_len=20)
    template_path = NER_DIR / "annotation_template.json"
    template_path.write_text(json.dumps(template, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Annotation template: {len(template)} samples → {template_path}")

    # Label mapping
    label_map = {
        "labels": LABELS,
        "label_to_id": {lbl: i for i, lbl in enumerate(LABELS)},
        "id_to_label": {i: lbl for i, lbl in enumerate(LABELS)},
    }
    (NER_DIR / "label_mapping.json").write_text(json.dumps(label_map, indent=2), encoding="utf-8")

    # Summary
    summary = {
        "total_rows": int(len(ocr_df)),
        "avg_text_length": float(ocr_df["text_length"].mean()),
        "median_text_length": float(ocr_df["text_length"].median()),
        "template_size": len(template),
        "status": "Ready for annotation"
    }
    (NER_DIR / "data_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\nNext:")
    print("  1) Run auto_annotation_suggester.py to get BIO suggestions")
    print("  2) Validate with annotation_quality_checker.py")
    print("  3) Finalize train/val/test splits")
    print("=" * 80)


if __name__ == "__main__":
    main()
