from typing import Dict, Any, List, Tuple
import cv2
import numpy as np

from .image_enhancer import enhance_image


def prepare_for_ocr(image: np.ndarray, *, params: Dict[str, Any] | None = None) -> np.ndarray:
    """Preprocess image with OCR-friendly settings.

    Args:
        image: Input BGR or grayscale image.
        params: Optional overrides for enhance_image options.
    """
    params = params or {}
    return enhance_image(
        image,
        denoise=params.get("denoise", True),
        contrast=params.get("contrast", True),
        binarize=params.get("binarize", True),
    )


def _resize(img: np.ndarray, scale: float) -> np.ndarray:
    if abs(scale - 1.0) < 1e-3:
        return img
    h, w = img.shape[:2]
    return cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)


def generate_preprocessed_variants(image: np.ndarray) -> List[Tuple[str, np.ndarray]]:
    """Generate multiple preprocessing variants for robust OCR."""
    variants: List[Tuple[str, np.ndarray]] = []
    
    # Core variants with different enhancement combinations
    base_default = enhance_image(image, denoise=True, contrast=True, binarize=True)
    base_soft = enhance_image(image, denoise=True, contrast=True, binarize=False)
    base_sharp = enhance_image(image, denoise=True, contrast=True, binarize=True, sharpen=True)
    base_deskew = enhance_image(image, denoise=True, contrast=True, binarize=True, deskew=True)
    
    variants.extend([
        ("default", base_default),
        ("soft", base_soft),
        ("sharp", base_sharp),
        ("deskew", base_deskew),
    ])

    # Light preprocessing for high-quality images
    light = enhance_image(image, denoise=False, contrast=True, binarize=False)
    variants.append(("light", light))

    # Aggressive contrast + sharpening for low-quality
    aggressive = enhance_image(image, denoise=True, contrast=True, binarize=True, sharpen=True, deskew=True)
    variants.append(("aggressive", aggressive))

    # Morphological cleanup on default binary
    kernel = np.ones((2, 2), np.uint8)
    opened = cv2.morphologyEx(base_default, cv2.MORPH_OPEN, kernel, iterations=1)
    closed = cv2.morphologyEx(base_default, cv2.MORPH_CLOSE, kernel, iterations=1)
    variants.extend([
        ("opened", opened),
        ("closed", closed),
    ])

    # Upscaled versions for small text
    for s in (1.5, 2.0):
        variants.append((f"default_x{s}", _resize(base_default, s)))
        variants.append((f"sharp_x{s}", _resize(base_sharp, s)))
        
    # Inverted (white text on dark background)
    inverted = cv2.bitwise_not(base_default)
    variants.append(("inverted", inverted))

    return variants
