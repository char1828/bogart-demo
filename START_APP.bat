@echo off
title BOGART DEMO
cd /d "%~dp0"

echo ======================================================================
echo                            BOGART DEMO
echo   Target: Google Cloud Platform (Cloud SQL Postgres + GCS Bucket)
echo ======================================================================
echo.
echo 1. Starting application server...
echo 2. Launching your browser automatically...
echo.

:: Automatically pop open default browser after server initializes
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000"

:: Start the FastAPI server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
