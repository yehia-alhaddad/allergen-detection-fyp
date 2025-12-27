import re


def clean_text(text: str) -> str:
    text = text or ""
    text = text.replace("\r", "\n")
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[^\x20-\x7E\n]", "", text)  # printable ASCII
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_ocr_noise(text: str) -> str:
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
        for t in re.split(r"(\s+)", text)
    ]
    return "".join(tokens)


def quality_score(text: str) -> float:
    text = text or ""
    if not text:
        return 0.0
    total = len(text)
    alpha = sum(1 for c in text if c.isalpha())
    alpha_ratio = alpha / total if total else 0.0
    tokens = [t for t in re.split(r"\s+", text) if t]
    common_vocab = {
        "ingredients", "contains", "may", "milk", "wheat", "egg", "soy", "peanut",
        "tree", "nut", "fish", "shellfish", "sesame", "mustard", "celery", "sulfites",
        "water", "salt", "sugar", "oil", "cocoa", "chocolate"
    }
    lower_tokens = [t.lower() for t in tokens]
    hits = sum(1 for t in lower_tokens if t in common_vocab)
    vocab_ratio = hits / (len(tokens) or 1)
    return (alpha_ratio * 0.7) + (vocab_ratio * 0.3)


def is_text_usable(text: str) -> bool:
    text = text or ""
    if len(text) < 50:
        return False
    return quality_score(text) >= 0.35
