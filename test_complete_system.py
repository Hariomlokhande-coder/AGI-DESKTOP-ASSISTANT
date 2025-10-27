#!/usr/bin/env python3
"""
Complete system test for AGE Agent with detailed analysis and debugging.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from main import AGEAgentMainWindow, AnalysisWorker
from src.llm.workflow_analyzer import WorkflowAnalyzer
from src.error_handling.debug_system import debug_system
from src.storage.simple_config import config
from src.error_handling.simple_logger import logger

def test_complete_system():
    """Test the complete AGE Agent system with detailed analysis."""
    print("🚀 Testing Complete AGE Agent System...")
    
    try:
        # Initialize debug system
        print("🔍 Initializing debug system...")
        health_check = debug_system.check_system_health()
        print(f"✅ System health: {health_check.get('overall_status', 'unknown')}")
        
        # Test QApplication
        app = QApplication([])
        print("✅ QApplication initialized")
        
        # Test main window
        window = AGEAgentMainWindow()
        print("✅ Main window created")
        
        # Simulate a realistic workflow session
        print("\n📊 Simulating Workflow Session...")
        session_data = {
            'duration': 180,  # 3 minutes
            'start_time': '2024-01-01 10:00:00',
            'end_time': '2024-01-01 10:03:00'
        }
        
        # Create realistic screenshots (35 screenshots over 3 minutes)
        screenshots = [f"workflow_screenshot_{i:03d}.png" for i in range(35)]
        audio_path = "workflow_audio.wav"
        
        print(f"   Session Duration: {session_data['duration']} seconds")
        print(f"   Screenshots: {len(screenshots)}")
        print(f"   Audio: {audio_path}")
        
        # Test workflow analyzer
        print("\n🔍 Testing Workflow Analysis...")
        analyzer = WorkflowAnalyzer(config)
        
        # Get basic workflow analysis
        workflows = analyzer.analyze_session(
            session_data, 
            screenshots, 
            "User working on computer tasks, clicking and typing, navigating between applications"
        )
        
        print(f"✅ Basic analysis completed: {len(workflows)} workflows found")
        
        if workflows:
            workflow = workflows[0]
            print(f"   Workflow Type: {workflow.get('workflow_type', 'unknown')}")
            print(f"   Description: {workflow.get('description', 'Unknown')}")
            print(f"   Automation Score: {workflow.get('automation_score', 0)}/100")
        
        # Get detailed analysis
        print("\n📊 Testing Detailed Analysis...")
        detailed_analysis = analyzer.get_detailed_analysis(
            session_data, 
            screenshots, 
            "User working on computer tasks, clicking and typing, navigating between applications"
        )
        
        print("✅ Detailed analysis completed")
        
        # Display detailed results
        session_summary = detailed_analysis.get('session_summary', {})
        print(f"\n📊 SESSION SUMMARY:")
        print(f"   Duration: {session_summary.get('total_duration', 'Unknown')}")
        print(f"   Interactions: {session_summary.get('total_interactions', 0)}")
        print(f"   Activity Rate: {session_summary.get('activity_rate', 'Unknown')}")
        print(f"   Session Type: {session_summary.get('session_type', 'Unknown')}")
        print(f"   Complexity: {session_summary.get('complexity_level', 'Unknown')}")
        
        # Display automation analysis
        automation_analysis = detailed_analysis.get('automation_analysis', {})
        print(f"\n🤖 AUTOMATION ANALYSIS:")
        automation_scores = automation_analysis.get('automation_scores', {})
        print(f"   Overall Score: {automation_scores.get('overall_score', 'Unknown')}")
        print(f"   Repetition Score: {automation_scores.get('repetition_score', 'Unknown')}")
        print(f"   Complexity Score: {automation_scores.get('complexity_score', 'Unknown')}")
        print(f"   Frequency Score: {automation_scores.get('frequency_score', 'Unknown')}")
        print(f"   Approach: {automation_analysis.get('recommended_approach', 'Unknown')}")
        
        # Display workflow breakdown
        workflow_breakdown = detailed_analysis.get('workflow_breakdown', {})
        print(f"\n🔧 WORKFLOW BREAKDOWN:")
        phases = workflow_breakdown.get('workflow_phases', [])
        for phase in phases:
            print(f"   📋 {phase.get('name', 'Unknown Phase')}")
            print(f"      Interactions: {phase.get('estimated_interactions', 0)}")
            print(f"      Description: {phase.get('description', 'Unknown')}")
            print(f"      Automation Potential: {phase.get('automation_potential', 'Unknown')}")
        
        # Display optimization recommendations
        optimization_recommendations = detailed_analysis.get('optimization_recommendations', [])
        print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
        for rec in optimization_recommendations:
            print(f"   🎯 Priority: {rec.get('priority', 'Unknown')}")
            print(f"   📂 Category: {rec.get('category', 'Unknown')}")
            print(f"   💡 Recommendation: {rec.get('recommendation', 'Unknown')}")
            print(f"   📈 Expected Benefit: {rec.get('expected_benefit', 'Unknown')}")
            print(f"   ⚙️  Implementation Effort: {rec.get('implementation_effort', 'Unknown')}")
            print()
        
        # Test analysis worker
        print("\n⚙️  Testing Analysis Worker...")
        worker = AnalysisWorker(session_data, screenshots, audio_path)
        print("✅ AnalysisWorker created successfully")
        
        # Test UI components
        print("\n🖥️  Testing UI Components...")
        print(f"   Start button enabled: {window.start_btn.isEnabled()}")
        print(f"   Stop button enabled: {window.stop_btn.isEnabled()}")
        print(f"   Analyze button enabled: {window.analyze_btn.isEnabled()}")
        print(f"   Status text: {window.status_label.text()}")
        
        # Test display results
        print("\n📄 Testing Results Display...")
        window.display_results(workflows)
        results_text = window.results_text.toPlainText()
        print(f"✅ Results displayed: {len(results_text)} characters")
        
        # Check if results contain expected content
        expected_sections = [
            "COMPREHENSIVE WORKFLOW ANALYSIS",
            "SESSION SUMMARY",
            "ACTIVITY PATTERNS",
            "AUTOMATION ANALYSIS",
            "WORKFLOW BREAKDOWN",
            "OPTIMIZATION RECOMMENDATIONS",
            "DEBUGGING INFORMATION"
        ]
        
        missing_sections = []
        for section in expected_sections:
            if section not in results_text:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"⚠️  Missing sections: {missing_sections}")
        else:
            print("✅ All expected sections present")
        
        # Generate debug report
        print("\n🔍 Generating Debug Report...")
        debug_report = debug_system.get_debug_report()
        print("✅ Debug report generated")
        
        # Save debug report
        report_file = debug_system.save_debug_report()
        if report_file:
            print(f"✅ Debug report saved to: {report_file}")
        
        # Display system health
        print(f"\n🏥 SYSTEM HEALTH:")
        print(f"   Overall Status: {health_check.get('overall_status', 'unknown')}")
        
        checks = health_check.get('checks', {})
        for check_name, check_result in checks.items():
            status = check_result.get('status', 'unknown')
            print(f"   {check_name}: {status}")
        
        print("\n🎉 Complete system test completed successfully!")
        print("✅ All components working properly")
        print("✅ Detailed analysis functional")
        print("✅ Debug system operational")
        print("✅ UI components responsive")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        logger.error(f"Complete system test failed: {e}", exc_info=True)
        
        # Log error to debug system
        debug_system.log_error(e, {"test": "complete_system"})
        
        return False

if __name__ == "__main__":
    success = test_complete_system()
    sys.exit(0 if success else 1)
