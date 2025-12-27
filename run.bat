@echo off
REM Convenience wrapper to run commands with the venv Python
set PYTHONPATH=%CD%
".venv\Scripts\python.exe" %*
