"""
Detailed workflow analyzer that provides comprehensive analysis of user workflows.
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..error_handling.simple_logger import logger


class DetailedWorkflowAnalyzer:
    """Comprehensive workflow analyzer with detailed step-by-step analysis."""
    
    def __init__(self):
        self.analysis_cache = {}
        self.pattern_history = []
        logger.info("DetailedWorkflowAnalyzer initialized")
    
    def analyze_detailed_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide comprehensive detailed analysis of the workflow."""
        try:
            screenshot_count = context.get('screenshot_count', 0)
            duration = context.get('duration', 0)
            audio_transcription = context.get('audio_transcription', '')
            screenshots = context.get('screenshots', [])
            
            logger.info(f"Analyzing detailed workflow: {screenshot_count} screenshots, {duration}s duration")
            
            # Comprehensive analysis
            analysis = {
                "session_summary": self._analyze_session_summary(context),
                "activity_patterns": self._analyze_activity_patterns(context),
                "workflow_breakdown": self._analyze_workflow_breakdown(context),
                "automation_analysis": self._analyze_automation_potential(context),
                "detailed_steps": self._generate_detailed_steps(context),
                "repetitive_patterns": self._identify_repetitive_patterns(context),
                "efficiency_analysis": self._analyze_efficiency(context),
                "optimization_recommendations": self._generate_optimization_recommendations(context),
                "implementation_roadmap": self._create_implementation_roadmap(context),
                "debugging_info": self._generate_debugging_info(context)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Detailed analysis error: {e}", exc_info=True)
            return self._generate_fallback_detailed_analysis(context)
    
    def _analyze_session_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze session summary with detailed metrics."""
        screenshot_count = context.get('screenshot_count', 0)
        duration = context.get('duration', 0)
        audio_transcription = context.get('audio_transcription', '')
        
        # Calculate activity metrics
        activity_rate = screenshot_count / max(duration, 1) if duration > 0 else 0
        avg_time_per_action = duration / max(screenshot_count, 1) if screenshot_count > 0 else 0
        
        # Determine session characteristics
        if activity_rate > 0.5:
            session_type = "High-intensity workflow"
            complexity_level = "Very Complex"
        elif activity_rate > 0.3:
            session_type = "Moderate-intensity workflow"
            complexity_level = "Complex"
        elif activity_rate > 0.1:
            session_type = "Low-intensity workflow"
            complexity_level = "Moderate"
        else:
            session_type = "Minimal activity"
            complexity_level = "Simple"
        
        return {
            "total_duration": f"{duration} seconds ({duration // 60} minutes {duration % 60} seconds)",
            "total_interactions": screenshot_count,
            "activity_rate": f"{activity_rate:.2f} interactions/second",
            "avg_time_per_action": f"{avg_time_per_action:.1f} seconds",
            "session_type": session_type,
            "complexity_level": complexity_level,
            "audio_available": bool(audio_transcription and len(audio_transcription.strip()) > 0),
            "audio_length": len(audio_transcription) if audio_transcription else 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_activity_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze detailed activity patterns."""
        screenshot_count = context.get('screenshot_count', 0)
        duration = context.get('duration', 0)
        
        # Activity distribution analysis
        if duration > 0:
            early_activity = min(screenshot_count * 0.3, screenshot_count)  # First 30% of time
            mid_activity = min(screenshot_count * 0.4, screenshot_count)    # Middle 40% of time
            late_activity = min(screenshot_count * 0.3, screenshot_count)   # Last 30% of time
        else:
            early_activity = mid_activity = late_activity = 0
        
        # Pattern detection
        patterns = []
        if screenshot_count > 30:
            patterns.append("High-frequency interactions")
        if duration > 300:
            patterns.append("Extended workflow session")
        if screenshot_count > 20 and duration < 120:
            patterns.append("Rapid task execution")
        if screenshot_count < 5 and duration > 60:
            patterns.append("Deliberate, slow workflow")
        
        return {
            "activity_distribution": {
                "early_phase": f"{early_activity:.0f} interactions",
                "mid_phase": f"{mid_activity:.0f} interactions", 
                "late_phase": f"{late_activity:.0f} interactions"
            },
            "detected_patterns": patterns,
            "workflow_intensity": "High" if screenshot_count > 25 else "Medium" if screenshot_count > 10 else "Low",
            "session_characteristics": {
                "is_repetitive": screenshot_count > 15 and duration > 60,
                "is_complex": screenshot_count > 20 or duration > 180,
                "is_efficient": screenshot_count > 10 and duration < 120,
                "needs_optimization": screenshot_count > 30 or duration > 300
            }
        }
    
    def _analyze_workflow_breakdown(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Break down the workflow into detailed components."""
        screenshot_count = context.get('screenshot_count', 0)
        duration = context.get('duration', 0)
        
        # Estimate workflow phases
        phases = []
        if screenshot_count > 0:
            # Setup phase (first 20% of interactions)
            setup_count = max(1, int(screenshot_count * 0.2))
            phases.append({
                "name": "Setup/Initialization",
                "estimated_interactions": setup_count,
                "description": "Opening applications, navigating to starting point",
                "automation_potential": "Medium"
            })
            
            # Main work phase (middle 60% of interactions)
            main_count = int(screenshot_count * 0.6)
            phases.append({
                "name": "Main Work Phase",
                "estimated_interactions": main_count,
                "description": "Core workflow execution, data processing",
                "automation_potential": "High"
            })
            
            # Completion phase (last 20% of interactions)
            completion_count = max(1, int(screenshot_count * 0.2))
            phases.append({
                "name": "Completion/Cleanup",
                "estimated_interactions": completion_count,
                "description": "Saving, organizing, finalizing work",
                "automation_potential": "Medium"
            })
        
        return {
            "workflow_phases": phases,
            "total_phases": len(phases),
            "phase_distribution": {
                "setup_percentage": 20,
                "main_work_percentage": 60,
                "completion_percentage": 20
            },
            "complexity_indicators": {
                "multiple_phases": len(phases) > 2,
                "high_interaction_count": screenshot_count > 20,
                "extended_duration": duration > 180,
                "potential_for_automation": screenshot_count > 10
            }
    }
    
    def _analyze_automation_potential(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detailed automation potential analysis."""
        screenshot_count = context.get('screenshot_count', 0)
        duration = context.get('duration', 0)
        
        # Calculate automation scores for different aspects
        repetition_score = min(100, (screenshot_count / max(duration, 1)) * 50) if duration > 0 else 0
        complexity_score = min(100, screenshot_count * 2)
        frequency_score = min(100, duration * 0.5) if duration > 0 else 0
        
        overall_score = (repetition_score + complexity_score + frequency_score) / 3
        
        # Automation opportunities
        opportunities = []
        if screenshot_count > 20:
            opportunities.append("High interaction count suggests repetitive tasks")
        if duration > 180:
            opportunities.append("Extended duration indicates complex workflow")
        if screenshot_count > 10 and duration < 120:
            opportunities.append("Efficient workflow with automation potential")
        
        # Risk assessment
        risks = []
        if screenshot_count > 50:
            risks.append("Very high interaction count - may be too complex to automate")
        if duration > 600:
            risks.append("Very long duration - automation may not be cost-effective")
        
        return {
            "automation_scores": {
                "repetition_score": f"{repetition_score:.1f}/100",
                "complexity_score": f"{complexity_score:.1f}/100", 
                "frequency_score": f"{frequency_score:.1f}/100",
                "overall_score": f"{overall_score:.1f}/100"
            },
            "automation_opportunities": opportunities,
            "automation_risks": risks,
            "recommended_approach": self._get_automation_approach(overall_score),
            "implementation_priority": "High" if overall_score > 70 else "Medium" if overall_score > 40 else "Low"
        }
    
    def _generate_detailed_steps(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed step-by-step breakdown."""
        screenshot_count = context.get('screenshot_count', 0)
        duration = context.get('duration', 0)
        
        steps = []
        
        # Phase 1: Preparation
        steps.append({
            "step_number": 1,
            "phase": "Preparation",
            "description": "Initial setup and preparation",
            "estimated_time": f"{duration // 6} seconds",
            "interactions": max(1, screenshot_count // 6),
            "automation_potential": "Low",
            "details": [
                "Opening required applications",
                "Setting up workspace",
                "Preparing data sources"
            ]
        })
        
        # Phase 2: Main execution
        steps.append({
            "step_number": 2,
            "phase": "Main Execution",
            "description": "Core workflow execution",
            "estimated_time": f"{duration // 2} seconds",
            "interactions": screenshot_count // 2,
            "automation_potential": "High",
            "details": [
                "Performing main tasks",
                "Data processing",
                "Application interactions"
            ]
        })
        
        # Phase 3: Completion
        steps.append({
            "step_number": 3,
            "phase": "Completion",
            "description": "Finalizing and cleanup",
            "estimated_time": f"{duration // 3} seconds",
            "interactions": max(1, screenshot_count // 3),
            "automation_potential": "Medium",
            "details": [
                "Saving work",
                "Organizing results",
                "Closing applications"
            ]
        })
        
        return steps
    
    def _identify_repetitive_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify repetitive patterns in the workflow."""
        screenshot_count = context.get('screenshot_count', 0)
        duration = context.get('duration', 0)
        
        patterns = []
        
        # High frequency patterns
        if screenshot_count > 25:
            patterns.append({
                "pattern_type": "High Frequency Interaction",
                "frequency": "Very High",
                "description": f"User performed {screenshot_count} interactions in {duration} seconds",
                "automation_potential": "Very High",
                "confidence": "High"
            })
        
        # Time-based patterns
        if duration > 300:
            patterns.append({
                "pattern_type": "Extended Workflow",
                "frequency": "Medium",
                "description": f"Workflow lasted {duration} seconds ({duration // 60} minutes)",
                "automation_potential": "High",
                "confidence": "Medium"
            })
        
        # Efficiency patterns
        if screenshot_count > 10 and duration < 120:
            patterns.append({
                "pattern_type": "Efficient Execution",
                "frequency": "High",
                "description": f"Completed {screenshot_count} interactions quickly",
                "automation_potential": "Medium",
                "confidence": "High"
            })
        
        return {
            "identified_patterns": patterns,
            "pattern_count": len(patterns),
            "most_significant_pattern": patterns[0] if patterns else None,
            "automation_confidence": "High" if len(patterns) > 2 else "Medium" if len(patterns) > 0 else "Low"
        }
    
    def _analyze_efficiency(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workflow efficiency."""
        screenshot_count = context.get('screenshot_count', 0)
        duration = context.get('duration', 0)
        
        # Efficiency metrics
        interactions_per_minute = (screenshot_count / max(duration, 1)) * 60 if duration > 0 else 0
        time_per_interaction = duration / max(screenshot_count, 1) if screenshot_count > 0 else 0
        
        # Efficiency rating
        if interactions_per_minute > 30:
            efficiency_rating = "Very High"
        elif interactions_per_minute > 20:
            efficiency_rating = "High"
        elif interactions_per_minute > 10:
            efficiency_rating = "Medium"
        else:
            efficiency_rating = "Low"
        
        # Bottleneck analysis
        bottlenecks = []
        if time_per_interaction > 10:
            bottlenecks.append("Slow interaction rate - potential for optimization")
        if screenshot_count > 50:
            bottlenecks.append("High interaction count - may indicate inefficiency")
        
        return {
            "efficiency_metrics": {
                "interactions_per_minute": f"{interactions_per_minute:.1f}",
                "time_per_interaction": f"{time_per_interaction:.1f} seconds",
                "efficiency_rating": efficiency_rating
            },
            "bottlenecks": bottlenecks,
            "optimization_potential": "High" if len(bottlenecks) > 0 else "Medium",
            "recommendations": [
                "Consider keyboard shortcuts",
                "Use automation tools",
                "Streamline repetitive tasks"
            ] if len(bottlenecks) > 0 else ["Workflow appears efficient"]
        }
    
    def _generate_optimization_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific optimization recommendations."""
        screenshot_count = context.get('screenshot_count', 0)
        duration = context.get('duration', 0)
        
        recommendations = []
        
        # High interaction recommendations
        if screenshot_count > 30:
            recommendations.append({
                "priority": "High",
                "category": "Automation",
                "recommendation": "Implement macro recording for repetitive tasks",
                "expected_benefit": f"Reduce interactions by {screenshot_count // 3}",
                "implementation_effort": "Medium"
            })
        
        # Duration-based recommendations
        if duration > 300:
            recommendations.append({
                "priority": "Medium",
                "category": "Process Optimization",
                "recommendation": "Break workflow into smaller, manageable tasks",
                "expected_benefit": f"Reduce total time by {duration // 4} seconds",
                "implementation_effort": "Low"
            })
        
        # Efficiency recommendations
        if screenshot_count > 10 and duration < 120:
            recommendations.append({
                "priority": "Low",
                "category": "Enhancement",
                "recommendation": "Add keyboard shortcuts for common actions",
                "expected_benefit": "Improve speed by 20-30%",
                "implementation_effort": "Low"
            })
        
        return recommendations
    
    def _create_implementation_roadmap(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create implementation roadmap for automation."""
        screenshot_count = context.get('screenshot_count', 0)
        duration = context.get('duration', 0)
        
        roadmap = {
            "phase_1": {
                "name": "Analysis and Planning",
                "duration": "1-2 weeks",
                "tasks": [
                    "Document current workflow steps",
                    "Identify automation opportunities",
                    "Select appropriate tools",
                    "Create implementation plan"
                ]
            },
            "phase_2": {
                "name": "Tool Selection",
                "duration": "1 week",
                "tasks": [
                    "Research automation tools",
                    "Test tool compatibility",
                    "Create proof of concept",
                    "Validate approach"
                ]
            },
            "phase_3": {
                "name": "Implementation",
                "duration": "2-4 weeks",
                "tasks": [
                    "Develop automation scripts",
                    "Test with sample data",
                    "Refine and optimize",
                    "Create documentation"
                ]
            },
            "phase_4": {
                "name": "Deployment and Monitoring",
                "duration": "1-2 weeks",
                "tasks": [
                    "Deploy automation solution",
                    "Train users",
                    "Monitor performance",
                    "Gather feedback and iterate"
                ]
            }
        }
        
        return roadmap
    
    def _generate_debugging_info(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate debugging information for troubleshooting."""
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "context_data": {
                "screenshot_count": context.get('screenshot_count', 0),
                "duration": context.get('duration', 0),
                "audio_length": len(context.get('audio_transcription', '')),
                "has_screenshots": bool(context.get('screenshots', [])),
                "session_data_keys": list(context.keys())
            },
            "analysis_metadata": {
                "analyzer_version": "1.0.0",
                "analysis_type": "detailed_workflow",
                "cache_hit": False,
                "processing_time": "N/A"
            },
            "potential_issues": [
                "High interaction count may indicate complex workflow",
                "Long duration may suggest inefficiency",
                "No audio transcription available for context"
            ] if context.get('screenshot_count', 0) > 30 else [],
            "recommendations": [
                "Record longer sessions for better pattern detection",
                "Enable audio recording for additional context",
                "Use consistent workflow patterns for better analysis"
            ]
        }
    
    def _get_automation_approach(self, score: float) -> str:
        """Get recommended automation approach based on score."""
        if score > 80:
            return "Full automation recommended - high potential for significant time savings"
        elif score > 60:
            return "Partial automation recommended - focus on repetitive tasks"
        elif score > 40:
            return "Selective automation recommended - automate specific high-value tasks"
        else:
            return "Manual optimization recommended - automation may not be cost-effective"
    
    def _generate_fallback_detailed_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback analysis when detailed analysis fails."""
        return {
            "session_summary": {
                "total_duration": f"{context.get('duration', 0)} seconds",
                "total_interactions": context.get('screenshot_count', 0),
                "session_type": "Basic computer activity",
                "complexity_level": "Simple"
            },
            "activity_patterns": {
                "detected_patterns": ["Basic computer usage"],
                "workflow_intensity": "Low"
            },
            "workflow_breakdown": {
                "workflow_phases": [{
                    "name": "General Activity",
                    "description": "Computer usage detected",
                    "automation_potential": "Low"
                }]
            },
            "automation_analysis": {
                "overall_score": "30/100",
                "recommended_approach": "Manual optimization recommended"
            },
            "debugging_info": {
                "analysis_timestamp": datetime.now().isoformat(),
                "fallback_used": True,
                "error_reason": "Detailed analysis failed"
            }
        }
