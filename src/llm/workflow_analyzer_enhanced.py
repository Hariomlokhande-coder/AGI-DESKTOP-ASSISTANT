"""
Enhanced workflow analyzer with OCR integration and advanced task detection.
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..error_handling.simple_logger import logger
from .local_llm_enhanced import LocalLLMClient
from .focused_analyzer import FocusedWorkflowAnalyzer
from .detailed_analyzer import DetailedWorkflowAnalyzer


class EnhancedWorkflowAnalyzer:
    """Enhanced workflow analyzer with OCR and advanced task detection."""
    
    def __init__(self, config):
        self.config = config
        self.local_llm = LocalLLMClient(config)
        self.focused_analyzer = FocusedWorkflowAnalyzer()
        self.detailed_analyzer = DetailedWorkflowAnalyzer()
        self.session_history = []
        self.pattern_database = {}
        
        logger.info("Enhanced WorkflowAnalyzer initialized with OCR integration")
    
    def analyze_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workflow with enhanced OCR and task detection."""
        try:
            logger.info(f"Analyzing enhanced workflow: {context.get('screenshot_count', 0)} screenshots, {context.get('duration', 0)}s duration")
            
            # Perform focused analysis first
            focused_result = self.focused_analyzer.analyze_focused_workflow(context)
            
            # Perform detailed analysis
            detailed_result = self.detailed_analyzer.analyze_detailed_workflow(context)
            
            # Perform enhanced local LLM analysis
            enhanced_result = self.local_llm.analyze_workflow(context)
            enhanced_data = json.loads(enhanced_result)
            
            # Combine all analyses
            combined_analysis = self._combine_analyses(focused_result, detailed_result, enhanced_data, context)
            
            # Update pattern database
            self._update_pattern_database(combined_analysis)
            
            # Store in session history
            self.session_history.append({
                'timestamp': datetime.now().isoformat(),
                'analysis': combined_analysis,
                'context': context
            })
            
            logger.info("Enhanced workflow analysis completed successfully")
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Enhanced workflow analysis failed: {e}")
            return self._fallback_analysis(context)
    
    def _combine_analyses(self, focused_result: Dict[str, Any], detailed_result: Dict[str, Any], 
                         enhanced_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Combine results from all analysis methods."""
        
        # Extract key information
        workflow_type = enhanced_data.get('workflow_type', 'general')
        detected_tasks = enhanced_data.get('detected_tasks', [])
        applications_used = enhanced_data.get('applications_used', [])
        
        # Create comprehensive result
        combined = {
            # Basic workflow information
            'workflow_type': workflow_type,
            'description': enhanced_data.get('description', 'Computer workflow detected'),
            'complexity': enhanced_data.get('complexity', 'moderate'),
            'automation_potential': enhanced_data.get('automation_potential', 'medium'),
            'automation_score': enhanced_data.get('automation_score', 50),
            'estimated_time': enhanced_data.get('estimated_time', 'Unknown'),
            
            # Detailed task information
            'detected_tasks': detected_tasks,
            'applications_used': applications_used,
            'steps': enhanced_data.get('steps', []),
            'repetitive_actions': enhanced_data.get('repetitive_actions', []),
            
            # Automation recommendations
            'automation_opportunities': enhanced_data.get('automation_opportunities', []),
            'recommended_tools': enhanced_data.get('recommended_tools', []),
            'implementation_difficulty': enhanced_data.get('implementation_difficulty', 'medium'),
            'time_savings': enhanced_data.get('time_savings', 'Unknown'),
            
            # Enhanced analysis details
            'detailed_analysis': enhanced_data.get('detailed_analysis', {}),
            'ocr_analysis': self._extract_ocr_insights(enhanced_data),
            'task_breakdown': self._create_comprehensive_task_breakdown(detected_tasks, applications_used),
            
            # Session context
            'session_info': {
                'duration': context.get('duration', 0),
                'screenshot_count': context.get('screenshot_count', 0),
                'audio_transcription': context.get('audio_transcription', ''),
                'timestamp': datetime.now().isoformat()
            },
            
            # Learning and patterns
            'learning_insights': self._generate_learning_insights(detected_tasks, applications_used),
            'pattern_analysis': self._analyze_patterns(detected_tasks, applications_used),
            
            # Quality metrics
            'analysis_quality': {
                'confidence_score': self._calculate_analysis_confidence(enhanced_data),
                'completeness_score': self._calculate_completeness_score(detected_tasks, applications_used),
                'reliability_score': self._calculate_reliability_score(enhanced_data)
            }
        }
        
        return combined
    
    def _extract_ocr_insights(self, enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract OCR-specific insights from enhanced analysis."""
        detailed_analysis = enhanced_data.get('detailed_analysis', {})
        
        return {
            'ocr_confidence': detailed_analysis.get('ocr_confidence', 0),
            'text_detection_quality': 'High' if detailed_analysis.get('ocr_confidence', 0) > 0.7 else 'Medium',
            'ui_element_detection': 'Active' if enhanced_data.get('applications_used') else 'Limited',
            'task_accuracy': 'High' if len(enhanced_data.get('detected_tasks', [])) > 0 else 'Low'
        }
    
    def _create_comprehensive_task_breakdown(self, tasks: List[Dict[str, Any]], applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comprehensive task breakdown analysis."""
        breakdown = {
            'total_tasks_detected': len(tasks),
            'total_applications_used': len(applications),
            'task_categories': {},
            'application_usage': {},
            'efficiency_metrics': {},
            'automation_potential_by_task': {}
        }
        
        # Categorize tasks
        for task in tasks:
            task_name = task.get('name', 'unknown')
            if task_name not in breakdown['task_categories']:
                breakdown['task_categories'][task_name] = {
                    'count': 0,
                    'total_confidence': 0,
                    'contexts': set()
                }
            
            breakdown['task_categories'][task_name]['count'] += 1
            breakdown['task_categories'][task_name]['total_confidence'] += task.get('average_confidence', 0)
            breakdown['task_categories'][task_name]['contexts'].update(task.get('contexts', []))
        
        # Convert sets to lists for JSON serialization
        for task_name, data in breakdown['task_categories'].items():
            data['contexts'] = list(data['contexts'])
            data['average_confidence'] = data['total_confidence'] / data['count'] if data['count'] > 0 else 0
            del data['total_confidence']
        
        # Analyze application usage
        for app in applications:
            app_name = app.get('name', 'unknown')
            breakdown['application_usage'][app_name] = {
                'usage_count': app.get('count', 0),
                'confidence': app.get('confidence', 0),
                'contexts': app.get('contexts', [])
            }
        
        # Calculate efficiency metrics
        total_tasks = sum(task.get('frequency', 1) for task in tasks)
        breakdown['efficiency_metrics'] = {
            'task_density': total_tasks,
            'application_switching': len(applications),
            'task_variety': len(tasks)
        }
        
        # Calculate automation potential by task
        automation_scores = {
            'data_entry': 0.9,
            'file_management': 0.8,
            'formatting': 0.7,
            'calculation': 0.9,
            'navigation': 0.5,
            'searching': 0.6
        }
        
        for task in tasks:
            task_name = task.get('name', 'unknown')
            if task_name in automation_scores:
                breakdown['automation_potential_by_task'][task_name] = {
                    'score': automation_scores[task_name],
                    'frequency': task.get('frequency', 1),
                    'total_potential': automation_scores[task_name] * task.get('frequency', 1)
                }
        
        return breakdown
    
    def _generate_learning_insights(self, tasks: List[Dict[str, Any]], applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate learning insights from the workflow analysis."""
        insights = {
            'skill_areas': [],
            'improvement_opportunities': [],
            'automation_candidates': [],
            'workflow_optimization': []
        }
        
        # Identify skill areas based on applications used
        skill_mapping = {
            'excel': 'Spreadsheet Management',
            'word': 'Document Processing',
            'file_explorer': 'File Organization',
            'browser': 'Web Research',
            'paint': 'Image Editing',
            'vscode': 'Programming/Development'
        }
        
        for app in applications:
            app_name = app.get('name', '')
            if app_name in skill_mapping:
                insights['skill_areas'].append(skill_mapping[app_name])
        
        # Identify improvement opportunities
        low_confidence_tasks = [task for task in tasks if task.get('average_confidence', 0) < 0.5]
        if low_confidence_tasks:
            insights['improvement_opportunities'].append("Improve task detection accuracy for better analysis")
        
        repetitive_tasks = [task for task in tasks if task.get('frequency', 1) > 2]
        if repetitive_tasks:
            insights['improvement_opportunities'].append("Consider automating repetitive tasks")
        
        # Identify automation candidates
        high_frequency_tasks = [task for task in tasks if task.get('frequency', 1) > 1]
        for task in high_frequency_tasks:
            insights['automation_candidates'].append({
                'task': task.get('name', ''),
                'frequency': task.get('frequency', 1),
                'potential': 'High' if task.get('frequency', 1) > 3 else 'Medium'
            })
        
        # Workflow optimization suggestions
        if len(applications) > 3:
            insights['workflow_optimization'].append("Consider reducing application switching for better efficiency")
        
        if len(tasks) > 10:
            insights['workflow_optimization'].append("Break down complex workflows into smaller, manageable steps")
        
        return insights
    
    def _analyze_patterns(self, tasks: List[Dict[str, Any]], applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in the workflow."""
        patterns = {
            'task_sequences': [],
            'application_workflows': [],
            'time_patterns': {},
            'efficiency_patterns': []
        }
        
        # Analyze task sequences
        task_names = [task.get('name', '') for task in tasks]
        if len(task_names) > 1:
            patterns['task_sequences'] = task_names
        
        # Analyze application workflows
        app_names = [app.get('name', '') for app in applications]
        if len(app_names) > 1:
            patterns['application_workflows'] = app_names
        
        # Identify efficiency patterns
        high_confidence_tasks = [task for task in tasks if task.get('average_confidence', 0) > 0.8]
        if high_confidence_tasks:
            patterns['efficiency_patterns'].append("High confidence task detection indicates good workflow clarity")
        
        repetitive_tasks = [task for task in tasks if task.get('frequency', 1) > 1]
        if repetitive_tasks:
            patterns['efficiency_patterns'].append("Repetitive tasks detected - automation opportunity")
        
        return patterns
    
    def _calculate_analysis_confidence(self, enhanced_data: Dict[str, Any]) -> float:
        """Calculate overall analysis confidence."""
        confidence_factors = []
        
        # OCR confidence
        detailed_analysis = enhanced_data.get('detailed_analysis', {})
        ocr_confidence = detailed_analysis.get('ocr_confidence', 0)
        confidence_factors.append(ocr_confidence)
        
        # Task detection confidence
        tasks = enhanced_data.get('detected_tasks', [])
        if tasks:
            avg_task_confidence = sum(task.get('average_confidence', 0) for task in tasks) / len(tasks)
            confidence_factors.append(avg_task_confidence)
        
        # Application detection confidence
        applications = enhanced_data.get('applications_used', [])
        if applications:
            avg_app_confidence = sum(app.get('confidence', 0) for app in applications) / len(applications)
            confidence_factors.append(avg_app_confidence)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
    def _calculate_completeness_score(self, tasks: List[Dict[str, Any]], applications: List[Dict[str, Any]]) -> float:
        """Calculate completeness score of the analysis."""
        score = 0.0
        
        # Base score for having any analysis
        if tasks or applications:
            score += 0.5
        
        # Bonus for multiple task types
        if len(tasks) > 1:
            score += 0.2
        
        # Bonus for multiple applications
        if len(applications) > 1:
            score += 0.2
        
        # Bonus for high confidence detections
        high_confidence_count = sum(1 for task in tasks if task.get('average_confidence', 0) > 0.7)
        if high_confidence_count > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_reliability_score(self, enhanced_data: Dict[str, Any]) -> float:
        """Calculate reliability score of the analysis."""
        reliability_factors = []
        
        # Check for detailed analysis
        detailed_analysis = enhanced_data.get('detailed_analysis', {})
        if detailed_analysis:
            reliability_factors.append(0.3)
        
        # Check for OCR analysis
        if detailed_analysis.get('ocr_confidence', 0) > 0.5:
            reliability_factors.append(0.3)
        
        # Check for task detection
        tasks = enhanced_data.get('detected_tasks', [])
        if tasks:
            reliability_factors.append(0.2)
        
        # Check for application detection
        applications = enhanced_data.get('applications_used', [])
        if applications:
            reliability_factors.append(0.2)
        
        return sum(reliability_factors)
    
    def _update_pattern_database(self, analysis: Dict[str, Any]):
        """Update the pattern database with new analysis."""
        workflow_type = analysis.get('workflow_type', 'general')
        
        if workflow_type not in self.pattern_database:
            self.pattern_database[workflow_type] = {
                'count': 0,
                'total_score': 0,
                'common_tasks': {},
                'common_applications': {},
                'last_seen': None
            }
        
        # Update counts and scores
        self.pattern_database[workflow_type]['count'] += 1
        self.pattern_database[workflow_type]['total_score'] += analysis.get('automation_score', 50)
        self.pattern_database[workflow_type]['last_seen'] = datetime.now().isoformat()
        
        # Update common tasks
        tasks = analysis.get('detected_tasks', [])
        for task in tasks:
            task_name = task.get('name', 'unknown')
            if task_name not in self.pattern_database[workflow_type]['common_tasks']:
                self.pattern_database[workflow_type]['common_tasks'][task_name] = 0
            self.pattern_database[workflow_type]['common_tasks'][task_name] += 1
        
        # Update common applications
        applications = analysis.get('applications_used', [])
        for app in applications:
            app_name = app.get('name', 'unknown')
            if app_name not in self.pattern_database[workflow_type]['common_applications']:
                self.pattern_database[workflow_type]['common_applications'][app_name] = 0
            self.pattern_database[workflow_type]['common_applications'][app_name] += 1
    
    def _fallback_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when enhanced analysis fails."""
        return {
            'workflow_type': 'general',
            'description': 'Computer workflow detected',
            'complexity': 'moderate',
            'automation_potential': 'medium',
            'automation_score': 50,
            'estimated_time': 'Unknown',
            'detected_tasks': [],
            'applications_used': [],
            'steps': ['Workflow analysis'],
            'repetitive_actions': ['General computer activity'],
            'automation_opportunities': ['Process review and optimization'],
            'recommended_tools': ['Manual analysis', 'Process documentation'],
            'implementation_difficulty': 'medium',
            'time_savings': 'Unknown',
            'detailed_analysis': {},
            'ocr_analysis': {'ocr_confidence': 0, 'text_detection_quality': 'Low'},
            'task_breakdown': {'total_tasks_detected': 0, 'total_applications_used': 0},
            'learning_insights': {'skill_areas': [], 'improvement_opportunities': []},
            'pattern_analysis': {'task_sequences': [], 'efficiency_patterns': []},
            'analysis_quality': {'confidence_score': 0.3, 'completeness_score': 0.3, 'reliability_score': 0.3},
            'session_info': {
                'duration': context.get('duration', 0),
                'screenshot_count': context.get('screenshot_count', 0),
                'audio_transcription': context.get('audio_transcription', ''),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def get_pattern_database(self) -> Dict[str, Any]:
        """Get the current pattern database."""
        return self.pattern_database
    
    def get_session_history(self) -> List[Dict[str, Any]]:
        """Get the session history."""
        return self.session_history
