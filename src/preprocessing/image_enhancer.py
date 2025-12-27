from typing import Any, Optional
import cv2
import numpy as np


def _unsharp_mask(image: np.ndarray, sigma: float = 1.0, strength: float = 1.5) -> np.ndarray:
    """Apply unsharp masking to sharpen text."""
    blurred = cv2.GaussianBlur(image, (0, 0), sigma)
    sharpened = cv2.addWeighted(image, 1.0 + strength, blurred, -strength, 0)
    return sharpened


def _detect_and_correct_skew(image: np.ndarray, max_angle: float = 10.0) -> np.ndarray:
    """Detect and correct skew angle for better OCR."""
    try:
        coords = np.column_stack(np.where(image > 0))
        if len(coords) < 10:
            return image
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        if abs(angle) < max_angle and abs(angle) > 0.5:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated
    except Exception:
        pass
    return image


def _adaptive_contrast(gray: np.ndarray) -> np.ndarray:
    """Apply adaptive CLAHE based on image statistics."""
    mean_val = np.mean(gray)
    std_val = np.std(gray)
    
    if std_val < 30:  # Very low contrast
        clip_limit = 3.0
        tile_size = (4, 4)
    elif std_val < 50:  # Low contrast
        clip_limit = 2.5
        tile_size = (8, 8)
    else:  # Normal/high contrast
        clip_limit = 2.0
        tile_size = (8, 8)
    
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
    return clahe.apply(gray)


def _smart_binarize(gray: np.ndarray) -> np.ndarray:
    """Apply Otsu or adaptive threshold based on image characteristics."""
    mean_val = np.mean(gray)
    
    # Try Otsu for uniform lighting
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Adaptive for uneven lighting
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 31, 5)
    
    # Use adaptive if image has uneven lighting (high variance in local means)
    regions = [
        gray[i:i+50, j:j+50]
        for i in range(0, gray.shape[0] - 50, 50)
        for j in range(0, gray.shape[1] - 50, 50)
    ]
    if regions:
        local_means = [np.mean(r) for r in regions if r.size > 0]
        if len(local_means) > 1 and np.std(local_means) > 20:
            return adaptive
    
    return otsu


def enhance_image(image: np.ndarray, *, denoise: bool = True, contrast: bool = True, binarize: bool = True, sharpen: bool = False, deskew: bool = False) -> np.ndarray:
    """Apply advanced enhancements to improve OCR performance.

    Args:
        image: Input BGR image as numpy array.
        denoise: Apply bilateral filter to reduce noise.
        contrast: Apply adaptive CLAHE for contrast enhancement.
        binarize: Apply smart binarization (Otsu or adaptive).
        sharpen: Apply unsharp masking for text sharpening.
        deskew: Detect and correct skew angle.

    Returns:
        Enhanced grayscale or binary image.
    """
    if image is None:
        raise ValueError("image is None")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()

    if sharpen:
        gray = _unsharp_mask(gray, sigma=1.0, strength=1.2)

    if denoise:
        gray = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

    if contrast:
        gray = _adaptive_contrast(gray)

    if binarize:
        gray = _smart_binarize(gray)
        if deskew:
            gray = _detect_and_correct_skew(gray, max_angle=10.0)
    
    return gray
