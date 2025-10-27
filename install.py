#!/usr/bin/env python3
"""
AGE Agent Installation Script
Installs all required dependencies and sets up the environment
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def install_dependencies():
    """Install all required dependencies."""
    print("🚀 Installing AGE Agent dependencies...")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not in a virtual environment. Consider creating one:")
        print("   python -m venv venv")
        print("   venv\\Scripts\\activate  # Windows")
        print("   source venv/bin/activate  # Linux/Mac")
        print()
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        print("❌ Failed to install dependencies. Please check your internet connection and try again.")
        return False
    
    print("✅ All dependencies installed successfully!")
    return True


def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = [
        "user_data",
        "user_data/recordings",
        "user_data/processed", 
        "user_data/temp",
        "user_data/screenshots",
        "user_data/audio",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory}")
    
    return True


def create_env_file():
    """Create .env file template."""
    print("\n🔧 Creating .env file template...")
    
    env_content = """# AGE Agent Environment Variables
# Add your API keys here (optional - app works without them)

# OpenAI API Key (for external LLM analysis)
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API Key (alternative)
GEMINI_API_KEY=your_gemini_api_key_here

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("💡 You can add your API keys to .env file for enhanced analysis")
    else:
        print("✅ .env file already exists")
    
    return True


def test_installation():
    """Test if installation was successful."""
    print("\n🧪 Testing installation...")
    
    try:
        # Test PyQt5
        import PyQt5
        print("✅ PyQt5 imported successfully")
    except ImportError:
        print("❌ PyQt5 import failed")
        return False
    
    try:
        # Test other key modules
        import mss
        print("✅ MSS (screen capture) imported successfully")
    except ImportError:
        print("⚠️  MSS not available - screen recording will be limited")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError:
        print("⚠️  OpenCV not available - video processing will be limited")
    
    try:
        import pyaudio
        print("✅ PyAudio imported successfully")
    except ImportError:
        print("⚠️  PyAudio not available - audio recording will be limited")
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError:
        print("❌ Requests import failed")
        return False
    
    print("✅ Installation test completed!")
    return True


def main():
    """Main installation process."""
    print("=" * 60)
    print("🎯 AGE Agent Installation Script")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 AGE Agent installation completed successfully!")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("1. Run the application: python main.py")
    print("2. Or use the batch file: START.bat (Windows)")
    print("3. Add your API keys to .env file for enhanced analysis")
    print("\n💡 The app works without API keys using local analysis!")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ Installation completed successfully!")
        sys.exit(0)
