@echo off
REM Wrapper script to run iterative NER training with error recovery
REM Logs output to file and console

echo ================================================================================
echo ALLERGEN DETECTION - NER TRAINING
echo ================================================================================
echo.
echo Starting training with error handling...
echo Output will be logged to results/training/
echo.
echo Press Ctrl+C to stop training (progress will be saved)
echo ================================================================================
echo.

cd /d "%~dp0.."

REM Run training with output logging
.venv\Scripts\python.exe scripts/train_ner_iterative.py 2>&1 | tee results/training/training_console.log

if %ERRORLEVEL% == 0 (
    echo.
    echo ================================================================================
    echo Training completed successfully!
    echo ================================================================================
) else (
    echo.
    echo ================================================================================
    echo Training ended with code %ERRORLEVEL%
    echo Check results/training/ for logs and saved models
    echo ================================================================================
)

pause
