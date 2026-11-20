@echo off
title Seed GCP Benchmark Assets
cd /d "%~dp0"

echo ======================================================================
echo           Seed Assets to GCP Cloud SQL & GCS
echo ======================================================================
echo.
echo Populating 15 calibrated benchmark assets to Google Cloud Platform...
echo.

python scripts/seed_data.py 15

echo.
echo ======================================================================
echo Done! All assets uploaded to Cloud SQL (Option 1) and GCS (Option 2).
echo ======================================================================
pause
