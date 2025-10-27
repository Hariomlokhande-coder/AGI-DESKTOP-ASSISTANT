#!/usr/bin/env python3
"""
Test the detailed workflow analysis system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm.workflow_analyzer import WorkflowAnalyzer
from src.storage.simple_config import config
from src.error_handling.simple_logger import logger

def test_detailed_analysis():
    """Test the detailed workflow analysis."""
    print("🧪 Testing Detailed Workflow Analysis...")
    
    try:
        analyzer = WorkflowAnalyzer(config)
        
        # Test with high-activity scenario (like your 35 screenshots)
        session_data = {
            'duration': 120,  # 2 minutes
            'start_time': '2024-01-01 10:00:00',
            'end_time': '2024-01-01 10:02:00'
        }
        
        screenshots = [f'screenshot_{i:03d}.png' for i in range(35)]
        audio_transcription = "User working on computer tasks, clicking and typing, navigating between applications"
        
        print(f"📊 Testing with {len(screenshots)} screenshots, {session_data['duration']}s duration")
        
        # Get detailed analysis
        detailed_analysis = analyzer.get_detailed_analysis(
            session_data, 
            screenshots, 
            audio_transcription
        )
        
        print("✅ Detailed analysis completed!")
        
        # Display session summary
        session_summary = detailed_analysis.get('session_summary', {})
        print(f"\n📊 SESSION SUMMARY:")
        print(f"   Duration: {session_summary.get('total_duration', 'Unknown')}")
        print(f"   Interactions: {session_summary.get('total_interactions', 0)}")
        print(f"   Activity Rate: {session_summary.get('activity_rate', 'Unknown')}")
        print(f"   Session Type: {session_summary.get('session_type', 'Unknown')}")
        print(f"   Complexity: {session_summary.get('complexity_level', 'Unknown')}")
        
        # Display activity patterns
        activity_patterns = detailed_analysis.get('activity_patterns', {})
        print(f"\n🔍 ACTIVITY PATTERNS:")
        patterns = activity_patterns.get('detected_patterns', [])
        for pattern in patterns:
            print(f"   • {pattern}")
        print(f"   Intensity: {activity_patterns.get('workflow_intensity', 'Unknown')}")
        
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
            print(f"   📋 {phase.get('name', 'Unknown')}")
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
        
        # Display debugging information
        debugging_info = detailed_analysis.get('debugging_info', {})
        print(f"🔍 DEBUGGING INFORMATION:")
        print(f"   Timestamp: {debugging_info.get('analysis_timestamp', 'Unknown')}")
        context_data = debugging_info.get('context_data', {})
        print(f"   Screenshot Count: {context_data.get('screenshot_count', 0)}")
        print(f"   Duration: {context_data.get('duration', 0)} seconds")
        print(f"   Audio Length: {context_data.get('audio_length', 0)} characters")
        print(f"   Has Screenshots: {context_data.get('has_screenshots', False)}")
        
        potential_issues = debugging_info.get('potential_issues', [])
        if potential_issues:
            print(f"\n⚠️  Potential Issues:")
            for issue in potential_issues:
                print(f"   • {issue}")
        
        recommendations = debugging_info.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"   • {rec}")
        
        print("\n🎉 Detailed analysis test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Detailed analysis test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_detailed_analysis()
    sys.exit(0 if success else 1)
