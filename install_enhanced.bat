@echo off
echo ========================================
echo AGE Agent Enhanced Installation
echo ========================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Installing Tesseract OCR...
echo Please download and install Tesseract OCR from:
echo https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo After installation, add Tesseract to your PATH or set TESSDATA_PREFIX
echo.

echo.
echo Creating necessary directories...
if not exist "user_data" mkdir user_data
if not exist "user_data\audio" mkdir user_data\audio
if not exist "user_data\recordings" mkdir user_data\recordings
if not exist "user_data\screenshots" mkdir user_data\screenshots
if not exist "user_data\processed" mkdir user_data\processed
if not exist "user_data\temp" mkdir user_data\temp
if not exist "logs" mkdir logs

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Features installed:
echo - Enhanced OCR analysis with Tesseract
echo - Advanced task detection for Excel, Word, etc.
echo - Complete offline analysis with local LLM
echo - Enhanced dashboard with detailed results
echo - Pattern recognition and learning
echo.
echo To run the application:
echo python main.py
echo.
echo For enhanced dashboard, run analysis first, then click "Enhanced Dashboard"
echo.
pause
