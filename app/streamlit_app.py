"""
Professional Allergen Detection Web Application
A modern, user-friendly interface for detecting allergens in food product labels.
"""

import os
import io
import json
import requests
import streamlit as st
from PIL import Image
import time

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
HEALTH_ENDPOINT = f"{API_URL}/health"
DETECT_ENDPOINT = f"{API_URL}/detect"
DETECT_TEXT_ENDPOINT = f"{API_URL}/detect-text"

# Page Configuration - must be first Streamlit command
st.set_page_config(
    page_title="Allergen Detection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Allergen Detection System powered by AI/ML"
    }
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #FF6B6B;
        --secondary-color: #4ECDC4;
        --bg-color: #F7F9FC;
        --text-color: #2C3E50;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: white !important;
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* Card styling */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Allergen badge styling */
    .allergen-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .allergen-high {
        background-color: #ff4444;
        color: white;
    }
    
    .allergen-medium {
        background-color: #ffaa00;
        color: white;
    }
    
    .allergen-low {
        background-color: #00C851;
        color: white;
    }
    
    /* Status indicators */
    .status-online {
        color: #00C851;
        font-weight: bold;
    }
    
    .status-offline {
        color: #ff4444;
        font-weight: bold;
    }
    
    /* Feature boxes */
    .feature-box {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .feature-box h3 {
        color: #667eea;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🔍 AI-Powered Allergen Detection System</h1>
    <p>Identify allergens in food products instantly using advanced machine learning</p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
# Sidebar for configuration and system status
with st.sidebar:
    st.markdown("## ⚙️ System Configuration")
    
    # API Configuration
    with st.expander("🔌 API Settings", expanded=True):
        api_url = st.text_input(
            "API Base URL",
            value=API_URL,
            help="Enter the FastAPI server address"
        )
        HEALTH_URL = f"{api_url}/health"
        DETECT_URL = f"{api_url}/detect"
        DETECT_TEXT_URL = f"{api_url}/detect-text"
    
    # System Status Check
    st.markdown("### 🏥 System Health")
    
    # Initialize session state for health status
    if 'health_status' not in st.session_state:
        st.session_state.health_status = None
        st.session_state.last_check = None
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🔄 Check Status", use_container_width=True):
            try:
                with st.spinner("Checking..."):
                    resp = requests.get(HEALTH_URL, timeout=5)
                    if resp.ok:
                        st.session_state.health_status = "online"
                        st.session_state.health_data = resp.json()
                        st.session_state.last_check = time.strftime("%H:%M:%S")
                    else:
                        st.session_state.health_status = "error"
                        st.session_state.health_data = f"Status {resp.status_code}"
            except Exception as exc:
                st.session_state.health_status = "offline"
                st.session_state.health_data = str(exc)
    
    with col2:
        if st.session_state.health_status == "online":
            st.success("✅ Online")
        elif st.session_state.health_status == "offline":
            st.error("❌ Offline")
        elif st.session_state.health_status == "error":
            st.warning("⚠️ Error")
        else:
            st.info("🔘 Unknown")
    
    if st.session_state.last_check:
        st.caption(f"Last checked: {st.session_state.last_check}")
    
    # Information about allergen categories
    st.markdown("---")
    st.markdown("### 📋 Detected Allergen Categories")
    st.markdown("""
    <div style='font-size: 0.85rem; line-height: 1.6;'>
    The system can identify these common allergens:
    <ul>
    <li>🌾 <b>Gluten</b> (wheat, rye, barley)</li>
    <li>🥛 <b>Milk</b> & dairy products</li>
    <li>🥚 <b>Eggs</b></li>
    <li>🥜 <b>Peanuts</b></li>
    <li>🌰 <b>Tree Nuts</b> (almonds, cashews, etc.)</li>
    <li>🦐 <b>Shellfish</b></li>
    <li>🐟 <b>Fish</b></li>
    <li>🌱 <b>Soy</b></li>
    <li>🌿 <b>Sesame</b></li>
    <li>🦪 <b>Molluscs</b></li>
    <li>🥬 <b>Celery</b></li>
    <li>🌶️ <b>Mustard</b></li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ℹ️ How to Use")
    st.markdown("""
    <div style='font-size: 0.85rem; line-height: 1.6;'>
    <b>Method 1: Image Upload</b><br>
    1. Upload a photo of ingredient label<br>
    2. Enable OCR to extract text<br>
    3. Click "Analyze Image"<br><br>
    
    <b>Method 2: Text Input</b><br>
    1. Copy ingredient list from package<br>
    2. Paste into text area<br>
    3. Click "Analyze Text"<br>
    </div>
    """, unsafe_allow_html=True)

# ==================== MAIN CONTENT ====================

# Feature Overview Section
st.markdown("## 🌟 Key Features")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>📸 Image Recognition</h3>
        <p>Upload photos of ingredient labels and extract text automatically using OCR technology</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>🤖 AI Detection</h3>
        <p>Advanced NER model identifies allergens with confidence scores</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-box">
        <h3>⚡ Instant Results</h3>
        <p>Get comprehensive allergen analysis in seconds</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs for different detection methods
tab_image, tab_text, tab_batch = st.tabs([
    "📷 Image Analysis",
    "📝 Text Analysis",
    "📊 About & Statistics"
])

# ==================== HELPER FUNCTIONS ====================

def get_allergen_severity(confidence):
    """Determine severity level based on confidence score."""
    if confidence >= 0.8:
        return "high", "allergen-high"
    elif confidence >= 0.5:
        return "medium", "allergen-medium"
    else:
        return "low", "allergen-low"

def render_results(data: dict):
    """
    Render detection results in a professional format.
    
    Components explained:
    - Summary Metrics: Quick overview of detection success and performance
    - Detected Allergens: Visual badges showing found allergens with confidence
    - Detailed Breakdown: Entity-level information with text spans
    - Performance Timing: How long each pipeline stage took
    """
    if not data:
        st.warning("⚠️ No data returned from API")
        return
    
    # Success indicator
    if data.get("success"):
        st.success("✅ Analysis completed successfully!")
    else:
        st.error("❌ Analysis encountered issues")
    
    # Summary metrics in columns
    st.markdown("### 📊 Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Success Rate",
            value="100%" if data.get("success") else "0%",
            delta=None
        )
    
    with col2:
        avg_conf = data.get('avg_confidence', 0)
        st.metric(
            label="Avg Confidence",
            value=f"{avg_conf:.1%}",
            delta=None
        )
    
    with col3:
        allergen_count = len(data.get('detected_allergens', {}))
        st.metric(
            label="Allergens Found",
            value=allergen_count,
            delta=None
        )
    
    with col4:
        total_time = data.get('timings', {}).get('total', 0)
        st.metric(
            label="Processing Time",
            value=f"{total_time:.2f}s",
            delta=None
        )
    
    st.markdown("---")
    
    # Detected Allergens Section - Most Important
    detected = data.get("detected_allergens") or {}
    if detected:
        st.markdown("### 🚨 Detected Allergens")
        st.markdown("**The following allergens were identified in this product:**")
        
        for allergen, items in detected.items():
            # Get max confidence for this allergen category
            max_conf = max([item.get('confidence', 0) for item in items])
            severity, badge_class = get_allergen_severity(max_conf)
            
            # Create expandable section for each allergen
            with st.expander(f"**{allergen.upper()}** - {len(items)} occurrence(s) found", expanded=True):
                st.markdown(f"""
                <div class='allergen-badge {badge_class}'>
                    {allergen.replace('_', ' ').title()} - Confidence: {max_conf:.1%}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**Detected instances:**")
                for idx, item in enumerate(items, 1):
                    conf = item.get('confidence', 0)
                    text = item.get('text', 'N/A')
                    label = item.get('label', 'N/A')
                    
                    st.markdown(f"""
                    - **Instance {idx}**: "{text}" 
                      - Label: `{label}` 
                      - Confidence: {conf:.1%}
                    """)
    else:
        st.success("✅ **No allergens detected** - This product appears to be safe based on the ingredient list provided.")
    
    st.markdown("---")
    
    # Text extraction results
    with st.expander("📄 Text Extraction", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Raw OCR Text:**")
            raw_text = data.get("raw_text", "N/A")
            st.text_area(
                "Raw text from image",
                value=raw_text,
                height=150,
                disabled=True,
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**Cleaned Text:**")
            cleaned_text = data.get("cleaned_text", "N/A")
            st.text_area(
                "Processed text",
                value=cleaned_text,
                height=150,
                disabled=True,
                label_visibility="collapsed"
            )
    
    # Entity-level details
    entities = data.get("entities_found") or []
    if entities:
        with st.expander(f"🔍 Entity Details ({len(entities)} entities found)", expanded=False):
            st.markdown("Raw entities detected by the NER model:")
            
            entity_data = []
            for ent in entities:
                if len(ent) == 3:
                    text_span, label, conf = ent
                    entity_data.append({
                        "Text": text_span,
                        "Label": label,
                        "Confidence": f"{conf:.1%}"
                    })
            
            if entity_data:
                st.table(entity_data)
    
    # Performance timing breakdown
    with st.expander("⏱️ Performance Breakdown", expanded=False):
        timings = data.get("timings", {})
        if timings:
            st.markdown("Time taken for each pipeline stage:")
            
            timing_cols = st.columns(len(timings))
            for idx, (stage, duration) in enumerate(timings.items()):
                with timing_cols[idx]:
                    st.metric(
                        label=stage.replace('_', ' ').title(),
                        value=f"{duration:.3f}s"
                    )
        else:
            st.info("No timing data available")

# ==================== IMAGE ANALYSIS TAB ====================
with tab_image:
    st.markdown("### 📸 Upload Product Image")
    st.markdown("""
    Upload a clear photo of the ingredient label from a food product. The system will:
    1. **Extract text** from the image using OCR (Optical Character Recognition)
    2. **Clean and process** the extracted text
    3. **Identify allergens** using AI-powered Named Entity Recognition
    4. **Display results** with confidence scores
    """)
    
    # Settings
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=["jpg", "jpeg", "png"],
            help="Supported formats: JPG, JPEG, PNG"
        )
    
    with col2:
        use_ocr = st.checkbox(
            "Enable OCR",
            value=True,
            help="Extract text from image automatically"
        )
    
    # Display uploaded image
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            
            # Show image preview
            st.markdown("#### 🖼️ Image Preview")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # File information
            with st.expander("📁 File Information"):
                file_details = {
                    "Filename": uploaded_file.name,
                    "File Size": f"{uploaded_file.size / 1024:.2f} KB",
                    "Image Type": uploaded_file.type,
                    "Image Dimensions": f"{image.size[0]} x {image.size[1]} pixels"
                }
                for key, value in file_details.items():
                    st.text(f"{key}: {value}")
            
            st.markdown("---")
            
            # Analysis button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                analyze_btn = st.button(
                    "🔍 Analyze Image",
                    type="primary",
                    use_container_width=True
                )
            
            if analyze_btn:
                with st.spinner("🔄 Processing image... This may take a few seconds..."):
                    try:
                        # Prepare request
                        files = {
                            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "image/jpeg")
                        }
                        data = {"use_ocr": json.dumps(use_ocr)}
                        
                        # Make API call
                        start_time = time.time()
                        resp = requests.post(DETECT_URL, files=files, data=data, timeout=60)
                        elapsed = time.time() - start_time
                        
                        if resp.ok:
                            st.balloons()  # Celebration animation
                            st.success(f"✅ Analysis completed in {elapsed:.2f} seconds!")
                            render_results(resp.json())
                        else:
                            st.error(f"❌ API Error {resp.status_code}")
                            st.code(resp.text)
                    
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Request timed out. The server might be busy or down.")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Cannot connect to API server. Make sure it's running!")
                    except Exception as exc:
                        st.error(f"❌ Unexpected error: {exc}")
        
        except Exception as e:
            st.error(f"❌ Error loading image: {e}")
    
    else:
        # Placeholder when no image uploaded
        st.info("👆 Upload an image above to get started")
        
        # Example section
        with st.expander("💡 Tips for Best Results"):
            st.markdown("""
            - **Use clear, well-lit photos** of ingredient labels
            - **Ensure text is readable** and not blurry
            - **Avoid glare or shadows** on the label
            - **Capture the entire ingredient list** in the frame
            - **Hold camera steady** to avoid motion blur
            """)

# ==================== TEXT ANALYSIS TAB ====================
with tab_text:
    st.markdown("### 📝 Enter Ingredient Text")
    st.markdown("""
    If you already have the ingredient list as text, paste it here. This method:
    - **Skips OCR** for faster processing
    - **Works with copied text** from websites or digital labels
    - **Gives same accurate results** as image analysis
    """)
    
    # Text input
    text_input = st.text_area(
        "Ingredient List",
        height=200,
        placeholder="Example: Contains: Wheat flour, milk powder, eggs, peanuts, soy lecithin, tree nuts (almonds)",
        help="Paste or type the ingredient list from the product"
    )
    
    # Sample texts for quick testing
    with st.expander("📋 Try Sample Texts"):
        sample_texts = {
            "Sample 1 - Multiple Allergens": "Ingredients: Wheat flour, whole milk powder, fresh eggs, roasted peanuts, soy lecithin, almond pieces, fish sauce",
            "Sample 2 - Dairy Product": "Contains: Fresh milk, cream, whey protein, lactose, milk solids",
            "Sample 3 - Shellfish Warning": "May contain traces of shrimp, crab, lobster and other crustaceans",
            "Sample 4 - Gluten Free": "Ingredients: Rice flour, corn starch, potato starch, vegetable oil, salt, sugar"
        }
        
        for sample_name, sample_text in sample_texts.items():
            if st.button(f"Load: {sample_name}", key=f"sample_{sample_name}"):
                st.session_state.text_input = sample_text
                st.rerun()
    
    # Use session state if available
    if 'text_input' in st.session_state:
        text_input = st.session_state.text_input
    
    st.markdown("---")
    
    # Analysis button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_text_btn = st.button(
            "🔍 Analyze Text",
            type="primary",
            use_container_width=True,
            disabled=not text_input.strip()
        )
    
    if analyze_text_btn and text_input.strip():
        with st.spinner("🔄 Analyzing text..."):
            try:
                start_time = time.time()
                resp = requests.post(
                    DETECT_TEXT_URL,
                    params={"text": text_input},
                    timeout=30
                )
                elapsed = time.time() - start_time
                
                if resp.ok:
                    st.balloons()
                    st.success(f"✅ Analysis completed in {elapsed:.2f} seconds!")
                    render_results(resp.json())
                else:
                    st.error(f"❌ API Error {resp.status_code}")
                    st.code(resp.text)
            
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to API server")
            except Exception as exc:
                st.error(f"❌ Error: {exc}")
    
    elif analyze_text_btn:
        st.warning("⚠️ Please enter some text first")

# ==================== ABOUT TAB ====================
with tab_batch:
    st.markdown("### 📊 System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='info-card'>
        <h4>🎯 Project Overview</h4>
        <p>This is an <b>AI-powered allergen detection system</b> designed to help consumers 
        quickly identify allergens in food products.</p>
        
        <h4>🔬 Technology Stack</h4>
        <ul>
        <li><b>Frontend:</b> Streamlit (Python web framework)</li>
        <li><b>Backend:</b> FastAPI (REST API)</li>
        <li><b>OCR:</b> EasyOCR + OpenCV</li>
        <li><b>NER Model:</b> BERT-based transformer</li>
        <li><b>ML Framework:</b> PyTorch + Hugging Face</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='info-card'>
        <h4>⚙️ How It Works</h4>
        <ol>
        <li><b>Image Upload:</b> User uploads product photo</li>
        <li><b>OCR Extraction:</b> Text extracted from image</li>
        <li><b>Text Cleaning:</b> Remove noise and normalize</li>
        <li><b>NER Detection:</b> AI identifies allergen entities</li>
        <li><b>Mapping:</b> Match to standard allergen categories</li>
        <li><b>Results:</b> Display with confidence scores</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Statistics section
    st.markdown("### 📈 Model Information")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Allergen Categories", "12", help="Number of allergen types detected")
    
    with col2:
        st.metric("Model Type", "BERT", help="Transformer-based NER model")
    
    with col3:
        st.metric("Languages", "English", help="Currently supported languages")
    
    with col4:
        st.metric("Avg Response", "< 2s", help="Average processing time")
    
    st.markdown("---")
    
    # API Documentation
    st.markdown("### 🔌 API Endpoints")
    
    with st.expander("View API Documentation"):
        st.markdown("""
        **Base URL:** `http://localhost:8000`
        
        **Endpoints:**
        
        1. **GET /health** - Check API health status
        2. **POST /detect** - Analyze image file
           - Parameters: `file` (image), `use_ocr` (boolean)
        3. **POST /detect-text** - Analyze text input
           - Parameters: `text` (string)
        
        **Response Format:**
        ```json
        {
          "success": true,
          "detected_allergens": {...},
          "avg_confidence": 0.85,
          "timings": {...},
          "raw_text": "...",
          "cleaned_text": "..."
        }
        ```
        """)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; padding: 2rem; color: #666;'>
        <p><b>Allergen Detection System</b> | Powered by AI/ML</p>
        <p style='font-size: 0.85rem;'>⚠️ Note: This system is for informational purposes. 
        Always verify allergen information with product manufacturers.</p>
    </div>
    """, unsafe_allow_html=True)
