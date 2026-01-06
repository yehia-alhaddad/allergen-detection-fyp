"""
Google Gemini AI utilities for text cleaning and health recommendations.
"""
import os
import base64
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    MODEL_NAME = "gemini-1.5-flash"  # Fast and free tier
else:
    logger.warning("⚠️  GEMINI_API_KEY not set - AI features disabled")
    MODEL_NAME = None


def clean_ocr_text(corrupted_text: str, allergen_name: str) -> str:
    """
    Use Gemini to clean corrupted OCR text related to an allergen.
    
    Args:
        corrupted_text: The corrupted text from OCR (garbage characters, etc.)
        allergen_name: The allergen being referenced (e.g., "PEANUT", "MILK")
    
    Returns:
        Cleaned, readable text
    """
    if not MODEL_NAME:
        logger.warning("Gemini not configured - returning original text")
        return corrupted_text
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = f"""Clean up this corrupted OCR text. The text mentions the allergen '{allergen_name}'. 
Remove garbage characters, fix obvious typos, and return ONLY the cleaned text without explanation.

Corrupted text:
{corrupted_text}

Return only the cleaned text:"""
        
        response = model.generate_content(prompt)
        cleaned = response.text.strip()
        
        logger.info(f"✓ Cleaned text for {allergen_name}")
        return cleaned
    except Exception as e:
        logger.error(f"❌ Text cleaning failed: {e}")
        return corrupted_text


def get_health_recommendation(allergen_name: str, trigger_phrase: str) -> Dict[str, Any]:
    """
    Generate comprehensive health recommendations for an allergen.
    
    Args:
        allergen_name: The allergen (e.g., "PEANUT", "MILK")
        trigger_phrase: The text snippet where it was detected
    
    Returns:
        Dictionary with:
        - risk_level: 'low', 'moderate', 'high', 'critical'
        - symptoms: List of symptoms to watch for
        - immediate_actions: List of actions to take
        - when_to_seek_help: When to contact medical professionals
        - alternatives: Safe alternative products
        - summary: Short summary of the recommendation
    """
    if not MODEL_NAME:
        logger.warning("Gemini not configured - using default recommendation")
        return _default_recommendation(allergen_name)
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = f"""Provide health and safety information for someone with a {allergen_name} allergy 
who found this allergen in a product: "{trigger_phrase}"

Return a JSON response with these exact fields:
{{
  "risk_level": "low|moderate|high|critical",
  "symptoms": ["symptom1", "symptom2", ...] (list of 3-4 most common symptoms),
  "immediate_actions": ["action1", "action2", ...] (list of 3-4 immediate steps),
  "when_to_seek_help": "description of when to call doctor or emergency",
  "alternatives": ["alternative1", "alternative2", ...] (3-4 safe alternative products/ingredients),
  "summary": "1-2 sentence summary of the health concern"
}}

Return ONLY valid JSON, no other text."""
        
        response = model.generate_content(prompt)
        
        # Parse the response
        import json
        try:
            recommendation = json.loads(response.text)
            logger.info(f"✓ Generated recommendation for {allergen_name}")
            return recommendation
        except json.JSONDecodeError:
            logger.warning(f"Could not parse Gemini response - using defaults")
            return _default_recommendation(allergen_name)
            
    except Exception as e:
        logger.error(f"❌ Recommendation generation failed: {e}")
        return _default_recommendation(allergen_name)


def _default_recommendation(allergen_name: str) -> Dict[str, Any]:
    """Fallback recommendations when Gemini is unavailable."""
    
    recommendations = {
        'PEANUT': {
            'risk_level': 'high',
            'symptoms': ['Itching in mouth/throat', 'Swelling of lips/tongue', 'Hives', 'Anaphylaxis'],
            'immediate_actions': ['Stop eating immediately', 'Rinse mouth with water', 'Check for antihistamines', 'Monitor breathing'],
            'when_to_seek_help': 'Call emergency if swelling, difficulty breathing, or signs of anaphylaxis appear',
            'alternatives': ['Sunflower seed butter', 'Tahini (sesame)', 'Soy nut butter'],
            'summary': 'Peanut allergies can be severe. Avoid all peanut products and cross-contaminated items.'
        },
        'MILK': {
            'risk_level': 'moderate',
            'symptoms': ['Hives/skin reactions', 'Stomach pain', 'Vomiting', 'Anaphylaxis (rare)'],
            'immediate_actions': ['Stop consuming immediately', 'Drink water', 'Take antihistamine if available', 'Monitor symptoms'],
            'when_to_seek_help': 'Seek help if severe allergic reaction, persistent vomiting, or difficulty breathing',
            'alternatives': ['Almond milk', 'Oat milk', 'Soy milk', 'Coconut milk'],
            'summary': 'Milk allergies are common. Replace dairy with plant-based or lactose-free alternatives.'
        },
        'EGG': {
            'risk_level': 'moderate',
            'symptoms': ['Stomach cramps', 'Hives', 'Swelling', 'Anaphylaxis (rare)'],
            'immediate_actions': ['Stop eating', 'Wash hands and mouth', 'Take antihistamine', 'Monitor for reactions'],
            'when_to_seek_help': 'Call doctor if severe reaction, difficulty breathing, or signs of anaphylaxis',
            'alternatives': ['Applesauce', 'Flax eggs (1 tbsp flax + 3 tbsp water)', 'Chia eggs', 'Banana'],
            'summary': 'Egg allergies are manageable with proper ingredient checking. Many baking substitutes available.'
        },
        'GLUTEN': {
            'risk_level': 'moderate',
            'symptoms': ['Stomach pain', 'Bloating', 'Diarrhea', 'Fatigue'],
            'immediate_actions': ['Stop eating gluten-containing food', 'Drink water', 'Rest', 'Take antacid if needed'],
            'when_to_seek_help': 'Contact doctor if severe symptoms persist or if celiac disease is suspected',
            'alternatives': ['Rice flour', 'Almond flour', 'Gluten-free oats', 'Corn flour'],
            'summary': 'Celiac disease and gluten sensitivity affect digestion. Stick to certified gluten-free products.'
        },
        'SHELLFISH': {
            'risk_level': 'high',
            'symptoms': ['Itching in mouth', 'Swelling of lips', 'Hives', 'Anaphylaxis'],
            'immediate_actions': ['Stop eating immediately', 'Rinse mouth', 'Take antihistamine', 'Check EpiPen if available'],
            'when_to_seek_help': 'Call emergency if swelling or difficulty breathing occurs',
            'alternatives': ['Fish (if not allergic)', 'Mushrooms', 'Hearts of palm', 'Tofu'],
            'summary': 'Shellfish allergies can be severe. Avoid all shellfish and cross-contaminated seafood.'
        },
        'TREE_NUT': {
            'risk_level': 'high',
            'symptoms': ['Itching/swelling in mouth', 'Hives', 'Wheezing', 'Anaphylaxis'],
            'immediate_actions': ['Stop eating', 'Rinse mouth', 'Take antihistamine', 'Have EpiPen ready'],
            'when_to_seek_help': 'Call emergency if breathing difficulty or anaphylaxis symptoms appear',
            'alternatives': ['Seeds (sunflower, pumpkin)', 'Coconut', 'Legumes (if not allergic)'],
            'summary': 'Tree nut allergies are serious. Check all processed foods for traces.'
        },
        'SOY': {
            'risk_level': 'low',
            'symptoms': ['Itching in mouth', 'Hives', 'Stomach discomfort', 'Anaphylaxis (rare)'],
            'immediate_actions': ['Stop consuming', 'Drink water', 'Take antihistamine if available'],
            'when_to_seek_help': 'Contact doctor if severe reaction or anaphylaxis signs appear',
            'alternatives': ['Chickpea-based products', 'Lentil-based products', 'Pea protein', 'Sesame'],
            'summary': 'Soy allergy is usually mild. Check ingredient labels for soy lecithin and soy oil.'
        },
        'FISH': {
            'risk_level': 'high',
            'symptoms': ['Itching in mouth', 'Swelling', 'Hives', 'Anaphylaxis'],
            'immediate_actions': ['Stop eating immediately', 'Rinse mouth', 'Take antihistamine', 'Check EpiPen'],
            'when_to_seek_help': 'Call emergency if swelling, difficulty breathing, or anaphylaxis occurs',
            'alternatives': ['Mushrooms', 'Hearts of palm', 'Tofu', 'Legumes'],
            'summary': 'Fish allergies can be serious. Avoid all fish and cross-contaminated seafood products.'
        },
        'SESAME': {
            'risk_level': 'moderate',
            'symptoms': ['Oral itching', 'Hives', 'Stomach pain', 'Anaphylaxis (rare)'],
            'immediate_actions': ['Stop eating', 'Drink water', 'Take antihistamine if needed'],
            'when_to_seek_help': 'Contact doctor if severe reaction occurs',
            'alternatives': ['Sunflower seed butter', 'Tahini from other sources', 'Soy sauce (some brands)', 'Coconut oil'],
            'summary': 'Sesame allergies are becoming more common. Check labels for sesame oil and tahini.'
        },
    }
    
    return recommendations.get(allergen_name, {
        'risk_level': 'moderate',
        'symptoms': ['Allergic reaction symptoms'],
        'immediate_actions': ['Stop eating the product', 'Drink water', 'Monitor symptoms'],
        'when_to_seek_help': 'Seek medical help if severe symptoms develop',
        'alternatives': ['Consult with allergen specialist'],
        'summary': f'{allergen_name} allergy detected. Consult medical professional for personalized advice.'
    })


def analyze_image_for_context(image_base64: str, allergen_name: str) -> str:
    """
    Analyze product image to get more context about the allergen.
    Optional: Can be used to provide more accurate recommendations.
    
    Args:
        image_base64: Base64 encoded image
        allergen_name: The allergen to focus on
    
    Returns:
        Context description from the image
    """
    if not MODEL_NAME:
        return ""
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Convert base64 to image bytes
        image_data = base64.b64decode(image_base64)
        
        prompt = f"""Look at this product label. Find where it mentions '{allergen_name}' 
and describe the context (Is it in ingredients? In warnings? In facility information?).
Be brief - 1-2 sentences."""
        
        response = model.generate_content([
            {
                "mime_type": "image/jpeg",
                "data": image_base64,
            },
            prompt
        ])
        
        return response.text.strip()
    except Exception as e:
        logger.error(f"❌ Image analysis failed: {e}")
        return ""
