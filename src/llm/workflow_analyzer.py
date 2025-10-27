"""Enhanced workflow analysis and pattern detection with local LLM."""

from typing import List, Dict, Any, Optional
import json
import logging

from .external_llm import LLMClient
from .focused_analyzer import FocusedWorkflowAnalyzer
from .detailed_analyzer import DetailedWorkflowAnalyzer
from .workflow_analyzer_enhanced import EnhancedWorkflowAnalyzer
from ..error_handling.exceptions import ProcessingError
from ..error_handling.logger import logger


class WorkflowAnalyzer:
    """Enhanced workflow analyzer with comprehensive error handling and local LLM integration."""
    
    def __init__(self, config):
        self.config = config
        
        try:
            # Use external LLM client
            self.llm_client = LLMClient(config)
            # Use focused analyzer for pattern recognition
            self.focused_analyzer = FocusedWorkflowAnalyzer()
            # Use detailed analyzer for comprehensive analysis
            self.detailed_analyzer = DetailedWorkflowAnalyzer()
            # Use enhanced analyzer for OCR and advanced task detection
            self.enhanced_analyzer = EnhancedWorkflowAnalyzer(config)
            logger.info("WorkflowAnalyzer initialized with external LLM, focused analyzer, detailed analyzer, and enhanced analyzer")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise ProcessingError(f"Failed to initialize WorkflowAnalyzer: {e}")
    
    def analyze_session(self, session_data: Dict[str, Any], screenshots: List[str], 
                       audio_transcription: str) -> List[Dict[str, Any]]:
        """Analyze a complete session to detect workflows with comprehensive error handling."""
        try:
            if not session_data:
                logger.warning("No session data provided")
                return self._generate_fallback_workflows(session_data, screenshots, audio_transcription)
            
            logger.info(f"Analyzing session with {len(screenshots)} screenshots")
            
            # Build context from session data
            context = {
                'duration': session_data.get('duration', 0),
                'screenshot_count': len(screenshots),
                'audio_transcription': audio_transcription[:500] if audio_transcription else 'No audio available',  # Limit length
                'screenshots': screenshots[:5] if screenshots else []  # First 5 screenshots
            }
            
            # Prepare data for analysis
            analysis_text = self._prepare_analysis_text(session_data, screenshots, audio_transcription)
            
            # Use enhanced analyzer first for comprehensive analysis
            try:
                enhanced_analysis = self.enhanced_analyzer.analyze_workflow(context)
                workflows = [enhanced_analysis]
                logger.info(f"Enhanced analysis completed. Found workflow: {enhanced_analysis.get('workflow_type', 'unknown')}")
                return workflows
                
            except Exception as e:
                logger.error(f"Error in focused analysis: {e}")
                
                # Fallback to external LLM
                try:
                    analysis_result = self.llm_client.analyze_workflow(context)
                    
                    # Parse the analysis result
                    if isinstance(analysis_result, str):
                        try:
                            analysis_data = json.loads(analysis_result)
                        except json.JSONDecodeError:
                            analysis_data = {
                                'description': analysis_result[:200],
                                'workflow_type': 'general',
                                'complexity': 'moderate',
                                'automation_potential': 'medium',
                                'automation_score': 50,
                                'steps': analysis_result.split('.')[:5],
                                'estimated_time': 'Unknown',
                                'recommendations': []
                            }
                    else:
                        analysis_data = analysis_result
                    
                    workflows = [analysis_data]
                    logger.info(f"External LLM analysis completed. Found {len(workflows)} workflows")
                    return workflows
                    
                except Exception as e2:
                    logger.error(f"Error in external LLM analysis: {e2}")
                    return self._generate_fallback_workflows(session_data, screenshots, audio_transcription)
            
        except Exception as e:
            logger.error(f"Error analyzing session: {e}", exc_info=True)
            return self._generate_fallback_workflows(session_data, screenshots, audio_transcription)
    
    def get_detailed_analysis(self, session_data: Dict[str, Any], screenshots: List[str], 
                             audio_transcription: str) -> Dict[str, Any]:
        """Get comprehensive detailed analysis of the workflow."""
        try:
            # Build context for detailed analysis
            context = {
                'duration': session_data.get('duration', 0),
                'screenshot_count': len(screenshots),
                'audio_transcription': audio_transcription[:500] if audio_transcription else '',
                'screenshots': screenshots[:5] if screenshots else []
            }
            
            # Get detailed analysis
            detailed_analysis = self.detailed_analyzer.analyze_detailed_workflow(context)
            
            logger.info("Detailed analysis completed successfully")
            return detailed_analysis
            
        except Exception as e:
            logger.error(f"Error in detailed analysis: {e}", exc_info=True)
            return self.detailed_analyzer._generate_fallback_detailed_analysis(context)
    
    def _prepare_analysis_text(self, session_data: Dict[str, Any], screenshots: List[str], 
                              audio_transcription: str) -> str:
        """Prepare text for analysis."""
        try:
            text_parts = []
            
            # Add duration info
            if 'duration' in session_data:
                text_parts.append(f"Session duration: {session_data['duration']}s")
            
            # Add screenshot count
            if screenshots:
                text_parts.append(f"Captured {len(screenshots)} screenshots")
            
            # Add audio transcription
            if audio_transcription:
                # Limit transcription length
                truncated_transcription = audio_transcription[:500]
                text_parts.append(f"Audio: {truncated_transcription}")
            
            # Add session metadata
            if 'start_time' in session_data:
                text_parts.append(f"Started at: {session_data['start_time']}")
            if 'end_time' in session_data:
                text_parts.append(f"Ended at: {session_data['end_time']}")
            
            return ". ".join(text_parts)
            
        except Exception as e:
            logger.error(f"Error preparing analysis text: {e}")
            return "Workflow analysis data"
    
    def _convert_to_workflows(self, analysis_data: Dict[str, Any], 
                             context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert analysis data to workflow list."""
        try:
            workflows = []
            
            # Create workflow from analysis
            workflow = {
                'description': analysis_data.get('description', 'Detected workflow'),
                'workflow_type': analysis_data.get('workflow_type', 'general'),
                'complexity': analysis_data.get('complexity', 'moderate'),
                'automation_potential': analysis_data.get('automation_potential', 'medium'),
                'automation_score': analysis_data.get('automation_score', 50),
                'steps': analysis_data.get('steps', []),
                'estimated_time': analysis_data.get('estimated_time', 'Unknown'),
                'recommendations': analysis_data.get('recommendations', []),
                'session_context': context
            }
            
            workflows.append(workflow)
            
            # If multiple patterns detected, create additional workflows
            if context.get('screenshot_count', 0) > 10:
                # High activity suggests multiple sub-workflows
                additional_workflows = self._detect_sub_workflows(analysis_data, context)
                workflows.extend(additional_workflows)
            
            return workflows
            
        except Exception as e:
            logger.error(f"Error converting to workflows: {e}")
            return self._generate_fallback_workflows(None, None, None)
    
    def _detect_sub_workflows(self, analysis_data: Dict[str, Any], 
                             context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect sub-workflows in complex sessions."""
        try:
            sub_workflows = []
            
            # Based on screenshot count, estimate number of sub-workflows
            screenshot_count = context.get('screenshot_count', 0)
            
            if screenshot_count > 20:
                # Complex session with multiple activities
                for i in range(min(2, screenshot_count // 10)):
                    sub_workflow = {
                        'description': f"Sub-workflow {i+1}: Continued activity detected",
                        'workflow_type': analysis_data.get('workflow_type', 'general'),
                        'complexity': 'moderate',
                        'automation_potential': 'medium',
                        'automation_score': 40,
                        'steps': [f"Continue workflow activity {i+1}"],
                        'estimated_time': '15 minutes',
                        'recommendations': ['Monitor for patterns']
                    }
                    sub_workflows.append(sub_workflow)
            
            return sub_workflows
            
        except Exception as e:
            logger.error(f"Error detecting sub-workflows: {e}")
            return []
    
    def _generate_fallback_workflows(self, session_data: Optional[Dict[str, Any]], 
                                    screenshots: Optional[List[str]], 
                                    audio_transcription: Optional[str]) -> List[Dict[str, Any]]:
        """Generate fallback workflows when analysis fails."""
        try:
            screenshot_count = len(screenshots) if screenshots else 0
            duration = session_data.get('duration', 0) if session_data else 0
            
            # Generate more specific fallback based on activity level
            if screenshot_count > 20:
                workflow = {
                    'description': f'High-activity workflow detected with {screenshot_count} screenshots',
                    'workflow_type': 'data_entry',
                    'complexity': 'complex',
                    'automation_potential': 'high',
                    'automation_score': 75,
                    'steps': [
                        'User performed extensive computer activity',
                        'Multiple interactions captured',
                        'Potential repetitive patterns detected',
                        'Review screenshots for automation opportunities'
                    ],
                    'estimated_time': f'{duration // 60} minutes' if duration > 60 else 'Less than 1 minute',
                    'repetitive_actions': ['Multiple user interactions', 'Screen navigation'],
                    'automation_opportunities': ['Automate repetitive tasks', 'Create workflow templates'],
                    'recommended_tools': ['Python automation scripts', 'RPA tools', 'Macro recording'],
                    'implementation_difficulty': 'medium',
                    'time_savings': f'{duration // 3} minutes per execution' if duration > 0 else 'Significant'
                }
            elif screenshot_count > 10:
                workflow = {
                    'description': f'Moderate-activity workflow with {screenshot_count} screenshots',
                    'workflow_type': 'file_operations',
                    'complexity': 'moderate',
                    'automation_potential': 'medium',
                    'automation_score': 60,
                    'steps': [
                        'User performed computer tasks',
                        'File or application interactions detected',
                        'Review captured activity for patterns'
                    ],
                    'estimated_time': f'{duration // 60} minutes' if duration > 60 else 'Less than 1 minute',
                    'repetitive_actions': ['Application usage', 'File operations'],
                    'automation_opportunities': ['Streamline common tasks', 'Create shortcuts'],
                    'recommended_tools': ['Custom scripts', 'Application macros'],
                    'implementation_difficulty': 'easy',
                    'time_savings': f'{duration // 4} minutes per execution' if duration > 0 else 'Moderate'
                }
            else:
                workflow = {
                    'description': f'Basic computer activity with {screenshot_count} screenshots',
                    'workflow_type': 'navigation',
                    'complexity': 'simple',
                    'automation_potential': 'low',
                    'automation_score': 30,
                    'steps': [
                        'Basic computer usage detected',
                        'Limited activity captured',
                        'Consider recording longer sessions for better analysis'
                    ],
                    'estimated_time': f'{duration // 60} minutes' if duration > 60 else 'Less than 1 minute',
                    'repetitive_actions': ['General computer usage'],
                    'automation_opportunities': ['Document common tasks', 'Create process guides'],
                    'recommended_tools': ['Manual documentation', 'Process mapping'],
                    'implementation_difficulty': 'easy',
                    'time_savings': 'Minimal'
                }
            
            return [workflow]
            
        except Exception as e:
            logger.error(f"Error generating fallback workflows: {e}")
            # Return a basic workflow even if everything fails
            return [{
                'description': 'Computer activity detected',
                'workflow_type': 'general',
                'complexity': 'simple',
                'automation_potential': 'low',
                'automation_score': 25,
                'steps': ['Computer activity was captured'],
                'estimated_time': 'Unknown',
                'repetitive_actions': ['General computer usage'],
                'automation_opportunities': ['Review captured activity'],
                'recommended_tools': ['Manual analysis'],
                'implementation_difficulty': 'easy',
                'time_savings': 'Unknown'
            }]
    
    def detect_patterns(self, screenshots: List[str]) -> List[Dict[str, Any]]:
        """Detect repetitive patterns in screenshots with enhanced analysis."""
        try:
            patterns = []
            
            if not screenshots:
                logger.warning("No screenshots provided for pattern detection")
                return patterns
            
            screenshot_count = len(screenshots)
            
            # Pattern 1: Repetitive Activity
            if screenshot_count > 5:
                patterns.append({
                    'type': 'Repetitive Activity',
                    'confidence': 'Medium',
                    'description': f'User activity captured over {screenshot_count} screenshots',
                    'frequency': 'High',
                    'automation_potential': 'Medium'
                })
            
            # Pattern 2: High Frequency Activity
            if screenshot_count > 15:
                patterns.append({
                    'type': 'High Frequency Activity',
                    'confidence': 'High',
                    'description': f'Dense activity captured with {screenshot_count} screenshots',
                    'frequency': 'Very High',
                    'automation_potential': 'High'
                })
            
            # Pattern 3: Regular Intervals
            if screenshot_count > 10:
                patterns.append({
                    'type': 'Regular Pattern',
                    'confidence': 'Low',
                    'description': 'Potential regular intervals detected in screenshots',
                    'frequency': 'Medium',
                    'automation_potential': 'Low'
                })
            
            logger.info(f"Detected {len(patterns)} patterns from {screenshot_count} screenshots")
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return []
    
    def generate_workflow_recommendations(self, workflows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate automation recommendations from detected workflows with enhanced logic."""
        try:
            if not workflows:
                logger.warning("No workflows provided for recommendations")
                return []
            
            recommendations = []
            
            for i, workflow in enumerate(workflows, 1):
                try:
                    potential = workflow.get('automation_potential', 'Medium')
                    automation_score = workflow.get('automation_score', 50)
                    workflow_type = workflow.get('workflow_type', 'general')
                    complexity = workflow.get('complexity', 'moderate')
                    
                    # Generate comprehensive recommendations
                    recommendation = {
                        'workflow_id': i,
                        'description': workflow.get('description', 'Unknown'),
                        'workflow_type': workflow_type,
                        'complexity': complexity,
                        'automation_potential': potential,
                        'automation_score': automation_score,
                        'recommended_tools': self._get_tool_recommendations(workflow, workflow_type),
                        'steps': workflow.get('steps', []),
                        'estimated_time': workflow.get('estimated_time', 'Unknown'),
                        'recommendations': workflow.get('recommendations', []),
                        'implementation_suggestions': self._get_implementation_suggestions(workflow_type, complexity, automation_score)
                    }
                    
                    recommendations.append(recommendation)
                    
                except Exception as e:
                    logger.error(f"Error processing workflow {i}: {e}")
                    continue
            
            logger.info(f"Generated recommendations for {len(recommendations)} workflows")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating workflow recommendations: {e}")
            return []
    
    def _get_tool_recommendations(self, workflow: Dict[str, Any], 
                                 workflow_type: str) -> List[str]:
        """Recommend automation tools for a workflow with comprehensive options."""
        try:
            tools = []
            description = workflow.get('description', '').lower()
            automation_score = workflow.get('automation_score', 50)
            
            # High automation potential tools
            if automation_score >= 70:
                if 'file' in description or 'folder' in description or workflow_type == 'file_operations':
                    tools.extend(['Python scripts', 'PowerShell (Windows)', 'Bash scripts (Linux/Mac)'])
                    tools.append('Robotic Process Automation (RPA)')
                
                if 'data' in description or 'excel' in description or workflow_type == 'data_analysis':
                    tools.extend(['Python pandas', 'Excel VBA macros', 'Power BI'])
                    tools.append('Apache Airflow (for scheduling)')
                
                if 'browser' in description or 'web' in description or workflow_type == 'browser_operations':
                    tools.extend(['Selenium WebDriver', 'Playwright', 'Puppeteer'])
                    tools.append('Browser automation framework')
                
                if 'text' in description or workflow_type == 'text_operations':
                    tools.extend(['Regular expressions', 'Text processing scripts'])
                    tools.append('Natural language processing libraries')
            
            # Medium automation potential tools
            elif automation_score >= 40:
                tools.extend(['Custom Python scripts', 'Batch automation'])
                if 'file' in description or workflow_type == 'file_operations':
                    tools.append('File system automation libraries')
            
            # Always include general options
            if not tools:
                tools = ['Custom automation script', 'Manual review and documentation']
            
            return tools
            
        except Exception as e:
            logger.error(f"Error getting tool recommendations: {e}")
            return ['Custom automation script']
    
    def _get_implementation_suggestions(self, workflow_type: str, complexity: str, 
                                      automation_score: int) -> List[str]:
        """Get implementation suggestions based on workflow characteristics."""
        try:
            suggestions = []
            
            # High automation potential
            if automation_score >= 70:
                suggestions.append("Consider implementing automated script")
                suggestions.append("Document all steps for automation")
                if complexity in ['complex', 'very_complex']:
                    suggestions.append("Break into smaller automated tasks")
            
            # Medium automation potential
            elif automation_score >= 40:
                suggestions.append("Consider partial automation for repetitive parts")
                suggestions.append("Create templates or scripts for common operations")
            
            # Low automation potential
            else:
                suggestions.append("Focus on documentation rather than automation")
                suggestions.append("Create runbooks for manual execution")
            
            # Workflow-specific suggestions
            if workflow_type == 'file_operations':
                suggestions.append("Consider batch processing for file operations")
            elif workflow_type == 'data_analysis':
                suggestions.append("Create reusable analysis templates")
            elif workflow_type == 'development_tasks':
                suggestions.append("Use CI/CD pipelines for automation")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting implementation suggestions: {e}")
            return ['Review workflow for automation opportunities']
