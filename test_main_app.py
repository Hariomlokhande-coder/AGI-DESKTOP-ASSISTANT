#!/usr/bin/env python3
"""
Test script to verify the main application workflow.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from main import AGEAgentMainWindow, AnalysisWorker
from src.storage.simple_config import config
from src.error_handling.simple_logger import logger

def test_main_app():
    """Test main application components."""
    print("🧪 Testing Main Application...")
    
    try:
        # Test QApplication
        app = QApplication([])
        print("✅ QApplication initialized")
        
        # Test main window
        window = AGEAgentMainWindow()
        print("✅ Main window created successfully")
        
        # Test analysis worker with sample data
        session_data = {
            'duration': 60,
            'start_time': '2024-01-01 10:00:00',
            'end_time': '2024-01-01 10:01:00'
        }
        
        screenshots = [f"test_screenshot_{i}.png" for i in range(10)]
        audio_path = "test_audio.wav"
        
        print("📊 Testing AnalysisWorker...")
        
        # Create analysis worker
        worker = AnalysisWorker(session_data, screenshots, audio_path)
        print("✅ AnalysisWorker created successfully")
        
        # Test workflow analysis directly
        from src.llm.workflow_analyzer import WorkflowAnalyzer
        analyzer = WorkflowAnalyzer(config)
        
        workflows = analyzer.analyze_session(
            session_data, 
            screenshots, 
            "User working on computer tasks"
        )
        
        print(f"✅ Direct analysis completed! Found {len(workflows)} workflows")
        
        if workflows:
            workflow = workflows[0]
            print(f"   Workflow Type: {workflow.get('workflow_type', 'unknown')}")
            print(f"   Description: {workflow.get('description', 'Unknown')}")
            print(f"   Automation Score: {workflow.get('automation_score', 0)}/100")
            
            # Check if all required fields are present
            required_fields = ['description', 'workflow_type', 'complexity', 'automation_potential', 'automation_score']
            missing_fields = [field for field in required_fields if field not in workflow]
            
            if missing_fields:
                print(f"⚠️  Missing fields: {missing_fields}")
            else:
                print("✅ All required fields present")
        
        # Test UI components
        print("🖥️  Testing UI components...")
        
        # Test buttons
        start_btn = window.start_btn
        stop_btn = window.stop_btn
        analyze_btn = window.analyze_btn
        
        print(f"   Start button enabled: {start_btn.isEnabled()}")
        print(f"   Stop button enabled: {stop_btn.isEnabled()}")
        print(f"   Analyze button enabled: {analyze_btn.isEnabled()}")
        
        # Test status label
        status_text = window.status_label.text()
        print(f"   Status text: {status_text}")
        
        print("\n🎉 All main application tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Main app test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_main_app()
    sys.exit(0 if success else 1)
