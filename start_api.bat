@echo off
echo Starting FastAPI server...
set PYTHONPATH=%CD%
".venv\Scripts\python.exe" src\api\allergen_api.py
