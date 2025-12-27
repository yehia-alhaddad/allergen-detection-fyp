import json
import re
from typing import Dict, List, Set


class SynonymMapper:
    def __init__(self, mapping: Dict[str, List[str]], use_word_boundaries: bool = True):
        self.mapping = {k: set(v) | {k} for k, v in mapping.items()}
        self.use_word_boundaries = use_word_boundaries
        # Pre-compile regex patterns for efficiency
        self.patterns = {}
        for key, syns in self.mapping.items():
            if use_word_boundaries:
                # Use word-boundary regex with flexibility for suffixes (e.g., "peanuts" matches "peanut")
                pattern_str = r"\b(" + "|".join(re.escape(s) for s in syns) + r")s?\b"
                self.patterns[key] = re.compile(pattern_str, re.IGNORECASE)
            else:
                self.patterns[key] = None

    @classmethod
    def from_json(cls, path: str, use_word_boundaries: bool = True):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Support both list of allergens or dict format
        if isinstance(data, dict) and "allergens" in data:
            mapping = {a["name"]: a.get("synonyms", []) for a in data["allergens"]}
        else:
            mapping = data
        return cls(mapping, use_word_boundaries=use_word_boundaries)

    def match(self, text: str) -> Set[str]:
        text_lower = text.lower()
        hits = set()
        for key, syns in self.mapping.items():
            if self.use_word_boundaries and key in self.patterns:
                if self.patterns[key].search(text_lower):
                    hits.add(key)
            else:
                # Fallback to simple substring match if word boundaries disabled
                for s in syns:
                    if s.lower() in text_lower:
                        hits.add(key)
                        break
        return hits
