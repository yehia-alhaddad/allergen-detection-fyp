"""Product name matcher for allergen detection via database lookup"""
from difflib import SequenceMatcher
from typing import Optional, Tuple
import pandas as pd
import cv2
import numpy as np


class ProductNameMatcher:
    """Match product names from images to database and retrieve allergen info.
    
    Strategy:
    1. Extract text from top portion of image (brand/logo area)
    2. Fuzzy match against known product names in database
    3. Return allergens from matched product
    """
    
    def __init__(self, products_df: pd.DataFrame, confidence_threshold: float = 0.6):
        """Initialize matcher with product database.
        
        Args:
            products_df: DataFrame with columns ['product_name', 'allergens', ...]
            confidence_threshold: Min similarity score (0-1) to consider a match
        """
        self.df = products_df
        self.threshold = confidence_threshold
        # Filter out NaN product names
        valid_names = products_df['product_name'].dropna()
        self.product_names = valid_names.str.lower().unique()
    
    def extract_brand_region(self, image: np.ndarray, top_fraction: float = 0.4) -> np.ndarray:
        """Extract top portion of image where brand/logo typically appears.
        
        Args:
            image: Input image (BGR or grayscale)
            top_fraction: Fraction of image height to extract (default 0.4 = top 40%)
        
        Returns:
            Cropped image region (top portion)
        """
        h = image.shape[0]
        crop_height = int(h * top_fraction)
        return image[:crop_height, :]
    
    def extract_text_from_region(self, image_region: np.ndarray, ocr_engine) -> str:
        """Extract text from image region using OCR.
        
        Args:
            image_region: Image region to process
            ocr_engine: EasyOCR engine instance
        
        Returns:
            Extracted text (lowercase, cleaned)
        """
        text = ocr_engine.extract(image_region)
        return text.lower().strip()
    
    def fuzzy_match(self, text: str) -> Tuple[Optional[str], float]:
        """Find best matching product name in database.
        
        Args:
            text: Extracted text to match
        
        Returns:
            Tuple of (best_match_name, confidence_score)
            Returns (None, 0.0) if no match above threshold
        """
        text_clean = text.lower().strip()
        
        best_match = None
        best_score = 0.0
        
        for product_name in self.product_names:
            # Calculate similarity using sequence matcher
            score = SequenceMatcher(None, text_clean, product_name).ratio()
            
            # Also check if product name is substring (high confidence if found)
            if product_name in text_clean or text_clean in product_name:
                score = max(score, 0.85)
            
            if score > best_score:
                best_score = score
                best_match = product_name
        
        # Return match only if above threshold
        if best_score >= self.threshold:
            return best_match, best_score
        
        return None, best_score
    
    def get_allergens(self, product_name: str) -> set:
        """Retrieve allergens for matched product.
        
        Args:
            product_name: Product name to look up
        
        Returns:
            Set of allergen strings, or empty set if none
        """
        matches = self.df[self.df['product_name'].str.lower() == product_name.lower()]
        
        if len(matches) == 0:
            return set()
        
        allergens_str = matches.iloc[0]['allergens']
        
        if pd.isna(allergens_str) or allergens_str == 'NaN':
            return set()
        
        # Parse comma-separated allergens
        allergens = {a.strip().lower() for a in str(allergens_str).split(',')}
        return allergens - {'nan', ''}
    
    def detect_from_image(self, image: np.ndarray, ocr_engine) -> dict:
        """Complete pipeline: extract brand → match → get allergens.
        
        Args:
            image: Input image
            ocr_engine: EasyOCR engine
        
        Returns:
            Dict with keys:
            - 'extracted_text': Text from brand region
            - 'matched_product': Matched product name or None
            - 'confidence': Matching confidence score
            - 'allergens': Set of detected allergens
            - 'method': 'product_name_match' or 'no_match'
        """
        # Extract brand region (top of image)
        brand_region = self.extract_brand_region(image)
        
        # Extract text from brand region
        extracted_text = self.extract_text_from_region(brand_region, ocr_engine)
        
        # Try to match against database
        matched_product, confidence = self.fuzzy_match(extracted_text)
        
        # If match found, get allergens
        if matched_product:
            allergens = self.get_allergens(matched_product)
            return {
                'extracted_text': extracted_text,
                'matched_product': matched_product,
                'confidence': confidence,
                'allergens': allergens,
                'method': 'product_name_match'
            }
        else:
            return {
                'extracted_text': extracted_text,
                'matched_product': None,
                'confidence': confidence,
                'allergens': set(),
                'method': 'no_match'
            }
