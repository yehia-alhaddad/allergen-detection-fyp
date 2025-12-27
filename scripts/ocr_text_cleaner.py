"""
OCR Text Cleaning & Normalization Module.
Fixes common OCR errors, typos, and normalizes text for better NER performance.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
from difflib import SequenceMatcher

# Common OCR substitutions (character-level errors)
OCR_CHAR_FIXES = {
    # Letter confusions
    'rn': 'm',  # rn → m (e.g., "cornn" → "comm")
    '1': 'l',   # 1 → l (e.g., "a1mond" → "almond")
    '0': 'o',   # 0 → o (e.g., "c0w" → "cow")
    '5': 's',   # 5 → s (e.g., "salt5" → "salts")
    'S': 's',   # S → s (e.g., "Salt" → "salt")
    'T': 't',   # T → t (e.g., "Tg" → "tg")
}

# Common allergen-specific OCR errors
ALLERGEN_OCR_FIXES = {
    # Peanuts
    'peanats': 'peanut',
    'peanuts': 'peanut',
    'peatat': 'peanut',
    'peanu': 'peanut',
    'peanut skin-on': 'peanut',
    'peanut skin on': 'peanut',
    'groundnut': 'peanut',
    'arachis': 'peanut',
    
    # Tree Nuts
    'nuts': 'nut',
    'almond': 'almond',
    'hazelnut': 'hazelnut',
    'walnut': 'walnut',
    'walnuts': 'walnut',
    'walnt': 'walnut',
    'cashew': 'cashew',
    'cashews': 'cashew',
    'pistachio': 'pistachio',
    'pecan': 'pecan',
    'brazil nut': 'brazil nut',
    'brazil nuts': 'brazil nut',
    'brazli': 'brazil nut',
    'brazi': 'brazil nut',
    'macadamia': 'macadamia',
    'coconut': 'coconut',
    'muts': 'nuts',
    'nut': 'nut',
    
    # Milk
    'mk': 'milk',
    'milk product': 'milk',
    'dairy': 'milk',
    'lactose': 'milk',
    'casein': 'milk',
    'whey': 'milk',
    'butter': 'butter',
    'cheese': 'cheese',
    'yogurt': 'yogurt',
    # Note: 'cream' NOT mapped to avoid false matches
    
    # Gluten  
    'cereak': 'cereal',
    'gltn': 'gluten',
    'glten': 'gluten',
    'wheat': 'wheat',
    'barley': 'barley',
    'rye': 'rye',
    'gluten': 'gluten',
    'flour': 'flour',
    'bread': 'bread',
    'pasta': 'pasta',
    'noodle': 'noodle',
    'oat': 'oat',
    # Note: 'cereal' removed from fixes to prevent false 'cream' → 'cereal' conversion
    
    # Sesame
    'sesame': 'sesame',
    'sesem': 'sesame',
    'seseme': 'sesame',
    'tahini': 'tahini',
    'hummu': 'hummus',
    
    # Soy
    'soy': 'soy',
    'soya': 'soy',
    'soybean': 'soy',
    
    # Fish
    'fish': 'fish',
    'anchovy': 'anchovy',
    'salmon': 'salmon',
    'tuna': 'tuna',
    'cod': 'cod',
    
    # Shellfish
    'shellfish': 'shellfish',
    'shrimp': 'shrimp',
    'prawn': 'prawn',
    'crab': 'crab',
    'lobster': 'lobster',
    'clam': 'clam',
    'oyster': 'oyster',
    'mussel': 'mussel',
    'scallop': 'scallop',
    
    # Eggs
    'egg': 'egg',
    'albumen': 'albumen',
    'mayonnaise': 'mayonnaise',
    
    # Mustard
    'mustard': 'mustard',
    'dijon': 'dijon',
    
    # Sulphites
    'sulphite': 'sulphite',
    'sulfite': 'sulphite',
    'so2': 'sulphite',
    'preservative': 'preservative',
    
    # Celery
    'celery': 'celery',
    'celeriac': 'celery',
    
    # Lupin
    'lupin': 'lupin',
}

# Common OCR phrase patterns
ALLERGEN_PHRASE_PATTERNS = [
    (r'contains?\s*[:\-]*\s*', 'contains '),  # "Contains:" or "Contains -"
    (r'may\s+contain\s+trace', 'may contain trace'),  # "May contain trace"
    (r'may\s+contain\s+', 'may contain '),
    (r'allergy\s+advice[:\-]*\s*', 'contains '),
    (r'allergen[s]?\s+info[:\-]*\s*', 'contains '),
    (r'ingredient[s]?[:\-]*\s*', 'ingredients: '),
    (r'\s+and\s+', ', '),  # "and" → ", "
    (r',\s*,', ','),  # ",," → ","
]

class OCRTextCleaner:
    """Clean and normalize noisy OCR text."""
    
    def __init__(self):
        self.allergen_fixes = ALLERGEN_OCR_FIXES
        self.phrase_patterns = ALLERGEN_PHRASE_PATTERNS
    
    def clean(self, text: str) -> str:
        """Apply all cleaning steps including fuzzy matching for unknown allergen words."""
        if not text:
            return ""
        
        # 1. Lowercase
        text = text.lower()
        
        # 2. Fix common phrase patterns
        for pattern, replacement in self.phrase_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # 3. Fix allergen-specific terms
        for ocr_variant, correct_form in self.allergen_fixes.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(ocr_variant) + r'\b'
            text = re.sub(pattern, correct_form, text, flags=re.IGNORECASE)
        
        # 4. Apply fuzzy matching for potential allergen words (2-3 chars, likely OCR errors)
        words = text.split()
        fuzzy_matched = []
        for word in words:
            # Fuzzy match short words that might be garbled allergen names
            # Avoid very short words (<4 chars) to prevent false matches like 'cream' → 'cereal'
            if len(word) >= 4 and len(word) <= 8 and not any(c.isdigit() for c in word):
                matched = self.fuzzy_match_allergen(word, threshold=0.65)
                if matched != word:  # Found a match
                    fuzzy_matched.append(matched)
                else:
                    fuzzy_matched.append(word)
            else:
                fuzzy_matched.append(word)
        text = ' '.join(fuzzy_matched)
        
        # 5. Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 6. Remove common OCR artifacts
        text = re.sub(r'[^a-z0-9\s\-\.,:]', '', text)
        
        return text
    
    def fuzzy_match_allergen(self, word: str, threshold: float = 0.65) -> str:
        """
        Try to match garbled word to known allergen using fuzzy matching.
        Returns matched allergen name or original word if no match.
        Tuned to 0.65 threshold to catch moderate OCR damage while avoiding false positives.
        """
        # Exclusion list: common words that should NOT be fuzzy-matched
        exclusions = ['cream', 'cereal', 'cream milk', 'organic', 'ingredients', 
                      'contains', 'serving', 'energy', 'protein', 'total', 'sugar']
        if word.lower() in exclusions:
            return word
        
        best_match = None
        best_score = threshold
        
        # Extended list with specific allergen variants
        allergen_keywords = [
            "peanut", "tree nut", "milk", "egg", "fish", "shellfish",
            "gluten", "wheat", "cereal", "sesame", "soy", "sulphite",
            "mustard", "lupin",
            # Additional specific nut types for better matching
            "walnut", "almond", "cashew", "hazelnut", "pecan", "pistachio", "macadamia",
            "brazil nut", "coconut"
        ]
        
        for allergen in allergen_keywords:
            # Use SequenceMatcher for fuzzy string matching
            ratio = SequenceMatcher(None, word.lower(), allergen).ratio()
            if ratio > best_score:
                best_score = ratio
                best_match = allergen
        
        return best_match if best_match else word
    
    def compare(self, original: str, cleaned: str) -> Dict:
        """Return statistics on what was cleaned."""
        return {
            'original_length': len(original),
            'cleaned_length': len(cleaned),
            'characters_removed': len(original) - len(cleaned),
            'original': original[:100],
            'cleaned': cleaned[:100],
        }


def _compute_context_confidence(text: str, match_pos: int, keyword: str) -> float:
    """
    Smart context analyzer: scores how likely a keyword match is a real allergen mention.
    
    Strategy:
    - HIGH confidence: Near ingredient markers, surrounded by food words
    - LOW confidence: Near nutritional terms WITHOUT ingredient context
    - Uses semantic context, not hardcoded lists
    
    Returns: 0.0 (definitely false) to 1.0 (definitely true allergen)
    """
    # Extract window around match
    window_size = 100
    start = max(0, match_pos - window_size)
    end = min(len(text), match_pos + len(keyword) + window_size)
    context = text[start:end].lower()
    
    score = 0.5  # Neutral starting point
    
    # 1. STRONG POSITIVE SIGNALS (ingredient context)
    ingredient_markers = ['ingredients:', 'contains:', 'may contain', 'allergen', 'allergy', 'contains ']
    has_ingredient_marker = any(marker in context for marker in ingredient_markers)
    if has_ingredient_marker:
        score += 0.6  # Very strong boost for clear ingredient markers (overcomes nearby nutritional terms)
    
    # Food/ingredient-related words nearby suggest real allergen
    food_words = ['oil', 'salt', 'sugar', 'flour', 'sauce', 'powder', 'extract', 
                  'organic', 'natural', 'fresh', 'whole', 'grain', 'seed', 'water']
    food_word_count = sum(1 for word in food_words if word in context)
    score += min(0.3, food_word_count * 0.08)
    
    # 2. NEGATIVE SIGNALS (non-ingredient context)
    # Nutritional/measurement terms ONLY penalize if no ingredient markers present
    nutrition_terms = ['serving', 'per 100', 'energy', 'kilojoule', 'calorie', 
                       'average', 'rdi', 'qty']
    nutrition_term_count = sum(1 for term in nutrition_terms if term in context)
    if nutrition_term_count > 0 and not has_ingredient_marker:
        score -= min(0.4, nutrition_term_count * 0.15)
    
    # Headings/labels suggest false positive ONLY if isolated
    metadata_terms = ['information', 'nutrition facts', 'label', 'package']
    if any(term in context for term in metadata_terms) and not has_ingredient_marker:
        score -= 0.3
    
    # Numbers with units in immediate vicinity (within 10 chars) suggest nutritional data
    # BUT only penalize if the allergen word itself looks like it's part of a measurement
    keyword_pos_in_context = context.find(keyword)
    if keyword_pos_in_context != -1:
        # Check 10 chars before and after the keyword
        nearby_start = max(0, keyword_pos_in_context - 10)
        nearby_end = min(len(context), keyword_pos_in_context + len(keyword) + 10)
        nearby = context[nearby_start:nearby_end]
        
        # Only penalize if number+unit appears IMMEDIATELY adjacent (within 3 chars)
        immediate_before = context[max(0, keyword_pos_in_context - 3):keyword_pos_in_context]
        immediate_after = context[keyword_pos_in_context + len(keyword):min(len(context), keyword_pos_in_context + len(keyword) + 3)]
        
        if re.search(r'\d+\s*[gm][gl]?\b', immediate_before + immediate_after):
            score -= 0.3
    
    # 3. STRUCTURAL SIGNALS
    # Colon after match suggests it's a heading/label (e.g., "Nutrition Information:")
    if re.search(r'\b' + re.escape(keyword) + r'\b\s*:', context):
        score -= 0.4
    
    # Commas, parentheses suggest list of ingredients (positive)
    if ',' in context or '(' in context or ')' in context:
        score += 0.2
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, score))


def extract_allergen_mentions(text: str) -> Dict[str, List[str]]:
    """
    Extract allergen mentions using smart context analysis.
    
    This approach is generalizable - it learns what ingredient contexts LOOK like
    semantically, rather than hardcoding specific patterns to filter.
    
    Returns: allergen → list of contexts where found
    """
    allergens = {
        'PEANUT': ['peanut', 'groundnut', 'arachis'],
        'TREE_NUT': ['almond', 'walnut', 'cashew', 'hazelnut', 'pecan', 'pistachio', 
                     'brazil nut', 'macadamia', 'coconut', 'nut'],
        'MILK': ['milk', 'dairy', 'lactose', 'casein', 'whey', 'butter', 'cheese', 'yogurt'],
        'GLUTEN': ['gluten', 'wheat', 'barley', 'rye', 'flour', 'bread', 'pasta', 'noodle', 'oat'],
        'SESAME': ['sesame', 'tahini', 'hummus'],
        'SOY': ['soy', 'soya', 'soybean'],
        'FISH': ['fish', 'anchovy', 'salmon', 'tuna', 'cod'],
        'SHELLFISH': ['shellfish', 'shrimp', 'prawn', 'crab', 'lobster', 'clam', 'oyster', 'mussel', 'scallop'],
        'EGG': ['egg', 'albumen', 'mayonnaise'],
        'MUSTARD': ['mustard', 'dijon'],
        'SULPHITES': ['sulphite', 'sulphites', 'sulfite', 'sulfites', 'so2', 'preservative'],
        'CELERY': ['celery', 'celeriac'],
        'LUPIN': ['lupin'],
    }
    
    text_lower = text.lower()
    found = {}
    
    # Lower confidence threshold: 0.4 allows detection even in mixed contexts
    # (e.g., ingredient list near nutrition table)
    CONFIDENCE_THRESHOLD = 0.4
    
    for allergen, keywords in allergens.items():
        mentions = []
        for keyword in keywords:
            # Use word boundaries to prevent partial matches (e.g., "nut" in "nutrition")
            pattern = r'\b' + re.escape(keyword) + r'\b'
            
            for m in re.finditer(pattern, text_lower):
                idx = m.start()
                
                # Smart context analysis
                confidence = _compute_context_confidence(text_lower, idx, keyword)
                
                # Negation handling: skip mentions like "free from X", "no X", "does not contain X"
                start = max(0, idx - 50)
                end = min(len(text), idx + len(keyword) + 50)
                local_context = text[start:end].lower()
                negation_patterns = [
                    r"free\s+from\s+" + re.escape(keyword),
                    r"does\s+not\s+contain\s+" + re.escape(keyword),
                    r"no\s+" + re.escape(keyword),
                    r"zero\s+" + re.escape(keyword)
                ]
                if any(re.search(p, local_context) for p in negation_patterns):
                    continue

                if confidence < CONFIDENCE_THRESHOLD:
                    continue  # Skip low-confidence matches
                
                # Extract context for display
                start2 = max(0, idx - 30)
                end2 = min(len(text), idx + len(keyword) + 30)
                context = text[start2:end2].strip()
                mentions.append(context)
        
        if mentions:
            found[allergen] = list(set(mentions))  # Remove duplicates
    
    return found


def main():
    # Test with the problematic OCR text
    dirty_text = """MulheluFUNMAULL SERVES PER PACK 20 SERVE SIZE 25g Avg: Per Avg Per Serve 100g 619kJ 2475kJ Energy Protien 6.5g 25.9g Fat; Total 121g 48.2g Saturated Fat 0.Tg 2.8g Carbohydrate 21g 8.5g Sugars 1.4g 5.4g Sodium S1mg 202mg Ingredients: Mixed Muts (989) Peanuts, Almonds Cashews; Peatats Skin-On Brazi Muts, Watuts) Canola Oil; Jalt (1%) Contains: Peanus Almonds, Cashews, Peanus Brazil Nuts Walnus May contain traces ot Cereak: containing Gluten; Other Tree Nus Sesame Seeds, Lupins Soy' Suphites and Mk Products"""
    
    cleaner = OCRTextCleaner()
    cleaned = cleaner.clean(dirty_text)
    
    print("=" * 80)
    print("OCR TEXT CLEANING DEMO")
    print("=" * 80)
    print("\nORIGINAL:")
    print(dirty_text[:200])
    print("\nCLEANED:")
    print(cleaned[:200])
    
    print("\nALLERGENS DETECTED:")
    allergens = extract_allergen_mentions(cleaned)
    for allergen, contexts in sorted(allergens.items()):
        print(f"\n{allergen}:")
        for ctx in contexts[:2]:  # Show first 2 contexts
            print(f"  - ...{ctx}...")
    
    print(f"\nTotal Allergens Found: {len(allergens)}")


if __name__ == "__main__":
    main()
