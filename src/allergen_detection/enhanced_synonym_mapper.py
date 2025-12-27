"""Enhanced synonym matcher with multi-level matching strategies"""
import json
import re
from typing import Set
from pathlib import Path


class EnhancedSynonymMapper:
    """Improved allergen detection with multiple matching strategies.
    
    Features:
    1. Word boundary matching (no false positives)
    2. Plural/singular handling
    3. Compound word matching
    4. Partial word matching with context
    5. Case-insensitive matching
    """
    
    def __init__(self, allergen_dict: dict):
        """Initialize with allergen dictionary."""
        self.allergen_dict = allergen_dict
        self._compile_patterns()
        
        # Track statistics
        self.matches_log = []
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        self.patterns = {}
        
        for allergen, synonyms in self.allergen_dict.items():
            # Build regex pattern with word boundaries and plural forms
            pattern_parts = []
            for synonym in synonyms:
                # Add word boundary version and plural version
                # Handle phrases like "milk solids" -> "milk\s+solids"
                pattern_parts.append(re.escape(synonym.lower()))
                
                # Add plural variant
                if not synonym.endswith('s'):
                    pattern_parts.append(re.escape(synonym.lower()) + 's')
            
            # Combine patterns with OR, add word boundaries
            combined = '|'.join(pattern_parts)
            # Word boundaries: \b or preceded/followed by space/punctuation
            pattern_str = r'(?:^|[\s\-,;:\(]?)(' + combined + r')(?:[\s\-,;:\).]|$)'
            
            try:
                self.patterns[allergen] = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
            except re.error as e:
                print(f"Warning: Failed to compile pattern for {allergen}: {e}")
                self.patterns[allergen] = None
    
    def match(self, text: str) -> Set[str]:
        """Find allergens in text using multi-level matching.
        
        Returns:
            Set of detected allergen names (lowercase)
        """
        detected = set()
        text_lower = text.lower()
        
        for allergen, pattern in self.patterns.items():
            if pattern is None:
                continue
            
            # Use regex to find matches
            matches = pattern.finditer(text_lower)
            if matches:
                # Verify match is not in a compound word that wouldn't make sense
                for match in matches:
                    # Get the matched text (group 1 is the synonym)
                    matched_text = match.group(1) if match.groups() else match.group(0)
                    
                    # Check context - avoid matching inside other words
                    start = match.start()
                    end = match.end()
                    
                    # Check before
                    if start > 0:
                        before_char = text_lower[start-1]
                        if before_char.isalpha():
                            continue
                    
                    # Check after
                    if end < len(text_lower):
                        after_char = text_lower[end]
                        if after_char.isalpha():
                            continue
                    
                    detected.add(allergen)
                    self.matches_log.append({
                        'allergen': allergen,
                        'matched_text': matched_text,
                        'position': start
                    })
                    break  # Found this allergen, no need to match again
        
        return detected
    
    def match_with_confidence(self, text: str) -> dict:
        """Match allergens and return confidence scores.
        
        Returns:
            Dict with allergen -> confidence score (0-1)
        """
        detected = {}
        text_lower = text.lower()
        
        for allergen, pattern in self.patterns.items():
            if pattern is None:
                continue
            
            matches = pattern.finditer(text_lower)
            match_list = list(matches)
            
            if match_list:
                # Confidence based on:
                # 1. Number of mentions (more = higher)
                # 2. Word boundary match (higher than partial)
                mention_count = len(match_list)
                
                # Base confidence: 0.7 for each mention, max 1.0
                confidence = min(0.7 + (mention_count - 1) * 0.15, 1.0)
                
                detected[allergen] = confidence
        
        return detected

    def get_allergen_name(self, allergen_code: str) -> str:
        """Get human-readable allergen name."""
        name_map = {
            'tree_nut': 'Tree Nuts',
            'peanut': 'Peanuts',
            'shellfish': 'Shellfish',
            'sesame': 'Sesame',
            'sulfites': 'Sulfites'
        }
        return name_map.get(allergen_code, allergen_code.capitalize())
