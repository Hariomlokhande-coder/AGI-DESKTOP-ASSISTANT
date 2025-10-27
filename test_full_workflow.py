#!/usr/bin/env python3
"""
Test script to simulate the full recording and analysis workflow.
"""

import sys
import os
import time
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from main import AGEAgentMainWindow, RecordingWorker, AnalysisWorker
from src.storage.simple_config import config
from src.error_handling.simple_logger import logger

def simulate_recording_session():
    """Simulate a complete recording session."""
    print("🎬 Simulating Recording Session...")
    
    # Create mock session data
    session_data = {
        'duration': 180,  # 3 minutes
        'start_time': '2024-01-01 10:00:00',
        'end_time': '2024-01-01 10:03:00',
        'screenshot_count': 25
    }
    
    # Create mock screenshots
    screenshots = [f"mock_screenshot_{i:03d}.png" for i in range(25)]
    
    # Create mock audio path
    audio_path = "mock_audio.wav"
    
    print(f"📊 Session Data: {session_data['duration']}s, {len(screenshots)} screenshots")
    
    return session_data, screenshots, audio_path

def test_analysis_worker(session_data, screenshots, audio_path):
    """Test the analysis worker."""
    print("\n🔍 Testing Analysis Worker...")
    
    try:
        # Create analysis worker
        worker = AnalysisWorker(session_data, screenshots, audio_path)
        print("✅ AnalysisWorker created")
        
        # Simulate the analysis process
        print("📊 Running analysis...")
        
        # Initialize analyzer directly
        from src.llm.workflow_analyzer import WorkflowAnalyzer
        analyzer = WorkflowAnalyzer(config)
        
        # Analyze session
        workflows = analyzer.analyze_session(
            session_data, 
            screenshots, 
            "User working on Excel spreadsheet, entering data, creating charts, formatting cells"
        )
        
        print(f"✅ Analysis completed! Found {len(workflows)} workflows")
        
        # Display detailed results
        for i, workflow in enumerate(workflows, 1):
            print(f"\n📋 WORKFLOW {i}:")
            print(f"   Description: {workflow.get('description', 'Unknown')}")
            print(f"   Type: {workflow.get('workflow_type', 'unknown')}")
            print(f"   Complexity: {workflow.get('complexity', 'unknown')}")
            print(f"   Automation Potential: {workflow.get('automation_potential', 'unknown')}")
            print(f"   Automation Score: {workflow.get('automation_score', 0)}/100")
            print(f"   Estimated Time: {workflow.get('estimated_time', 'Unknown')}")
            
            # Check steps
            steps = workflow.get('steps', [])
            if steps:
                print(f"   Steps ({len(steps)}):")
                for j, step in enumerate(steps[:3], 1):
                    print(f"     {j}. {step}")
                if len(steps) > 3:
                    print(f"     ... and {len(steps) - 3} more")
            
            # Check repetitive actions
            repetitive = workflow.get('repetitive_actions', [])
            if repetitive:
                print(f"   Repetitive Actions: {', '.join(repetitive[:3])}")
            
            # Check automation opportunities
            opportunities = workflow.get('automation_opportunities', [])
            if opportunities:
                print(f"   Automation Opportunities: {', '.join(opportunities[:2])}")
            
            # Check recommended tools
            tools = workflow.get('recommended_tools', [])
            if tools:
                print(f"   Recommended Tools: {', '.join(tools[:3])}")
        
        return workflows
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        logger.error(f"Analysis test failed: {e}", exc_info=True)
        return []

def test_ui_display(workflows):
    """Test UI display of results."""
    print("\n🖥️  Testing UI Display...")
    
    try:
        app = QApplication([])
        window = AGEAgentMainWindow()
        
        # Test the display_results method
        window.display_results(workflows)
        
        # Get the results text
        results_text = window.results_text.toPlainText()
        
        print("✅ Results displayed in UI")
        print(f"📄 Results text length: {len(results_text)} characters")
        
        # Check if results contain expected content
        expected_content = [
            "WORKFLOW ANALYSIS RESULTS",
            "Description:",
            "Type:",
            "Complexity:",
            "Automation Potential:",
            "Automation Score:",
            "Steps:",
            "SUMMARY"
        ]
        
        missing_content = []
        for content in expected_content:
            if content not in results_text:
                missing_content.append(content)
        
        if missing_content:
            print(f"⚠️  Missing content: {missing_content}")
        else:
            print("✅ All expected content present")
        
        # Show first few lines of results
        lines = results_text.split('\n')[:10]
        print("\n📄 Sample Results:")
        for line in lines:
            if line.strip():
                print(f"   {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ UI display test failed: {e}")
        logger.error(f"UI display test failed: {e}", exc_info=True)
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Full Workflow Test...")
    
    try:
        # Simulate recording session
        session_data, screenshots, audio_path = simulate_recording_session()
        
        # Test analysis
        workflows = test_analysis_worker(session_data, screenshots, audio_path)
        
        if not workflows:
            print("❌ No workflows found - this might be the issue!")
            return False
        
        # Test UI display
        ui_success = test_ui_display(workflows)
        
        if ui_success:
            print("\n🎉 Full workflow test completed successfully!")
            print("✅ Recording simulation works")
            print("✅ Analysis works")
            print("✅ UI display works")
            return True
        else:
            print("\n❌ UI display test failed")
            return False
            
    except Exception as e:
        print(f"❌ Full workflow test failed: {e}")
        logger.error(f"Full workflow test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
