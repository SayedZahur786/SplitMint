@echo off
REM Start Email Monitor (Standalone)
REM This runs the email monitor without starting the FastAPI server

echo ============================================================
echo Starting Email Monitor (Standalone Mode)
echo ============================================================
echo.
echo This will check for new transaction emails every 45 seconds
echo and automatically add them to the database.
echo.
echo Press Ctrl+C to stop monitoring
echo ============================================================
echo.

cd /d "%~dp0\..\backend"
echo Current directory: %CD%
echo.

python email_monitor.py

pause
