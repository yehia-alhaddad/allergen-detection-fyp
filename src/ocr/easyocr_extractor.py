from typing import Optional


class EasyOCREngine:
    def __init__(
        self, 
        lang_list: Optional[list[str]] = None,
        gpu: bool = False,
        contrast_ths: float = 0.3,
        adjust_contrast: float = 0.7,
        mag_ratio: float = 1.5,
    ):
        self.lang_list = lang_list or ["en"]
        self.gpu = gpu
        self.contrast_ths = contrast_ths
        self.adjust_contrast = adjust_contrast
        self.mag_ratio = mag_ratio
        self._reader = None

    def _ensure_reader(self):
        if self._reader is None:
            import easyocr
            self._reader = easyocr.Reader(self.lang_list, gpu=self.gpu)

    def extract(self, image) -> str:
        self._ensure_reader()
        result = self._reader.readtext(
            image, 
            detail=0, 
            paragraph=True,
            contrast_ths=self.contrast_ths,
            adjust_contrast=self.adjust_contrast,
            mag_ratio=self.mag_ratio,
        )
        return "\n".join(result)
    
    def extract_with_confidence(self, image) -> tuple[str, float]:
        """Extract text with average confidence score."""
        self._ensure_reader()
        result = self._reader.readtext(
            image,
            detail=1,
            paragraph=False,
            contrast_ths=self.contrast_ths,
            adjust_contrast=self.adjust_contrast,
            mag_ratio=self.mag_ratio,
        )
        if not result:
            return "", 0.0
        
        texts = [item[1] for item in result]
        confidences = [item[2] for item in result]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        
        return "\n".join(texts), avg_conf
