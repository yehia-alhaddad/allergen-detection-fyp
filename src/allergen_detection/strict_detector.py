"""
Strict, explainable allergen detection with precise classification.
Separates 'Contains' from 'May Contain' with evidence tracking.
"""
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class AllergenCategory(Enum):
    """Allergen classification categories."""
    CONTAINS = "CONTAINS"
    MAY_CONTAIN = "MAY_CONTAIN"
    NOT_DETECTED = "NOT_DETECTED"


@dataclass
class DetectedAllergen:
    """Represents a detected allergen with evidence."""
    name: str
    category: AllergenCategory
    evidence: str  # Exact phrase from label
    confidence: float  # 0.0 to 1.0
    matched_keyword: str  # The keyword that triggered detection


class StrictAllergenDetector:
    """
    Enhanced allergen detector with:
    - Strict Contains vs May Contain classification
    - Exact keyword matching
    - Explainable output with evidence
    - Confidence scoring
    - False positive reduction
    """

    # Allergen keyword mappings with verified synonyms (STRICT - NO PARTIAL MATCHES)
    # Each keyword must match as a complete word to avoid false positives
    ALLERGEN_KEYWORDS = {
        'PEANUT': {
            'keywords': ['peanut', 'peanuts', 'groundnut', 'groundnuts', 'arachis'],
            'products': ['peanut oil', 'peanut butter', 'peanut paste', 'peanut flour']
        },
        'TREE_NUT': {
            'keywords': ['almond', 'almonds', 'walnut', 'walnuts', 'hazelnut', 'hazelnuts',
                        'cashew', 'cashews', 'pistachio', 'pistachios', 'pecan', 'pecans',
                        'brazil nut', 'brazil nuts', 'macadamia', 'macadamias', 
                        'chestnut', 'chestnuts', 'pine nut', 'pine nuts'],
            'products': ['nut butter', 'nut oil', 'nut paste', 'tree nut', 'tree nuts']
        },
        'MILK': {
            'keywords': ['milk', 'lactose', 'casein', 'whey', 'butter', 'cheese', 
                        'cream', 'yogurt', 'yoghurt', 'ghee', 'milkfat', 'dairy'],
            'products': ['milk powder', 'milk solids', 'milk fat', 'dairy product', 
                        'dairy products', 'whey powder', 'whey protein']
        },
        'EGG': {
            'keywords': ['egg', 'eggs', 'albumen', 'ovalbumin', 'albumin', 
                        'lysozyme', 'ovomucoid'],
            'products': ['egg powder', 'egg white', 'egg yolk', 'egg protein']
        },
        'GLUTEN': {
            'keywords': ['gluten', 'wheat', 'barley', 'rye', 'spelt', 'kamut'],
            'products': ['wheat flour', 'wheat protein', 'wheat starch', 
                        'rye flour', 'barley malt']
        },
        'SOY': {
            'keywords': ['soy', 'soya', 'soybean', 'soybeans', 'tofu', 'tempeh', 'edamame'],
            'products': ['soy sauce', 'soy lecithin', 'soy flour', 'soya oil', 
                        'soy protein', 'soya protein']
        },
        'FISH': {
            # CRITICAL: 'fish' must be standalone word, NOT part of 'shellfish'
            'keywords': ['anchovy', 'anchovies', 'cod', 'salmon', 'tuna', 'trout', 
                        'bass', 'herring', 'sardine', 'sardines', 'whitebait', 
                        'haddock', 'pollock', 'mackerel', 'tilapia'],
            'products': ['fish oil', 'fish sauce', 'fish stock', 'fish protein'],
            # Add exclusion patterns to avoid false positives
            'exclusions': ['shellfish']
        },
        'SHELLFISH': {
            # Must match complete shellfish terms, NOT just 'shell'
            'keywords': ['shrimp', 'shrimps', 'prawn', 'prawns', 'crab', 'crabs',
                        'lobster', 'lobsters', 'clam', 'clams', 'oyster', 'oysters',
                        'mussel', 'mussels', 'scallop', 'scallops', 'squid', 
                        'octopus', 'calamari', 'crustacean', 'crustaceans'],
            'products': ['shellfish', 'mollusc', 'molluscs', 'mollusk', 'mollusks']
        },
        'SESAME': {
            'keywords': ['sesame', 'tahini', 'hummus', 'halvah'],
            'products': ['sesame seed', 'sesame seeds', 'sesame oil']
        },
        'MUSTARD': {
            'keywords': ['mustard', 'dijon'],
            'products': ['mustard seed', 'mustard seeds', 'mustard powder', 'mustard oil']
        },
        'CELERY': {
            'keywords': ['celery', 'celeriac'],
            'products': ['celery seed', 'celery seeds', 'celery salt', 'celery juice']
        },
        'SULPHITES': {
            'keywords': ['sulphite', 'sulphites', 'sulfite', 'sulfites', 
                        'sulphur dioxide', 'sulfur dioxide', 'e220', 'e221', 'e222'],
            'products': []
        },
        'LUPIN': {
            'keywords': ['lupin', 'lupine'],
            'products': ['lupin flour', 'lupin seed', 'lupin seeds']
        }
    }

    # Patterns to identify "May Contain" / trace statements
    MAY_CONTAIN_PATTERNS = [
        r'\bmay\s+contain\b',
        r'\bcontains\s+trace',
        r'\btraces?\s+of\b',
        r'\bcross[\s-]contaminat',
        r'\bmay\s+contain\s+trace',
        r'\bproduced\s+in\s+a\s+facility',
        r'\bprocessed\s+with',
        r'\bshared\s+equipment',
        r'\bequipment\s+.*allergen'
    ]

    # Patterns to identify explicit ingredient list sections
    INGREDIENT_PATTERNS = [
        r'\bingredients?[\s:]*',
        r'\bcontains[\s:]*',
        r'\bmade\s+with[\s:]*'
    ]

    def __init__(self):
        """Initialize the detector."""
        self.may_contain_pattern = re.compile('|'.join(self.MAY_CONTAIN_PATTERNS), re.IGNORECASE)
        self.ingredient_pattern = re.compile('|'.join(self.INGREDIENT_PATTERNS), re.IGNORECASE)

    def detect(self, text: str) -> Dict[str, List[DetectedAllergen]]:
        """
        Detect allergens with strict classification.
        
        Args:
            text: Cleaned ingredient text from label
            
        Returns:
            Dictionary with 'contains', 'may_contain', and 'not_detected' lists
        """
        if not text or len(text.strip()) < 3:
            return self._empty_result()

        text_lower = text.lower()
        
        # Split text into sections
        ingredient_section, may_contain_section = self._split_sections(text)
        
        # Detect allergens in each section
        contains_allergens = self._detect_in_section(
            ingredient_section, 
            category=AllergenCategory.CONTAINS
        )
        
        may_contain_allergens = self._detect_in_section(
            may_contain_section,
            category=AllergenCategory.MAY_CONTAIN
        )
        
        # Compile results
        detected_names = {a.name for a in contains_allergens + may_contain_allergens}
        not_detected = [name for name in self.ALLERGEN_KEYWORDS.keys() if name not in detected_names]
        
        return {
            'contains': contains_allergens,
            'may_contain': may_contain_allergens,
            'not_detected': [DetectedAllergen(
                name=name,
                category=AllergenCategory.NOT_DETECTED,
                evidence='',
                confidence=0.0,
                matched_keyword=''
            ) for name in not_detected]
        }

    def _split_sections(self, text: str) -> Tuple[str, str]:
        """
        Split text into ingredient and may_contain sections.
        
        Returns:
            (ingredient_text, may_contain_text)
        """
        text_lower = text.lower()
        
        # Find may contain section
        may_contain_match = self.may_contain_pattern.search(text_lower)
        if may_contain_match:
            may_contain_start = may_contain_match.start()
            ingredient_text = text[:may_contain_start]
            may_contain_text = text[may_contain_start:]
            
            # Clean up may_contain section - remove storage/date instructions that follow
            # Look for common separators that indicate end of allergen list
            non_ingredient_markers = [
                'store in', 'store at', 'storage', 'best before', 'best by',
                'use by', 'expiry', 'batch', 'lot', 'manufactured', 'packed on',
                'keep refrigerated', 'keep frozen', 'refrigerate', 'freeze'
            ]
            
            # Find earliest non-ingredient marker
            may_contain_lower = may_contain_text.lower()
            earliest_marker_pos = len(may_contain_text)
            
            for marker in non_ingredient_markers:
                pos = may_contain_lower.find(marker)
                if pos != -1 and pos < earliest_marker_pos:
                    earliest_marker_pos = pos
            
            # Trim may_contain to exclude non-ingredient text
            if earliest_marker_pos < len(may_contain_text):
                may_contain_text = may_contain_text[:earliest_marker_pos].strip()
        else:
            ingredient_text = text
            may_contain_text = ''
        
        return ingredient_text, may_contain_text

    def _detect_in_section(self, text: str, category: AllergenCategory) -> List[DetectedAllergen]:
        """
        Detect allergens in a specific section with STRICT exact keyword matching.
        Prevents false positives from substring matches (e.g., 'shell' != 'shellfish')
        
        Args:
            text: Text to search
            category: CONTAINS or MAY_CONTAIN
            
        Returns:
            List of detected allergens with high precision
        """
        if not text or len(text.strip()) < 1:
            return []
        
        detected = []
        text_lower = text.lower()
        
        # Preprocess: normalize spacing and punctuation for better matching
        text_normalized = re.sub(r'[,;:]+', ' ', text_lower)
        text_normalized = re.sub(r'\s+', ' ', text_normalized).strip()
        
        # Check for instruction/storage/dating sections (not ingredient-based)
        # Instructions like "keep away from nuts" or "store in a cool place" shouldn't trigger allergen detection
        # Common OCR errors in these sections create false positives (e.g., "cool" → "cod")
        instruction_keywords = [
            'storage', 'instructions', 'keep away from', 'avoid contact',
            'separate from', 'do not store', 'store in', 'store at',
            'best before', 'best by', 'use by', 'expiry', 'expires',
            'batch', 'lot', 'manufactured', 'packed on', 'production date',
            'cool place', 'dry place', 'room temperature', 'refrigerate',
            'freeze', 'once opened', 'after opening', 'keep refrigerated',
            'keep frozen', 'consume within', 'shelf life'
        ]
        is_instruction_section = any(keyword in text_normalized for keyword in instruction_keywords)
        
        # If this is clearly an instruction/storage/dating section (not ingredients),
        # only detect if there's explicit ingredient language
        if is_instruction_section and category == AllergenCategory.CONTAINS:
            has_ingredient_language = any(lang in text_normalized for lang in 
                                         ['ingredient', 'contain', 'made with', 'include'])
            if not has_ingredient_language:
                return []  # Skip detection in instruction-only sections
        
        # SPECIAL HANDLING FOR FISH: Add standalone 'fish' only if not part of 'shellfish'
        # We'll handle FISH allergen specially to avoid 'shellfish' triggering it
        if 'FISH' in self.ALLERGEN_KEYWORDS:
            # Check if 'fish' appears standalone (not as part of 'shellfish')
            if re.search(r'\bfish\b', text_normalized):
                # Verify it's not part of 'shellfish'
                if not re.search(r'\bshellfish\b', text_normalized):
                    # Add 'fish' as a valid keyword for detection
                    # This ensures 'fish' alone triggers FISH allergen
                    if 'fish' not in self.ALLERGEN_KEYWORDS['FISH']['keywords']:
                        self.ALLERGEN_KEYWORDS['FISH']['keywords'].append('fish')
                else:
                    # Remove 'fish' if 'shellfish' is present to avoid false positive
                    if 'fish' in self.ALLERGEN_KEYWORDS['FISH']['keywords']:
                        self.ALLERGEN_KEYWORDS['FISH']['keywords'] = [
                            k for k in self.ALLERGEN_KEYWORDS['FISH']['keywords'] if k != 'fish'
                        ]
        
        # Split into words and phrases for exact matching
        for allergen_name, keywords_dict in self.ALLERGEN_KEYWORDS.items():
            
            # Check exclusion patterns first (prevents false positives)
            exclusions = keywords_dict.get('exclusions', [])
            skip_allergen = False
            for exclusion in exclusions:
                if exclusion in text_normalized:
                    # Check if this is specifically an exclusion case
                    # E.g., 'fish' should not match when 'shellfish' is present
                    if allergen_name == 'FISH':
                        # Only skip if we find 'shellfish' but not standalone 'fish'
                        if re.search(r'\bshellfish\b', text_normalized) and not re.search(r'\bfish\b(?!\s*oil|sauce|stock)', text_normalized):
                            skip_allergen = True
                            break
            
            if skip_allergen:
                continue
            
            # Try keyword matching with strict word boundaries
            all_keywords = keywords_dict.get('keywords', []) + keywords_dict.get('products', [])
            
            for keyword in all_keywords:
                # CRITICAL: Use strict word boundary matching
                # This prevents 'shell' from matching 'shellfish'
                pattern = r'\b' + re.escape(keyword) + r'\b'
                match = re.search(pattern, text_normalized)
                
                if match:
                    # Verify this is not a false positive
                    if not self._is_false_positive(keyword, text_normalized, match):
                        # Extract evidence from ORIGINAL text (not normalized)
                        # Find the keyword in the original text_lower to get correct indices
                        keyword_match = re.search(r'\b' + re.escape(keyword) + r'\b', text_lower)
                        if keyword_match:
                            # Extract surrounding context (20 chars before and after)
                            start = max(0, keyword_match.start() - 20)
                            end = min(len(text), keyword_match.end() + 20)
                            evidence = text[start:end].strip()
                        else:
                            evidence = ''
                        
                        confidence = self._calculate_confidence(allergen_name, evidence, category, text_normalized)
                        
                        # Only add if confidence is high enough
                        if confidence >= 0.7:  # Strict threshold
                            detected.append(DetectedAllergen(
                                name=allergen_name,
                                category=category,
                                evidence=evidence,
                                confidence=confidence,
                                matched_keyword=keyword
                            ))
                            break  # Only report once per allergen
            
        # Remove duplicates, keeping highest confidence
        unique_detected = {}
        for allergen in detected:
            if allergen.name not in unique_detected or allergen.confidence > unique_detected[allergen.name].confidence:
                unique_detected[allergen.name] = allergen
        
        return list(unique_detected.values())

    def _calculate_confidence(self, allergen: str, evidence: str, category: AllergenCategory, full_text: str = '') -> float:
        """
        Calculate confidence score for detected allergen with strict validation.
        
        Args:
            allergen: Allergen name
            evidence: Exact phrase from label
            category: CONTAINS or MAY_CONTAIN
            full_text: Full normalized text for context checking
            
        Returns:
            Confidence score 0.0-1.0 (strict threshold applied)
        """
        # Base confidence depends on category
        base_confidence = 1.0 if category == AllergenCategory.CONTAINS else 0.9
        
        evidence_lower = evidence.lower()
        
        # Check for negation words (allergen-free claims)
        negation_patterns = [
            r'\bno\s+' + re.escape(allergen.lower()),
            r'\bfree\s+from\s+' + re.escape(allergen.lower()),
            r'\b' + re.escape(allergen.lower()) + r'\s+free\b',
            r'\bwithout\s+' + re.escape(allergen.lower()),
            r'\bdoes\s+not\s+contain\s+' + re.escape(allergen.lower()),
            r'\bnon[- ]' + re.escape(allergen.lower())
        ]
        
        for pattern in negation_patterns:
            if re.search(pattern, evidence_lower):
                return 0.1  # Very low confidence for negated allergens
        
        # Check for ambiguous contexts that reduce confidence
        ambiguous_words = ['maybe', 'possibly', 'unclear', 'uncertain']
        for word in ambiguous_words:
            if word in evidence_lower:
                base_confidence *= 0.5
        
        # Boost confidence for explicit allergen declarations
        explicit_patterns = ['contains', 'ingredients:', 'made with', 'includes']
        for pattern in explicit_patterns:
            if pattern in evidence_lower:
                base_confidence = min(1.0, base_confidence * 1.1)
        
        return round(base_confidence, 2)
    
    def _is_false_positive(self, keyword: str, text: str, match: re.Match) -> bool:
        """
        Check if a keyword match is a false positive.
        
        Args:
            keyword: The matched keyword
            text: Full text being searched
            match: The regex match object
            
        Returns:
            True if this is a false positive, False if legitimate
        """
        # Get surrounding context (larger window for better detection)
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].lower()
        
        # Check if keyword appears in non-ingredient sections
        # Common OCR errors in storage/dating sections: "cool" → "cod", "batch" → "batch"
        non_ingredient_phrases = [
            'store in', 'store at', 'storage', 'cool place', 'dry place',
            'best before', 'best by', 'use by', 'expiry', 'expires',
            'batch', 'lot', 'manufactured', 'packed on', 'production',
            'room temperature', 'refrigerate', 'freeze', 'keep refrigerated',
            'keep frozen', 'once opened', 'after opening', 'consume within'
        ]
        
        for phrase in non_ingredient_phrases:
            if phrase in context:
                # Found non-ingredient context - likely false positive
                return True
        
        # SPECIAL: For "cod" - if it appears with "place" but no ingredient context, it's likely OCR error
        # "cod place" or similar is NOT an ingredient declaration
        if keyword == 'cod':
            # Check if this is just "cod" followed by non-ingredient words
            words_around = context.split()
            cod_words = [w for w in words_around if 'cod' in w]
            
            if cod_words:
                # Check what comes after cod
                for i, word in enumerate(words_around):
                    if 'cod' in word:
                        # If next word is place/places/placement/etc or previous word is storage-related
                        if i + 1 < len(words_around):
                            next_word = words_around[i + 1]
                            if next_word in ['place', 'places', 'placement', 'dry', 'cool']:
                                return True  # "cod place" is OCR error
                        if i > 0:
                            prev_word = words_around[i - 1]
                            if prev_word in ['store', 'stored', 'keep', 'storage']:
                                return True
        
        # Check for compound words that shouldn't match
        # E.g., 'shell' in 'eggshell' or 'seashell' is not 'shellfish'
        false_positive_compounds = {
            'shellfish': [
                'pistachio', 'walnut', 'almond', 'hazelnut', 'peanut',  # nuts + shell = not shellfish
                'oyster shell', 'clam shell', 'scallop shell',  # actual shells
                'eggshell', 'seashell', 'nutshell', 'bombshell',
                'w/out shell', 'without shell', 'with shell'  # OCR artifacts
            ],
            'shell': ['eggshell', 'seashell', 'nutshell', 'bombshell', 'oyster shell',
                     'walnut', 'pistachio', 'almond', 'hazelnut',  # nuts with shell
                     'w/out', 'without', 'with'],  # packaging references
            'nut': ['coconut', 'donut', 'doughnut', 'chestnut'],  # chestnut NOT a tree nut in this context
            'milk': ['almond milk', 'soy milk', 'coconut milk', 'oat milk', 'rice milk'],  # substitutes
            'butter': ['nut butter', 'peanut butter', 'almond butter', 'cashew butter',  # nut butters
                      'cocoa butter', 'shea butter', 'mango butter'],  # non-dairy butters
        }
        
        if keyword in false_positive_compounds:
            for compound in false_positive_compounds[keyword]:
                if compound in context:
                    return True
        
        # Special handling for "almond milk substitute" - should NOT trigger MILK
        # but SHOULD trigger TREE_NUT for almond
        if keyword in ['milk', 'dairy'] and 'substitute' in context:
            return True  # milk substitute is NOT milk allergen
        
        # If almond appears with milk/substitute, allow TREE_NUT detection
        # but block MILK detection
        if keyword == 'almond':
            return False  # almond is always valid TREE_NUT
        
        # Check for negation patterns right after the match
        close_negations = ['free', 'substitute', 'free formula', 'alternative']
        text_after = text[match.end():match.end() + 40].lower()
        for negation in close_negations:
            if negation in text_after:
                return True
        
        # Check if negation appears very close before the keyword
        words_before = context[:match.start() - start].lower().split()
        if len(words_before) > 0:
            near_words = words_before[-2:]  # Check last 2 words
            for near_word in near_words:
                if near_word in ['no', 'not', 'may', 'be', 'free']:
                    # Check pattern like "may be free", "no milk", "not milk"
                    if 'free' in text_after or 'substitute' in text_after:
                        return True
        
        return False

    def _empty_result(self) -> Dict[str, List[DetectedAllergen]]:
        """Return empty detection result with all allergens marked as not_detected."""
        return {
            'contains': [],
            'may_contain': [],
            'not_detected': [DetectedAllergen(
                name=name,
                category=AllergenCategory.NOT_DETECTED,
                evidence='',
                confidence=0.0,
                matched_keyword=''
            ) for name in self.ALLERGEN_KEYWORDS.keys()]
        }

    @staticmethod
    def format_results(detection_results: Dict[str, List[DetectedAllergen]]) -> Dict:
        """
        Format detection results for API response.
        
        Args:
            detection_results: Output from detect()
            
        Returns:
            Consumer-safe formatted output
        """
        return {
            'contains': [
                {
                    'allergen': a.name,
                    'evidence': a.evidence,
                    'keyword': a.matched_keyword,
                    'confidence': round(a.confidence, 2)
                }
                for a in detection_results['contains']
            ],
            'may_contain': [
                {
                    'allergen': a.name,
                    'evidence': a.evidence,
                    'keyword': a.matched_keyword,
                    'confidence': round(a.confidence, 2)
                }
                for a in detection_results['may_contain']
            ],
            'not_detected': [a.name for a in detection_results['not_detected']],
            'summary': {
                'contains_count': len(detection_results['contains']),
                'may_contain_count': len(detection_results['may_contain']),
                'total_detected': len(detection_results['contains']) + len(detection_results['may_contain'])
            }
        }
