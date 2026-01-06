#!/usr/bin/env python
"""
Wrapper script to start the ML API with optimized settings for Windows.
This solves the transformers import hanging issue by setting env vars early.
"""
import os
import sys

# Set all optimization flags BEFORE any imports
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['HUGGINGFACE_HUB_CACHE'] = os.path.expanduser('~/.cache/huggingface')
os.environ['TORCH_JIT'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Disable slow symbolic math in PyTorch on Windows
os.environ['TORCH_COMPILE_DISABLE'] = '1'

# Now import and run
if __name__ == '__main__':
    import uvicorn
    from src.api.allergen_api import app
    
    print("[INFO] Starting ML API with optimized settings...")
    print("[INFO] HF_HUB_DISABLE_TELEMETRY: 1")
    print("[INFO] TORCH_JIT: 0")
    print("[INFO] TORCH_COMPILE_DISABLE: 1")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
