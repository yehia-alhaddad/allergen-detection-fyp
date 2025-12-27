"""
Optimized OCR extractor that uses simple preprocessing for best results.
This replaces the complex hybrid approach which was over-processing images.
"""
from typing import Optional, Dict, Any
import cv2
import numpy as np

class SimpleOCREngine:
    """Simplified OCR engine that works better than multi-pass preprocessing."""
    
    def __init__(
        self, 
        lang_list: Optional[list[str]] = None,
        gpu: bool = False
    ):
        self.lang_list = lang_list or ["en"]
        self.gpu = gpu
        self._reader = None
    
    def _ensure_reader(self):
        if self._reader is None:
            import easyocr
            self._reader = easyocr.Reader(self.lang_list, gpu=self.gpu)
    
    def _simple_preprocess(self, image: np.ndarray) -> np.ndarray:
        """Light preprocessing - just grayscale and minimal contrast boost."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Very light CLAHE to avoid distortion
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        return clahe.apply(gray)
    
    def extract(self, image) -> str:
        """Extract text with minimal preprocessing."""
        self._ensure_reader()
        
        # Try original image first (EasyOCR handles it well)
        try:
            result_original = self._reader.readtext(
                image,
                detail=0,
                paragraph=True,
                contrast_ths=0.5,
                adjust_contrast=0.5,
                mag_ratio=1.0
            )
            text_original = "\n".join(result_original)
        except Exception:
            text_original = ""
        
        # If too short, try with light preprocessing
        if len(text_original) < 20:
            try:
                preprocessed = self._simple_preprocess(image)
                result_prep = self._reader.readtext(
                    preprocessed,
                    detail=0,
                    paragraph=True,
                    contrast_ths=0.5,
                    adjust_contrast=0.5,
                    mag_ratio=1.0
                )
                text_prep = "\n".join(result_prep)
                
                # Use whichever is longer
                if len(text_prep) > len(text_original):
                    return text_prep
            except Exception:
                pass
        
        return text_original
    
    def extract_with_confidence(self, image) -> tuple[str, float]:
        """Extract text with confidence scores."""
        self._ensure_reader()
        
        # Try original first
        try:
            result = self._reader.readtext(
                image,
                detail=1,
                paragraph=False,
                contrast_ths=0.5,
                adjust_contrast=0.5,
                mag_ratio=1.0
            )
            
            if not result:
                return "", 0.0
            
            texts = [item[1] for item in result]
            confidences = [item[2] for item in result]
            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
            
            return "\n".join(texts), avg_conf
        except Exception:
            return "", 0.0

    def read_boxes(self, image):
        """
        Return EasyOCR detailed results including bounding boxes for layout parsing.
        Each item is a tuple: (bbox, text, confidence)
        """
        self._ensure_reader()
        try:
            result = self._reader.readtext(
                image,
                detail=1,
                paragraph=False,
                contrast_ths=0.5,
                adjust_contrast=0.5,
                mag_ratio=1.0
            )
            return result or []
        except Exception:
            return []
