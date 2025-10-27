@echo off
echo ========================================
echo AGE Agent - FINAL INSTALLATION
echo ========================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Installing additional dependencies...
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install pytesseract==0.3.10
pip install Pillow==10.1.0

echo.
echo ========================================
echo TESSERACT OCR INSTALLATION
echo ========================================
echo.
echo Please install Tesseract OCR manually:
echo 1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
echo 2. Install to default location: C:\Program Files\Tesseract-OCR
echo 3. Add to PATH or set TESSDATA_PREFIX environment variable
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
echo INSTALLATION COMPLETE!
echo ========================================
echo.
echo Features installed:
echo - Live task detection during recording
echo - Advanced OCR analysis with Tesseract
echo - Real-time application detection
echo - Enhanced dashboard with detailed results
echo - Complete offline operation
echo.
echo To run the application:
echo python main.py
echo.
echo NEW FEATURES:
echo - Click "Start Recording" to begin live detection
echo - Live detection shows tasks and apps in real-time
echo - Toggle live detection on/off as needed
echo - Enhanced dashboard shows comprehensive analysis
echo.
echo The system will now detect tasks like:
echo - Excel operations (data entry, formulas, charts)
echo - Word processing (writing, formatting, editing)
echo - File management (copy, move, rename, organize)
echo - Web browsing (search, forms, navigation)
echo - Development tasks (coding, debugging)
echo.
pause
