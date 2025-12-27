from typing import Optional, List, Tuple, Dict, Any
import traceback
import sys
from pathlib import Path

# Add src to path if not already there
_src = Path(__file__).parent.parent
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from ocr.easyocr_extractor import EasyOCREngine
import importlib
from preprocessing.ocr_preprocessor import generate_preprocessed_variants
from ocr.ocr_postprocessor import clean_text, normalize_ocr_noise, quality_score


class HybridOCREngine:
    def __init__(
        self,
        lang_list: Optional[list[str]] = None,
        try_easyocr: bool = True,
        try_tesseract: bool = True,
        tesseract_cmd: Optional[str] = None,
    ) -> None:
        self.errors: List[str] = []
        self._engines: List[Tuple[str, Any]] = []

        if try_easyocr:
            try:
                self._engines.append(("easyocr", EasyOCREngine(lang_list=lang_list)))
            except Exception as e:
                self.errors.append(f"easyocr init failed: {e}")

        if try_tesseract:
            try:
                from ocr.tesseract_extractor import TesseractOCR
                self._engines.append(("tesseract", TesseractOCR(tesseract_cmd=tesseract_cmd, lang="eng")))
            except Exception as e:
                self.errors.append(f"tesseract init failed: {e}")

    def _extract_with_engine(self, engine_name: str, engine: Any, image) -> tuple[str, float]:
        """Extract text with optional confidence if engine supports it."""
        try:
            if hasattr(engine, 'extract_with_confidence'):
                text, conf = engine.extract_with_confidence(image)
                return text, conf
            else:
                text = engine.extract(image)
                return text, 0.5  # Default confidence for engines without confidence scoring
        except Exception as e:
            self.errors.append(f"{engine_name} extract failed: {e}\n{traceback.format_exc()}")
            return "", 0.0

    def extract_with_meta(self, image) -> Dict[str, Any]:
        """Extract text trying multiple variants and engines, return best result with metadata."""
        variants = generate_preprocessed_variants(image)
        best = {"text": "", "score": -1.0, "confidence": 0.0, "engine": None, "variant": None}
        
        for vname, vimg in variants:
            for ename, eng in self._engines:
                raw, conf = self._extract_with_engine(ename, eng, vimg)
                txt = normalize_ocr_noise(clean_text(raw))
                q_score = quality_score(txt)
                
                # Combined score: quality (70%) + OCR confidence (30%)
                combined_score = (q_score * 0.7) + (conf * 0.3)
                
                # Select best by combined score, then length as tiebreaker
                if combined_score > best["score"] or (combined_score == best["score"] and len(txt) > len(best["text"])):
                    best = {
                        "text": txt, 
                        "score": combined_score,
                        "quality_score": q_score,
                        "confidence": conf,
                        "engine": ename, 
                        "variant": vname
                    }
        
        return best

    def extract(self, image) -> str:
        """Extract text using best variant and engine combination."""
        return self.extract_with_meta(image).get("text", "")
