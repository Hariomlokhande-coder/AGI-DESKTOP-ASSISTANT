#!/usr/bin/env python3
"""
AGE Agent - Simple Run Script
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run AGE Agent."""
    print("🚀 Starting AGE Agent...")
    
    try:
        # Import and run main application
        from main import main as run_app
        run_app()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Try running the installation script first:")
        print("   python install.py")
        return False
    except Exception as e:
        print(f"❌ Error starting AGE Agent: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Failed to start AGE Agent")
        sys.exit(1)
