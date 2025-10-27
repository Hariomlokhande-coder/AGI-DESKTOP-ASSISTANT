#!/usr/bin/env python3
"""
Test script for AGE Agent
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all imports."""
    print("🧪 Testing imports...")
    
    try:
        from src.capture.simple_recorder import ScreenshotCapture, AudioRecorder
        print("✅ Simple recorder imports successful")
    except ImportError as e:
        print(f"❌ Simple recorder import failed: {e}")
        return False
    
    try:
        from src.llm.workflow_analyzer import WorkflowAnalyzer
        print("✅ Workflow analyzer import successful")
    except ImportError as e:
        print(f"❌ Workflow analyzer import failed: {e}")
        return False
    
    try:
        from src.storage.simple_config import config
        print("✅ Simple config import successful")
    except ImportError as e:
        print(f"❌ Simple config import failed: {e}")
        return False
    
    try:
        from src.error_handling.simple_logger import logger
        print("✅ Simple logger import successful")
    except ImportError as e:
        print(f"❌ Simple logger import failed: {e}")
        return False
    
    return True

def test_workflow_analysis():
    """Test workflow analysis."""
    print("\n🧪 Testing workflow analysis...")
    
    try:
        from src.llm.focused_analyzer import FocusedWorkflowAnalyzer
        
        analyzer = FocusedWorkflowAnalyzer()
        
        # Test context
        context = {
            'screenshot_count': 15,
            'duration': 120,
            'audio_transcription': 'I am working on Excel spreadsheet with data entry'
        }
        
        result = analyzer.analyze_focused_workflow(context)
        
        print(f"✅ Workflow analysis successful")
        print(f"   Workflow type: {result.get('workflow_type', 'unknown')}")
        print(f"   Automation score: {result.get('automation_score', 0)}/100")
        print(f"   Complexity: {result.get('complexity', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow analysis failed: {e}")
        return False

def test_config():
    """Test configuration."""
    print("\n🧪 Testing configuration...")
    
    try:
        from src.storage.simple_config import config
        
        # Test config access
        fps = config.get('recording.fps', 1)
        print(f"✅ Config access successful (FPS: {fps})")
        
        # Test API key check
        has_openai = config.has_api_key('openai')
        print(f"✅ API key check successful (OpenAI: {has_openai})")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_directories():
    """Test directory structure."""
    print("\n🧪 Testing directories...")
    
    required_dirs = [
        'user_data',
        'user_data/recordings',
        'user_data/processed',
        'user_data/temp',
        'user_data/screenshots',
        'user_data/audio',
        'logs'
    ]
    
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory} exists")
        else:
            print(f"❌ {directory} missing")
            return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 AGE Agent Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Workflow Analysis", test_workflow_analysis),
        ("Configuration", test_config),
        ("Directories", test_directories)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AGE Agent is ready to run.")
        print("\n💡 To run the application:")
        print("   python main.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
