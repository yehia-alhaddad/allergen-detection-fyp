from typing import Optional
import pytesseract
import cv2


class TesseractOCR:
    def __init__(self, tesseract_cmd: Optional[str] = None, lang: str = "eng"):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.lang = lang

    def extract(self, image) -> str:
        if image is None:
            raise ValueError("image is None")
        if isinstance(image, str):
            img = cv2.imread(image)
        else:
            img = image
        return pytesseract.image_to_string(img, lang=self.lang)
