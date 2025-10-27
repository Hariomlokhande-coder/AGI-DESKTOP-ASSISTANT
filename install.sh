#!/bin/bash

echo "================================"
echo "AGE Agent Installation Script"
echo "================================"
echo ""

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Upgrading pip..."
python -m pip install --upgrade pip

echo "[4/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "[5/5] Creating configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - Please add your API keys!"
fi

echo ""
echo "================================"
echo "Installation Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your GEMINI_API_KEY"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python src/main.py"
echo ""
