@echo off
echo ===================================
echo AGE Agent - Starting Application
echo ===================================
echo.
echo Activating virtual environment...
call .venv\Scripts\activate
echo.
echo Starting AGE Agent...
python run_app.py
echo.
echo ===================================
echo AGE Agent has stopped
echo ===================================
pause

