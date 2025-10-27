"""Focused workflow analyzer for specific patterns like Excel operations."""

import json
import time
from typing import Dict, List, Any, Optional
from ..error_handling.simple_logger import logger


class FocusedWorkflowAnalyzer:
    """Analyzer focused on specific workflow patterns like Excel operations."""
    
    def __init__(self):
        self.patterns = self._load_patterns()
        self.frequency_tracker = {}
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load focused workflow patterns."""
        return {
            'excel_operations': {
                'keywords': ['excel', 'spreadsheet', 'cell', 'formula', 'data', 'table', 'chart'],
                'actions': ['open', 'save', 'edit', 'format', 'calculate', 'sort', 'filter'],
                'automation_score': 85,
                'complexity_mapping': {
                    'simple': ['open', 'save'],
                    'moderate': ['edit', 'format', 'calculate'],
                    'complex': ['sort', 'filter', 'chart', 'formula']
                }
            },
            'data_entry': {
                'keywords': ['form', 'input', 'field', 'submit', 'validate', 'database'],
                'actions': ['type', 'click', 'select', 'submit', 'validate'],
                'automation_score': 90,
                'complexity_mapping': {
                    'simple': ['type', 'click'],
                    'moderate': ['select', 'submit'],
                    'complex': ['validate', 'database']
                }
            },
            'file_management': {
                'keywords': ['file', 'folder', 'copy', 'move', 'rename', 'delete'],
                'actions': ['navigate', 'select', 'copy', 'move', 'rename', 'delete'],
                'automation_score': 80,
                'complexity_mapping': {
                    'simple': ['navigate', 'select'],
                    'moderate': ['copy', 'move'],
                    'complex': ['rename', 'delete', 'organize']
                }
            },
            'text_processing': {
                'keywords': ['document', 'text', 'word', 'edit', 'format', 'paragraph'],
                'actions': ['type', 'edit', 'format', 'save', 'print'],
                'automation_score': 70,
                'complexity_mapping': {
                    'simple': ['type', 'save'],
                    'moderate': ['edit', 'format'],
                    'complex': ['paragraph', 'layout']
                }
            }
        }
    
    def analyze_focused_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workflow with focus on specific patterns."""
        try:
            screenshot_count = context.get('screenshot_count', 0)
            duration = context.get('duration', 0)
            audio_transcription = context.get('audio_transcription', '')
            
            # Detect workflow type based on patterns
            workflow_type = self._detect_workflow_type(context)
            
            # Analyze complexity and automation potential
            complexity = self._assess_complexity(screenshot_count, duration)
            automation_score = self._calculate_automation_score(workflow_type, screenshot_count, duration)
            
            # Generate specific analysis
            analysis = self._generate_focused_analysis(
                workflow_type, complexity, automation_score, screenshot_count, duration
            )
            
            # Track frequency for learning
            self._track_pattern_frequency(workflow_type, automation_score)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Focused analysis error: {e}")
            return self._generate_fallback_analysis()
    
    def _detect_workflow_type(self, context: Dict[str, Any]) -> str:
        """Detect the most likely workflow type based on actual user behavior."""
        audio_text = context.get('audio_transcription', '').lower()
        screenshot_count = context.get('screenshot_count', 0)
        duration = context.get('duration', 0)
        
        # More conservative detection - only detect if there's strong evidence
        scores = {}
        
        # Check for explicit keywords in audio (more reliable)
        for workflow_type, pattern in self.patterns.items():
            score = 0
            
            # Only score if keywords are explicitly mentioned
            keyword_matches = 0
            for keyword in pattern['keywords']:
                if keyword in audio_text:
                    keyword_matches += 1
                    score += 3  # Higher weight for explicit mentions
            
            # Only if we have multiple keyword matches
            if keyword_matches >= 2:
                scores[workflow_type] = score
        
        # If no explicit keywords, analyze based on activity patterns
        if not scores or max(scores.values()) < 4:
            # Analyze based on activity level and patterns
            if screenshot_count > 25 and duration > 120:
                # High activity, longer duration - likely complex workflow
                return 'general'  # Don't assume specific type without evidence
            elif screenshot_count > 15:
                # Moderate activity
                return 'general'
            else:
                # Low activity
                return 'general'
        
        # Return highest scoring workflow type only if score is significant
        if scores and max(scores.values()) >= 4:
            return max(scores, key=scores.get)
        
        return 'general'
    
    def _assess_complexity(self, screenshot_count: int, duration: int) -> str:
        """Assess workflow complexity."""
        if screenshot_count > 30 or duration > 300:
            return 'very_complex'
        elif screenshot_count > 20 or duration > 180:
            return 'complex'
        elif screenshot_count > 10 or duration > 60:
            return 'moderate'
        else:
            return 'simple'
    
    def _calculate_automation_score(self, workflow_type: str, screenshot_count: int, duration: int) -> int:
        """Calculate automation potential score based on actual patterns."""
        
        # Start with conservative base score
        base_score = 30
        
        # Adjust based on activity level (more screenshots = more repetitive potential)
        if screenshot_count > 30:
            activity_score = 40  # High activity
        elif screenshot_count > 20:
            activity_score = 30  # Moderate activity
        elif screenshot_count > 10:
            activity_score = 20  # Low activity
        else:
            activity_score = 10  # Very low activity
        
        # Adjust based on duration (longer sessions = more repetitive)
        if duration > 300:  # 5+ minutes
            duration_score = 20
        elif duration > 180:  # 3+ minutes
            duration_score = 15
        elif duration > 60:   # 1+ minutes
            duration_score = 10
        else:
            duration_score = 5
        
        # Calculate final score
        final_score = base_score + activity_score + duration_score
        
        # Cap the score to be more realistic
        return min(85, max(10, final_score))
    
    def _generate_focused_analysis(self, workflow_type: str, complexity: str, 
                                 automation_score: int, screenshot_count: int, duration: int) -> Dict[str, Any]:
        """Generate focused analysis based on workflow type."""
        
        if workflow_type == 'excel_operations':
            return self._analyze_excel_workflow(complexity, automation_score, screenshot_count, duration)
        elif workflow_type == 'data_entry':
            return self._analyze_data_entry_workflow(complexity, automation_score, screenshot_count, duration)
        elif workflow_type == 'file_management':
            return self._analyze_file_management_workflow(complexity, automation_score, screenshot_count, duration)
        elif workflow_type == 'text_processing':
            return self._analyze_text_processing_workflow(complexity, automation_score, screenshot_count, duration)
        else:
            return self._analyze_general_workflow(complexity, automation_score, screenshot_count, duration)
    
    def _analyze_excel_workflow(self, complexity: str, automation_score: int, 
                              screenshot_count: int, duration: int) -> Dict[str, Any]:
        """Analyze Excel-specific workflow."""
        steps = [
            "Open Excel application",
            "Navigate to spreadsheet",
            "Select cells or data range",
            "Perform operations (edit, format, calculate)",
            "Save spreadsheet"
        ]
        
        if complexity in ['complex', 'very_complex']:
            steps.extend([
                "Apply formulas or functions",
                "Create charts or graphs",
                "Sort or filter data",
                "Format cells and layout"
            ])
        
        repetitive_actions = ["Cell selection", "Data entry", "Formula application", "Formatting"]
        automation_opportunities = [
            "Automated data entry from external sources",
            "Formula generation and application",
            "Chart creation and formatting",
            "Data validation and cleaning"
        ]
        recommended_tools = [
            "Python pandas for data processing",
            "Excel VBA macros for automation",
            "Power Query for data transformation",
            "OpenPyXL for Python Excel automation"
        ]
        
        return {
            "description": f"Excel spreadsheet workflow with {screenshot_count} interactions",
            "workflow_type": "excel_operations",
            "complexity": complexity,
            "automation_potential": self._score_to_label(automation_score),
            "automation_score": automation_score,
            "estimated_time": f"{duration // 60} minutes" if duration > 60 else "Less than 1 minute",
            "steps": steps,
            "repetitive_actions": repetitive_actions,
            "automation_opportunities": automation_opportunities,
            "recommended_tools": recommended_tools,
            "implementation_difficulty": "medium" if automation_score > 70 else "easy",
            "time_savings": f"{duration // 3} minutes per spreadsheet"
        }
    
    def _analyze_data_entry_workflow(self, complexity: str, automation_score: int,
                                   screenshot_count: int, duration: int) -> Dict[str, Any]:
        """Analyze data entry workflow."""
        steps = [
            "Open data entry form or application",
            "Navigate to input fields",
            "Enter data systematically",
            "Validate entered information",
            "Submit or save data"
        ]
        
        repetitive_actions = ["Field navigation", "Data typing", "Form submission", "Validation"]
        automation_opportunities = [
            "Automated form filling from database",
            "Data validation scripts",
            "Batch data entry processing",
            "Auto-completion and suggestions"
        ]
        recommended_tools = [
            "Selenium WebDriver for web forms",
            "Python pandas for data processing",
            "AutoHotkey for desktop automation",
            "Power Automate for Microsoft forms"
        ]
        
        return {
            "description": f"Data entry workflow with {screenshot_count} form interactions",
            "workflow_type": "data_entry",
            "complexity": complexity,
            "automation_potential": self._score_to_label(automation_score),
            "automation_score": automation_score,
            "estimated_time": f"{duration // 60} minutes" if duration > 60 else "Less than 1 minute",
            "steps": steps,
            "repetitive_actions": repetitive_actions,
            "automation_opportunities": automation_opportunities,
            "recommended_tools": recommended_tools,
            "implementation_difficulty": "easy" if automation_score > 80 else "medium",
            "time_savings": f"{duration // 2} minutes per batch"
        }
    
    def _analyze_file_management_workflow(self, complexity: str, automation_score: int,
                                        screenshot_count: int, duration: int) -> Dict[str, Any]:
        """Analyze file management workflow."""
        steps = [
            "Navigate to source directory",
            "Select files for processing",
            "Apply file operations (copy, move, rename)",
            "Organize files in destination",
            "Verify operation completion"
        ]
        
        repetitive_actions = ["File selection", "Directory navigation", "File operations", "Organization"]
        automation_opportunities = [
            "Batch file processing scripts",
            "Automated file organization",
            "File renaming and sorting",
            "Duplicate file detection and removal"
        ]
        recommended_tools = [
            "Python os/pathlib for file operations",
            "PowerShell scripts for Windows",
            "Bash scripts for Linux/Mac",
            "File management automation tools"
        ]
        
        return {
            "description": f"File management workflow with {screenshot_count} file operations",
            "workflow_type": "file_management",
            "complexity": complexity,
            "automation_potential": self._score_to_label(automation_score),
            "automation_score": automation_score,
            "estimated_time": f"{duration // 60} minutes" if duration > 60 else "Less than 1 minute",
            "steps": steps,
            "repetitive_actions": repetitive_actions,
            "automation_opportunities": automation_opportunities,
            "recommended_tools": recommended_tools,
            "implementation_difficulty": "easy",
            "time_savings": f"{duration // 4} minutes per batch"
        }
    
    def _analyze_text_processing_workflow(self, complexity: str, automation_score: int,
                                        screenshot_count: int, duration: int) -> Dict[str, Any]:
        """Analyze text processing workflow."""
        steps = [
            "Open text editor or word processor",
            "Navigate to document area",
            "Enter or edit text content",
            "Apply formatting and styling",
            "Save document"
        ]
        
        repetitive_actions = ["Text entry", "Formatting", "Navigation", "Save operations"]
        automation_opportunities = [
            "Text templates and macros",
            "Auto-formatting and styling",
            "Content generation from templates",
            "Document processing automation"
        ]
        recommended_tools = [
            "Microsoft Word macros",
            "Python text processing libraries",
            "Document automation tools",
            "Content management systems"
        ]
        
        return {
            "description": f"Text processing workflow with {screenshot_count} text interactions",
            "workflow_type": "text_processing",
            "complexity": complexity,
            "automation_potential": self._score_to_label(automation_score),
            "automation_score": automation_score,
            "estimated_time": f"{duration // 60} minutes" if duration > 60 else "Less than 1 minute",
            "steps": steps,
            "repetitive_actions": repetitive_actions,
            "automation_opportunities": automation_opportunities,
            "recommended_tools": recommended_tools,
            "implementation_difficulty": "easy",
            "time_savings": f"{duration // 5} minutes per document"
        }
    
    def _analyze_general_workflow(self, complexity: str, automation_score: int,
                               screenshot_count: int, duration: int) -> Dict[str, Any]:
        """Analyze general workflow based on actual user behavior."""
        
        # Generate more specific analysis based on activity patterns
        if screenshot_count > 30:
            description = f"High-activity computer workflow with {screenshot_count} interactions"
            steps = [
                "User performed extensive computer activity",
                "Multiple applications or tasks were used",
                "Complex workflow with many steps",
                "Potential for automation analysis"
            ]
            repetitive_actions = ["Multiple application usage", "Complex task execution", "Navigation patterns"]
            automation_opportunities = [
                "Identify repetitive patterns in the workflow",
                "Automate common task sequences",
                "Create workflow templates"
            ]
            recommended_tools = [
                "Screen recording analysis tools",
                "Process mapping software",
                "RPA tools for automation"
            ]
            implementation_difficulty = "medium"
            time_savings = f"{duration // 4} minutes per execution"
            
        elif screenshot_count > 15:
            description = f"Moderate-activity computer workflow with {screenshot_count} interactions"
            steps = [
                "User performed computer tasks",
                "Multiple interactions captured",
                "Workflow with several steps",
                "Review for automation opportunities"
            ]
            repetitive_actions = ["Application usage", "Task execution", "Navigation"]
            automation_opportunities = [
                "Streamline common tasks",
                "Create shortcuts for frequent actions",
                "Automate routine processes"
            ]
            recommended_tools = [
                "Task automation tools",
                "Keyboard shortcuts",
                "Custom scripts"
            ]
            implementation_difficulty = "easy"
            time_savings = f"{duration // 5} minutes per execution"
            
        else:
            description = f"Basic computer activity with {screenshot_count} interactions"
            steps = [
                "User performed basic computer tasks",
                "Limited activity captured",
                "Simple workflow detected",
                "Consider recording longer sessions for better analysis"
            ]
            repetitive_actions = ["Basic computer usage", "Simple interactions"]
            automation_opportunities = [
                "Document common tasks",
                "Create process guides",
                "Identify improvement opportunities"
            ]
            recommended_tools = [
                "Process documentation tools",
                "Manual optimization",
                "Task planning software"
            ]
            implementation_difficulty = "easy"
            time_savings = "Minimal"
        
        return {
            "description": description,
            "workflow_type": "general",
            "complexity": complexity,
            "automation_potential": self._score_to_label(automation_score),
            "automation_score": automation_score,
            "estimated_time": f"{duration // 60} minutes" if duration > 60 else "Less than 1 minute",
            "steps": steps,
            "repetitive_actions": repetitive_actions,
            "automation_opportunities": automation_opportunities,
            "recommended_tools": recommended_tools,
            "implementation_difficulty": implementation_difficulty,
            "time_savings": time_savings
        }
    
    def _score_to_label(self, score: int) -> str:
        """Convert automation score to label."""
        if score >= 90:
            return "very_high"
        elif score >= 70:
            return "high"
        elif score >= 50:
            return "medium"
        elif score >= 30:
            return "low"
        else:
            return "very_low"
    
    def _track_pattern_frequency(self, workflow_type: str, automation_score: int):
        """Track pattern frequency for learning."""
        if workflow_type not in self.frequency_tracker:
            self.frequency_tracker[workflow_type] = {
                'count': 0,
                'total_score': 0,
                'avg_score': 0
            }
        
        tracker = self.frequency_tracker[workflow_type]
        tracker['count'] += 1
        tracker['total_score'] += automation_score
        tracker['avg_score'] = tracker['total_score'] / tracker['count']
        
        logger.info(f"Pattern frequency updated: {workflow_type} (count: {tracker['count']}, avg_score: {tracker['avg_score']:.1f})")
    
    def _generate_fallback_analysis(self) -> Dict[str, Any]:
        """Generate fallback analysis."""
        return {
            "description": "Computer workflow detected",
            "workflow_type": "general",
            "complexity": "moderate",
            "automation_potential": "medium",
            "automation_score": 50,
            "estimated_time": "Unknown",
            "steps": ["Workflow analysis"],
            "repetitive_actions": ["General computer activity"],
            "automation_opportunities": ["Process review and optimization"],
            "recommended_tools": ["Manual analysis", "Process documentation"],
            "implementation_difficulty": "medium",
            "time_savings": "Unknown"
        }
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics."""
        return {
            "total_patterns": len(self.frequency_tracker),
            "most_common": max(self.frequency_tracker.items(), key=lambda x: x[1]['count']) if self.frequency_tracker else None,
            "highest_automation": max(self.frequency_tracker.items(), key=lambda x: x[1]['avg_score']) if self.frequency_tracker else None,
            "patterns": self.frequency_tracker
        }
