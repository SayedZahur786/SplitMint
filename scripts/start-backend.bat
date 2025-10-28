@echo off
echo Starting SplitMint Backend Server...
echo.
echo Server will run on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

cd /d "%~dp0\..\backend"
echo Current directory: %CD%
echo.

python -m uvicorn main:app --reload
