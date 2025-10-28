@echo off
echo Starting SplitMint Frontend...
echo.

cd /d "%~dp0\..\splitmint"

echo Current directory: %CD%
echo.

if not exist "node_modules\" (
    echo Installing dependencies...
    call pnpm install
    echo.
)

echo Starting Next.js dev server on http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

call pnpm dev
