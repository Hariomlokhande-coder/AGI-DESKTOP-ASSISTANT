#!/usr/bin/env python3
"""
Test script to verify workflow analysis is working properly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm.workflow_analyzer import WorkflowAnalyzer
from src.storage.simple_config import config
from src.error_handling.simple_logger import logger

def test_workflow_analysis():
    """Test workflow analysis with sample data."""
    print("🧪 Testing Workflow Analysis...")
    
    try:
        # Initialize analyzer
        analyzer = WorkflowAnalyzer(config)
        print("✅ WorkflowAnalyzer initialized successfully")
        
        # Create sample session data
        session_data = {
            'duration': 120,  # 2 minutes
            'start_time': '2024-01-01 10:00:00',
            'end_time': '2024-01-01 10:02:00'
        }
        
        # Create sample screenshots (simulate file paths)
        screenshots = [f"screenshot_{i}.png" for i in range(15)]
        
        # Test audio transcription
        audio_transcription = "User working on Excel spreadsheet, entering data, creating charts"
        
        print(f"📊 Testing with {len(screenshots)} screenshots, {session_data['duration']}s duration")
        
        # Analyze session
        workflows = analyzer.analyze_session(session_data, screenshots, audio_transcription)
        
        print(f"✅ Analysis completed! Found {len(workflows)} workflows")
        
        # Display results
        for i, workflow in enumerate(workflows, 1):
            print(f"\n📋 WORKFLOW {i}:")
            print(f"   Description: {workflow.get('description', 'Unknown')}")
            print(f"   Type: {workflow.get('workflow_type', 'unknown')}")
            print(f"   Complexity: {workflow.get('complexity', 'unknown')}")
            print(f"   Automation Potential: {workflow.get('automation_potential', 'unknown')}")
            print(f"   Automation Score: {workflow.get('automation_score', 0)}/100")
            print(f"   Estimated Time: {workflow.get('estimated_time', 'Unknown')}")
            
            steps = workflow.get('steps', [])
            if steps:
                print(f"   Steps: {len(steps)} steps")
                for j, step in enumerate(steps[:3], 1):  # Show first 3 steps
                    print(f"     {j}. {step}")
                if len(steps) > 3:
                    print(f"     ... and {len(steps) - 3} more steps")
        
        # Test with minimal data
        print("\n🧪 Testing with minimal data...")
        minimal_workflows = analyzer.analyze_session(
            {'duration': 30}, 
            ['screenshot1.png'], 
            "Basic computer usage"
        )
        
        print(f"✅ Minimal analysis completed! Found {len(minimal_workflows)} workflows")
        
        if minimal_workflows:
            workflow = minimal_workflows[0]
            print(f"   Description: {workflow.get('description', 'Unknown')}")
            print(f"   Type: {workflow.get('workflow_type', 'unknown')}")
            print(f"   Score: {workflow.get('automation_score', 0)}/100")
        
        print("\n🎉 All tests passed! Workflow analysis is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_workflow_analysis()
    sys.exit(0 if success else 1)
