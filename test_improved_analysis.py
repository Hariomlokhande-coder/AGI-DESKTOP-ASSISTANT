#!/usr/bin/env python3
"""
Test the improved workflow analysis to ensure it's more accurate.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm.workflow_analyzer import WorkflowAnalyzer
from src.storage.simple_config import config
from src.error_handling.simple_logger import logger

def test_improved_analysis():
    """Test the improved workflow analysis."""
    print("🧪 Testing Improved Workflow Analysis...")
    
    try:
        analyzer = WorkflowAnalyzer(config)
        
        # Test cases with different scenarios
        test_cases = [
            {
                'name': 'High Activity - No Specific Keywords',
                'session_data': {'duration': 180, 'start_time': '10:00', 'end_time': '10:03'},
                'screenshots': [f'screenshot_{i}.png' for i in range(35)],
                'audio': 'User working on computer tasks, clicking and typing',
                'expected_type': 'general'  # Should not assume Excel without keywords
            },
            {
                'name': 'Moderate Activity - General Usage',
                'session_data': {'duration': 120, 'start_time': '10:00', 'end_time': '10:02'},
                'screenshots': [f'screenshot_{i}.png' for i in range(20)],
                'audio': 'Basic computer usage, browsing and typing',
                'expected_type': 'general'
            },
            {
                'name': 'Low Activity - Simple Tasks',
                'session_data': {'duration': 60, 'start_time': '10:00', 'end_time': '10:01'},
                'screenshots': [f'screenshot_{i}.png' for i in range(8)],
                'audio': 'Simple computer tasks',
                'expected_type': 'general'
            },
            {
                'name': 'Explicit Excel Keywords',
                'session_data': {'duration': 240, 'start_time': '10:00', 'end_time': '10:04'},
                'screenshots': [f'screenshot_{i}.png' for i in range(25)],
                'audio': 'Working on Excel spreadsheet, entering data, creating charts, applying formulas',
                'expected_type': 'excel_operations'  # Should detect Excel with explicit keywords
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📊 Test {i}: {test_case['name']}")
            
            workflows = analyzer.analyze_session(
                test_case['session_data'],
                test_case['screenshots'],
                test_case['audio']
            )
            
            if workflows:
                workflow = workflows[0]
                workflow_type = workflow.get('workflow_type', 'unknown')
                automation_score = workflow.get('automation_score', 0)
                description = workflow.get('description', 'Unknown')
                
                print(f"   ✅ Workflow Type: {workflow_type}")
                print(f"   📊 Automation Score: {automation_score}/100")
                print(f"   📝 Description: {description[:60]}...")
                
                # Check if the result matches expectations
                if test_case['expected_type'] == 'general' and workflow_type == 'general':
                    print(f"   ✅ Correctly identified as general workflow")
                elif test_case['expected_type'] == 'excel_operations' and workflow_type == 'excel_operations':
                    print(f"   ✅ Correctly identified Excel workflow")
                else:
                    print(f"   ⚠️  Expected {test_case['expected_type']}, got {workflow_type}")
                
                # Check automation score is reasonable
                if 10 <= automation_score <= 85:
                    print(f"   ✅ Automation score is realistic: {automation_score}")
                else:
                    print(f"   ⚠️  Automation score seems unrealistic: {automation_score}")
                    
            else:
                print(f"   ❌ No workflows returned")
        
        print("\n🎉 Improved analysis test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Improved analysis test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_improved_analysis()
    sys.exit(0 if success else 1)
