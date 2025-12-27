import json
from typing import Dict, List


def load_allergen_dictionary(path: str) -> Dict[str, List[str]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # if format is {"allergens": [{"name":..., "synonyms": [...]}, ...]}
    if isinstance(data, dict) and "allergens" in data:
        return {a["name"]: a.get("synonyms", []) for a in data["allergens"]}
    # if mapping dict already
    if isinstance(data, dict):
        return {k: list(v) for k, v in data.items()}
    raise ValueError("Unsupported allergen dictionary format")
