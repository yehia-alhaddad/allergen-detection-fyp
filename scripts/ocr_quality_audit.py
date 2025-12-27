"""
Audit OCR text quality in cleaned_text and export metrics.
"""
from pathlib import Path
import csv
import sys
import re

ROOT = Path(__file__).parent.parent
CLEANED = ROOT / 'data' / 'ocr_results' / 'cleaned_text'
OUT = ROOT / 'results' / 'ocr_comparison' / 'quality_audit.csv'

sys.path.insert(0, str(ROOT / 'src'))
def normalize_ocr_noise(text: str) -> str:
    import re as _re
    text = text or ""
    def _fix_token(tok: str) -> str:
        if not tok:
            return tok
        if tok.isupper():
            tok = tok.replace("0", "O").replace("1", "I").replace("4", "A").replace("5", "S")
        tok = tok.replace("COCOH", "COCOA")
        tok = tok.replace("CHEGOEA", "CHEESE")
        tok = tok.replace("WTLRE", "WATER")
        return tok
    tokens = [
        _fix_token(t)
        for t in _re.split(r"(\s+)", text)
    ]
    return "".join(tokens)

def quality_score(text: str) -> float:
    import re as _re
    text = text or ""
    if not text:
        return 0.0
    total = len(text)
    alpha = sum(1 for c in text if c.isalpha())
    alpha_ratio = alpha / total if total else 0.0
    tokens = [t for t in _re.split(r"\s+", text) if t]
    common_vocab = {
        "ingredients", "contains", "may", "milk", "wheat", "egg", "soy", "peanut",
        "tree", "nut", "fish", "shellfish", "sesame", "mustard", "celery", "sulfites",
        "water", "salt", "sugar", "oil", "cocoa", "chocolate"
    }
    lower_tokens = [t.lower() for t in tokens]
    hits = sum(1 for t in lower_tokens if t in common_vocab)
    vocab_ratio = hits / (len(tokens) or 1)
    return (alpha_ratio * 0.7) + (vocab_ratio * 0.3)

OUT.parent.mkdir(parents=True, exist_ok=True)

rows = []
for p in sorted(CLEANED.glob('*.txt')):
    try:
        text = p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        text = ''
    norm = normalize_ocr_noise(text)
    score = quality_score(norm)
    alpha = sum(1 for c in norm if c.isalpha())
    total = len(norm)
    alpha_ratio = (alpha / total) if total else 0.0
    tokens = [t for t in re.split(r"\s+", norm) if t]
    rows.append({
        'file': p.name,
        'length': total,
        'alpha_ratio': round(alpha_ratio, 3),
        'quality_score': round(score, 3),
        'sample': norm[:120]
    })

with OUT.open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['file','length','alpha_ratio','quality_score','sample'])
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} rows to {OUT}")
