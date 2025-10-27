@echo off
echo ================================
echo AGE Agent Installation Script
echo ================================
echo.

echo [1/5] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

echo [4/5] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo [5/5] Creating configuration...
if not exist .env (
    copy .env.example .env
    echo Created .env file - Please add your API keys!
)

if not exist config\config.yaml (
    echo Config file already exists
)

echo.
echo ================================
echo Installation Complete!
echo ================================
echo.
echo Next steps:
echo 1. Edit .env file and add your GEMINI_API_KEY
echo 2. Run: venv\Scripts\activate
echo 3. Run: python src\main.py
echo.
pause
