"""
Barcode Detection Module for Fast Allergen Lookup
Scans product barcodes and fetches allergen info from OpenFoodFacts API
"""

import requests
import json
import logging
from typing import Dict, Optional, List
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BarcodeDetector:
    """
    Detects barcodes in images and looks up allergen info from OpenFoodFacts API.
    Provides fast allergen detection without needing OCR.
    """
    
    def __init__(self, cache_dir: str = None, cache_ttl_hours: int = 24):
        """
        Initialize barcode detector with optional caching.
        
        Args:
            cache_dir: Directory to store cached barcode lookups
            cache_ttl_hours: Cache time-to-live in hours (default 24 hours)
        """
        self.api_url = "https://world.openfoodfacts.org/api/v0/product"
        self.cache_dir = Path(cache_dir) if cache_dir else Path(__file__).parent.parent.parent / "data" / "barcode_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        # Try to import pyzbar (barcode detection library)
        try:
            import pyzbar.pyzbar as pyzbar
            self.pyzbar = pyzbar
            self.barcode_available = True
            logger.info("[BarcodeDetector] Pyzbar loaded successfully")
        except ImportError:
            self.barcode_available = False
            logger.warning("[BarcodeDetector] Pyzbar not available. Install: pip install pyzbar pillow")
    
    def detect_barcode_from_image(self, image_path: str) -> Optional[str]:
        """
        Detect barcode from image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Barcode string if found, None otherwise
        """
        if not self.barcode_available:
            logger.warning("[BarcodeDetector] Pyzbar not available - barcode detection disabled")
            return None
        
        try:
            from PIL import Image
            image = Image.open(image_path)
            barcodes = self.pyzbar.decode(image)
            
            if barcodes:
                # Return first detected barcode
                barcode_data = barcodes[0].data.decode('utf-8')
                logger.info(f"[BarcodeDetector] Detected barcode: {barcode_data}")
                return barcode_data
            else:
                logger.debug("[BarcodeDetector] No barcode detected in image")
                return None
        except Exception as e:
            logger.error(f"[BarcodeDetector] Error detecting barcode: {e}")
            return None
    
    def _get_cache_path(self, barcode: str) -> Path:
        """Get cache file path for a barcode."""
        return self.cache_dir / f"{barcode}.json"
    
    def _load_from_cache(self, barcode: str) -> Optional[Dict]:
        """Load barcode data from cache if valid."""
        cache_path = self._get_cache_path(barcode)
        
        if not cache_path.exists():
            return None
        
        try:
            # Check if cache is still valid
            file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if file_age > self.cache_ttl:
                logger.debug(f"[BarcodeDetector] Cache expired for {barcode}")
                return None
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"[BarcodeDetector] Loaded from cache: {barcode}")
                return data
        except Exception as e:
            logger.error(f"[BarcodeDetector] Error loading cache for {barcode}: {e}")
            return None
    
    def _save_to_cache(self, barcode: str, data: Dict) -> None:
        """Save barcode data to cache."""
        try:
            cache_path = self._get_cache_path(barcode)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"[BarcodeDetector] Saved to cache: {barcode}")
        except Exception as e:
            logger.error(f"[BarcodeDetector] Error saving cache for {barcode}: {e}")
    
    def lookup_allergens_by_barcode(self, barcode: str) -> Optional[Dict]:
        """
        Look up product allergen information by barcode using OpenFoodFacts API.
        
        Args:
            barcode: Product barcode (EAN/UPC)
            
        Returns:
            Dict with allergen info or None if not found:
            {
                'barcode': '...',
                'name': 'Product Name',
                'brand': 'Brand Name',
                'allergens': ['MILK', 'GLUTEN', ...],
                'allergen_text': 'Raw allergen text from API',
                'ingredients': 'Raw ingredients text',
                'source': 'openfoodfacts'
            }
        """
        if not barcode or not isinstance(barcode, str):
            logger.warning(f"[BarcodeDetector] Invalid barcode: {barcode}")
            return None
        
        # Try cache first
        cached_data = self._load_from_cache(barcode)
        if cached_data:
            return cached_data
        
        try:
            # Query OpenFoodFacts API
            logger.info(f"[BarcodeDetector] Querying OpenFoodFacts for barcode: {barcode}")
            response = requests.get(
                f"{self.api_url}/{barcode}.json",
                timeout=5,
                headers={'User-Agent': 'AllergenDetectionFYP/1.0'}
            )
            
            if response.status_code != 200:
                logger.warning(f"[BarcodeDetector] API returned status {response.status_code} for barcode {barcode}")
                return None
            
            api_data = response.json()
            
            # Check if product was found
            if api_data.get('status') == 0 or api_data.get('status_verbose') == 'product not found':
                logger.info(f"[BarcodeDetector] Product not found for barcode: {barcode}")
                return None
            
            product = api_data.get('product', {})
            
            # Extract allergen information
            result = {
                'barcode': barcode,
                'name': product.get('product_name', 'Unknown'),
                'brand': product.get('brands', 'Unknown'),
                'allergen_text': product.get('allergens', ''),
                'ingredients': product.get('ingredients_text', ''),
                'source': 'openfoodfacts',
                'country': product.get('countries_en', ''),
                'url': product.get('url', '')
            }
            
            # Parse allergens
            allergens = self._parse_allergens_from_openfoodfacts(product)
            result['allergens'] = allergens
            
            # Cache the result
            self._save_to_cache(barcode, result)
            
            logger.info(f"[BarcodeDetector] Found {len(allergens)} allergens for {barcode}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"[BarcodeDetector] API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"[BarcodeDetector] Error parsing API response: {e}")
            return None
    
    def _parse_allergens_from_openfoodfacts(self, product: Dict) -> List[str]:
        """
        Parse allergen data from OpenFoodFacts product dict.
        Maps OpenFoodFacts allergen names to standard names.
        """
        allergen_map = {
            'gluten': 'GLUTEN',
            'cereals': 'GLUTEN',
            'wheat': 'GLUTEN',
            'barley': 'GLUTEN',
            'rye': 'GLUTEN',
            'oats': 'GLUTEN',
            'milk': 'MILK',
            'dairy': 'MILK',
            'lactose': 'MILK',
            'eggs': 'EGG',
            'egg': 'EGG',
            'peanuts': 'PEANUT',
            'peanut': 'PEANUT',
            'groundnut': 'PEANUT',
            'tree nuts': 'TREE_NUT',
            'almonds': 'TREE_NUT',
            'walnuts': 'TREE_NUT',
            'hazelnuts': 'TREE_NUT',
            'cashews': 'TREE_NUT',
            'pecans': 'TREE_NUT',
            'soy': 'SOY',
            'soya': 'SOY',
            'fish': 'FISH',
            'shellfish': 'SHELLFISH',
            'crustacean': 'SHELLFISH',
            'sesame': 'SESAME',
            'sesame-seeds': 'SESAME',
            'mustard': 'MUSTARD',
            'celery': 'CELERY',
            'sulphites': 'SULPHITES',
            'sulfites': 'SULPHITES',
            'lupin': 'LUPIN',
        }
        
        allergens = set()
        
        # Check allergens field
        allergens_text = product.get('allergens', '').lower()
        if allergens_text:
            for keyword, standard_name in allergen_map.items():
                if keyword in allergens_text:
                    allergens.add(standard_name)
        
        # Check ingredients field for common allergen keywords
        ingredients = product.get('ingredients_text', '').lower()
        if ingredients:
            for keyword, standard_name in allergen_map.items():
                if keyword in ingredients:
                    allergens.add(standard_name)
        
        return sorted(list(allergens))
    
    def quick_detect(self, image_path: str) -> Optional[Dict]:
        """
        Quick detection pipeline: barcode → allergen lookup
        Returns allergen info without needing OCR.
        
        Args:
            image_path: Path to product image
            
        Returns:
            Dict with allergen info or None if barcode not detected/found
        """
        # Try to detect barcode
        barcode = self.detect_barcode_from_image(image_path)
        if not barcode:
            return None
        
        # Look up allergens
        result = self.lookup_allergens_by_barcode(barcode)
        return result


def main():
    """Test barcode detector."""
    import sys
    
    detector = BarcodeDetector()
    
    if len(sys.argv) > 1:
        # Test with barcode argument
        barcode = sys.argv[1]
        print(f"\nLooking up barcode: {barcode}")
        result = detector.lookup_allergens_by_barcode(barcode)
        
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Product not found for barcode: {barcode}")
    else:
        print("Usage: python barcode_detector.py <barcode>")
        print("Example: python barcode_detector.py 4006381333931")


if __name__ == "__main__":
    main()
