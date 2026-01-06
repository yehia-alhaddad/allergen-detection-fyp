"""
Enhanced allergen detection with Gemini AI for text cleaning and health recommendations.
Wraps the StrictAllergenDetector with additional AI capabilities.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from src.allergen_detection.strict_detector import StrictAllergenDetector, DetectedAllergen
from src.utils.gemini_ai import (
    clean_ocr_text,
    get_health_recommendation
)

logger = logging.getLogger(__name__)


async def enhance_allergen_detection(
    detection_result: Dict[str, List[DetectedAllergen]],
    raw_text: str,
    image_base64: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enhance allergen detection results with Gemini AI.
    - Cleans corrupted OCR text in trigger phrases
    - Generates health recommendations for each allergen
    - Provides context and severity information
    
    Args:
        detection_result: Output from StrictAllergenDetector.detect()
        raw_text: Original OCR text (may be corrupted)
        image_base64: Optional base64 encoded image for context
    
    Returns:
        Enhanced detection result with cleaned text and recommendations
    """
    
    enhanced_result = {
        "contains": [],
        "may_contain": [],
        "not_detected": [],
        "summary": {}
    }
    
    # Process CONTAINS allergens
    for allergen in detection_result.get('contains', []):
        enhanced_allergen = await _enhance_single_allergen(
            allergen,
            raw_text,
            image_base64,
            is_contains=True
        )
        enhanced_result["contains"].append(enhanced_allergen)
    
    # Process MAY_CONTAIN allergens
    for allergen in detection_result.get('may_contain', []):
        enhanced_allergen = await _enhance_single_allergen(
            allergen,
            raw_text,
            image_base64,
            is_contains=False
        )
        enhanced_result["may_contain"].append(enhanced_allergen)
    
    # Process NOT_DETECTED (no enhancement needed)
    for allergen in detection_result.get('not_detected', []):
        enhanced_result["not_detected"].append(allergen.name)
    
    # Summary
    enhanced_result["summary"] = {
        "contains_count": len(enhanced_result["contains"]),
        "may_contain_count": len(enhanced_result["may_contain"]),
        "total_detected": len(enhanced_result["contains"]) + len(enhanced_result["may_contain"]),
        "has_health_recommendations": True,
        "has_cleaned_text": True
    }
    
    return enhanced_result


async def _enhance_single_allergen(
    allergen: DetectedAllergen,
    raw_text: str,
    image_base64: Optional[str],
    is_contains: bool
) -> Dict[str, Any]:
    """
    Enhance a single allergen detection with AI processing.
    
    Returns dictionary with:
    - allergen: name
    - evidence: original evidence
    - cleaned_trigger_phrase: AI-cleaned text
    - keyword: matched keyword
    - confidence: confidence score
    - health_recommendation: health info
    - severity: risk level
    """
    
    try:
        # Run text cleaning and health recommendation concurrently
        cleaned_text_task = asyncio.create_task(
            asyncio.to_thread(clean_ocr_text, allergen.evidence, allergen.name)
        )
        recommendation_task = asyncio.create_task(
            asyncio.to_thread(get_health_recommendation, allergen.name, allergen.evidence)
        )
        
        cleaned_text = await cleaned_text_task
        recommendation = await recommendation_task
        
        return {
            "allergen": allergen.name,
            "evidence": allergen.evidence,
            "cleaned_trigger_phrase": cleaned_text,
            "keyword": allergen.matched_keyword,
            "confidence": round(allergen.confidence, 2),
            "category": "CONTAINS" if is_contains else "MAY_CONTAIN",
            "health_recommendation": {
                "severity": recommendation.get("risk_level", "moderate"),
                "symptoms": recommendation.get("symptoms", []),
                "immediate_actions": recommendation.get("immediate_actions", []),
                "when_to_seek_help": recommendation.get("when_to_seek_help", ""),
                "alternatives": recommendation.get("alternatives", []),
                "summary": recommendation.get("summary", "")
            }
        }
    
    except Exception as e:
        logger.error(f"Error enhancing allergen {allergen.name}: {e}")
        # Return minimal enhancement without AI if processing fails
        return {
            "allergen": allergen.name,
            "evidence": allergen.evidence,
            "cleaned_trigger_phrase": allergen.evidence,  # Fallback to original
            "keyword": allergen.matched_keyword,
            "confidence": round(allergen.confidence, 2),
            "category": "CONTAINS" if is_contains else "MAY_CONTAIN",
            "health_recommendation": None,  # No recommendation if AI fails
            "ai_processing_failed": True
        }


def format_enhanced_for_response(enhanced_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format enhanced allergen detection for API response.
    
    Converts from internal format to API response format.
    """
    return {
        "contains": enhanced_result["contains"],
        "may_contain": enhanced_result["may_contain"],
        "not_detected": enhanced_result["not_detected"],
        "summary": enhanced_result["summary"]
    }
