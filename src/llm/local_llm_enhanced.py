"""
Enhanced local LLM client for complete offline workflow analysis.
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

from ..error_handling.exceptions import LLMError
from ..error_handling.logger import logger
from ..processing.ocr_analyzer import OCRAnalyzer


class EnhancedLocalLLMClient:
    """Enhanced local LLM client with OCR integration and advanced task detection."""
    
    def __init__(self, config):
        self.config = config
        self.ocr_analyzer = OCRAnalyzer()
        self.task_patterns = self._initialize_task_patterns()
        self.workflow_templates = self._initialize_workflow_templates()
        logger.info("Enhanced Local LLM Client initialized")
    
    def analyze_workflow(self, context: Dict[str, Any]) -> str:
        """Analyze workflow using enhanced local analysis with OCR."""
        try:
            logger.info("Starting enhanced workflow analysis")
            
            # Analyze screenshots with OCR
            screenshot_analyses = []
            if 'screenshots' in context:
                for screenshot in context['screenshots']:
                    if 'path' in screenshot:
                        analysis = self.ocr_analyzer.analyze_screenshot(screenshot['path'])
                        screenshot_analyses.append(analysis)
            
            # Perform comprehensive analysis
            analysis_result = self._perform_comprehensive_analysis(context, screenshot_analyses)
            
            return json.dumps(analysis_result, indent=2)
            
        except Exception as e:
            logger.error(f"Enhanced workflow analysis failed: {e}")
            return self._fallback_analysis(context)
    
    def _perform_comprehensive_analysis(self, context: Dict[str, Any], screenshot_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive workflow analysis."""
        # Extract key information
        duration = context.get('duration', 0)
        screenshot_count = context.get('screenshot_count', 0)
        audio_transcription = context.get('audio_transcription', '')
        
        # Analyze applications used
        applications = self._analyze_applications_used(screenshot_analyses)
        
        # Detect specific tasks
        detected_tasks = self._detect_specific_tasks(screenshot_analyses, context)
        
        # Determine workflow type
        workflow_type = self._determine_workflow_type(applications, detected_tasks, context)
        
        # Calculate complexity and automation potential
        complexity = self._calculate_complexity(screenshot_count, duration, detected_tasks)
        automation_potential = self._calculate_automation_potential(detected_tasks, applications)
        
        # Generate detailed steps
        steps = self._generate_detailed_steps(detected_tasks, applications, context)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(detected_tasks, applications, workflow_type)
        
        # Create comprehensive result
        result = {
            "description": self._generate_description(workflow_type, detected_tasks, applications),
            "workflow_type": workflow_type,
            "complexity": complexity,
            "automation_potential": automation_potential['level'],
            "automation_score": automation_potential['score'],
            "estimated_time": f"{duration // 60} minutes" if duration > 60 else "Less than 1 minute",
            "steps": steps,
            "detected_tasks": detected_tasks,
            "applications_used": applications,
            "repetitive_actions": self._identify_repetitive_actions(detected_tasks),
            "automation_opportunities": recommendations['automation_opportunities'],
            "recommended_tools": recommendations['tools'],
            "implementation_difficulty": recommendations['difficulty'],
            "time_savings": recommendations['time_savings'],
            "detailed_analysis": {
                "ocr_confidence": self._calculate_ocr_confidence(screenshot_analyses),
                "task_breakdown": self._create_task_breakdown(detected_tasks),
                "efficiency_metrics": self._calculate_efficiency_metrics(duration, detected_tasks),
                "learning_opportunities": self._identify_learning_opportunities(detected_tasks)
            }
        }
        
        return result
    
    def _initialize_task_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive task detection patterns."""
        return {
            'excel_operations': {
                'keywords': ['excel', 'spreadsheet', 'workbook', 'worksheet', 'cell', 'formula', 'chart', 'pivot'],
                'ui_elements': ['Microsoft Excel', 'Formula Bar', 'Cell', 'Row', 'Column'],
                'patterns': [r'[A-Z]\d+', r'=.*\(', r'SUM\(', r'AVERAGE\('],
                'weight': 0.9
            },
            'word_operations': {
                'keywords': ['word', 'document', 'text', 'paragraph', 'format', 'style'],
                'ui_elements': ['Microsoft Word', 'Document', 'Page Layout', 'Insert'],
                'patterns': [r'font', r'bold', r'italic', r'underline'],
                'weight': 0.8
            },
            'file_management': {
                'keywords': ['file', 'folder', 'directory', 'save', 'open', 'copy', 'move', 'delete'],
                'ui_elements': ['File Explorer', 'This PC', 'Documents', 'Downloads'],
                'patterns': [r'\.(txt|doc|pdf|xlsx|jpg|png)', r'C:\\', r'D:\\'],
                'weight': 0.7
            },
            'web_browsing': {
                'keywords': ['browser', 'website', 'url', 'search', 'google', 'chrome', 'firefox'],
                'ui_elements': ['Chrome', 'Firefox', 'Edge', 'Address Bar', 'Tab'],
                'patterns': [r'http[s]?://', r'www\.', r'\.com', r'\.org'],
                'weight': 0.6
            },
            'data_entry': {
                'keywords': ['enter', 'input', 'type', 'form', 'field', 'data'],
                'ui_elements': ['Input', 'Field', 'Form', 'Text Box'],
                'patterns': [r'[A-Za-z0-9@._-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'],  # Email pattern
                'weight': 0.8
            },
            'image_editing': {
                'keywords': ['paint', 'image', 'photo', 'edit', 'crop', 'resize'],
                'ui_elements': ['Paint', 'Canvas', 'Brush', 'Color'],
                'patterns': [r'\.(jpg|jpeg|png|gif|bmp)'],
                'weight': 0.7
            },
            'coding_development': {
                'keywords': ['code', 'programming', 'python', 'javascript', 'html', 'css'],
                'ui_elements': ['VS Code', 'Terminal', 'Explorer', 'Code'],
                'patterns': [r'def\s+\w+', r'function\s+\w+', r'class\s+\w+'],
                'weight': 0.9
            },
            'email_communication': {
                'keywords': ['email', 'mail', 'outlook', 'gmail', 'send', 'reply'],
                'ui_elements': ['Outlook', 'Mail', 'Compose', 'Inbox'],
                'patterns': [r'[A-Za-z0-9@._-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'],
                'weight': 0.8
            }
        }
    
    def _initialize_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize workflow templates for different application types."""
        return {
            'excel_workflow': {
                'description': 'Excel spreadsheet operations',
                'common_tasks': ['data_entry', 'formulas', 'formatting', 'charts', 'pivot_tables'],
                'automation_tools': ['Python pandas', 'Excel VBA', 'Power Query', 'OpenPyXL'],
                'complexity_factors': ['formula_complexity', 'data_volume', 'chart_creation']
            },
            'word_workflow': {
                'description': 'Word document processing',
                'common_tasks': ['writing', 'formatting', 'editing', 'reviewing', 'inserting'],
                'automation_tools': ['Python docx', 'Word macros', 'Templates', 'Mail merge'],
                'complexity_factors': ['document_length', 'formatting_complexity', 'collaboration']
            },
            'file_management_workflow': {
                'description': 'File and folder operations',
                'common_tasks': ['organizing', 'copying', 'moving', 'renaming', 'deleting'],
                'automation_tools': ['Python os/pathlib', 'PowerShell', 'Batch scripts', 'Robocopy'],
                'complexity_factors': ['file_count', 'directory_depth', 'file_types']
            },
            'web_browsing_workflow': {
                'description': 'Web browsing and research',
                'common_tasks': ['searching', 'browsing', 'form_filling', 'data_extraction'],
                'automation_tools': ['Selenium WebDriver', 'BeautifulSoup', 'Scrapy', 'Playwright'],
                'complexity_factors': ['site_complexity', 'interaction_count', 'data_extraction']
            }
        }
    
    def _analyze_applications_used(self, screenshot_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze which applications were used during the session."""
        app_usage = {}
        
        for analysis in screenshot_analyses:
            app_name = analysis.get('application', {}).get('name', 'unknown')
            if app_name != 'unknown':
                if app_name not in app_usage:
                    app_usage[app_name] = {
                        'name': app_name,
                        'count': 0,
                        'confidence': 0,
                        'contexts': []
                    }
                
                app_usage[app_name]['count'] += 1
                app_usage[app_name]['confidence'] = max(
                    app_usage[app_name]['confidence'],
                    analysis.get('confidence', 0)
                )
                app_usage[app_name]['contexts'].append(analysis.get('application', {}).get('context', {}))
        
        return list(app_usage.values())
    
    def _detect_specific_tasks(self, screenshot_analyses: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect specific tasks performed during the session."""
        all_tasks = []
        
        for analysis in screenshot_analyses:
            detected_tasks = analysis.get('detected_tasks', [])
            for task in detected_tasks:
                task['timestamp'] = analysis.get('timestamp', 0)
                task['screenshot_confidence'] = analysis.get('confidence', 0)
                all_tasks.append(task)
        
        # Group similar tasks
        grouped_tasks = self._group_similar_tasks(all_tasks)
        
        return grouped_tasks
    
    def _group_similar_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group similar tasks together."""
        grouped = {}
        
        for task in tasks:
            task_name = task['name']
            if task_name not in grouped:
                grouped[task_name] = {
                    'name': task_name,
                    'count': 0,
                    'total_confidence': 0,
                    'contexts': [],
                    'timestamps': []
                }
            
            grouped[task_name]['count'] += 1
            grouped[task_name]['total_confidence'] += task.get('confidence', 0)
            grouped[task_name]['contexts'].extend(task.get('keywords_found', []))
            grouped[task_name]['timestamps'].append(task.get('timestamp', 0))
        
        # Calculate average confidence and clean up
        result = []
        for task_name, data in grouped.items():
            data['average_confidence'] = data['total_confidence'] / data['count']
            data['contexts'] = list(set(data['contexts']))  # Remove duplicates
            data['frequency'] = data['count']
            del data['total_confidence']  # Clean up
            result.append(data)
        
        return result
    
    def _determine_workflow_type(self, applications: List[Dict[str, Any]], tasks: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """Determine the primary workflow type based on applications and tasks."""
        if not applications and not tasks:
            return 'general'
        
        # Score different workflow types
        workflow_scores = {}
        
        # Score based on applications
        for app in applications:
            app_name = app['name']
            if app_name in ['excel']:
                workflow_scores['excel_operations'] = workflow_scores.get('excel_operations', 0) + 3
            elif app_name in ['word']:
                workflow_scores['text_operations'] = workflow_scores.get('text_operations', 0) + 3
            elif app_name in ['file_explorer']:
                workflow_scores['file_operations'] = workflow_scores.get('file_operations', 0) + 3
            elif app_name in ['browser']:
                workflow_scores['browser_operations'] = workflow_scores.get('browser_operations', 0) + 3
        
        # Score based on tasks
        for task in tasks:
            task_name = task['name']
            if 'data_entry' in task_name:
                workflow_scores['data_entry'] = workflow_scores.get('data_entry', 0) + 2
            elif 'file' in task_name:
                workflow_scores['file_operations'] = workflow_scores.get('file_operations', 0) + 2
            elif 'formatting' in task_name:
                workflow_scores['text_operations'] = workflow_scores.get('text_operations', 0) + 2
        
        # Return highest scoring workflow type
        if workflow_scores:
            return max(workflow_scores, key=workflow_scores.get)
        
        return 'general'
    
    def _calculate_complexity(self, screenshot_count: int, duration: int, tasks: List[Dict[str, Any]]) -> str:
        """Calculate workflow complexity."""
        task_count = len(tasks)
        total_frequency = sum(task.get('frequency', 1) for task in tasks)
        
        # Complexity scoring
        score = 0
        score += min(screenshot_count / 10, 5)  # Screenshot complexity
        score += min(duration / 60, 5)  # Duration complexity
        score += min(task_count, 5)  # Task variety
        score += min(total_frequency / 5, 5)  # Repetition complexity
        
        if score >= 15:
            return 'very_complex'
        elif score >= 10:
            return 'complex'
        elif score >= 5:
            return 'moderate'
        else:
            return 'simple'
    
    def _calculate_automation_potential(self, tasks: List[Dict[str, Any]], applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate automation potential and score."""
        score = 0
        factors = []
        
        # Score based on task types
        automation_scores = {
            'data_entry': 0.9,
            'file_management': 0.8,
            'formatting': 0.7,
            'calculation': 0.9,
            'navigation': 0.5,
            'searching': 0.6
        }
        
        for task in tasks:
            task_name = task['name']
            if task_name in automation_scores:
                score += automation_scores[task_name] * task.get('frequency', 1)
                factors.append(f"{task_name}: {automation_scores[task_name]}")
        
        # Score based on applications
        app_scores = {
            'excel': 0.8,
            'word': 0.6,
            'file_explorer': 0.7,
            'browser': 0.5
        }
        
        for app in applications:
            app_name = app['name']
            if app_name in app_scores:
                score += app_scores[app_name] * app.get('count', 1)
                factors.append(f"{app_name}: {app_scores[app_name]}")
        
        # Normalize score
        max_possible_score = len(tasks) * 1.0 + len(applications) * 1.0
        if max_possible_score > 0:
            normalized_score = min((score / max_possible_score) * 100, 100)
        else:
            normalized_score = 50
        
        # Determine level
        if normalized_score >= 80:
            level = 'very_high'
        elif normalized_score >= 60:
            level = 'high'
        elif normalized_score >= 40:
            level = 'medium'
        elif normalized_score >= 20:
            level = 'low'
        else:
            level = 'very_low'
        
        return {
            'score': int(normalized_score),
            'level': level,
            'factors': factors
        }
    
    def _generate_detailed_steps(self, tasks: List[Dict[str, Any]], applications: List[Dict[str, Any]], context: Dict[str, Any]) -> List[str]:
        """Generate detailed workflow steps."""
        steps = []
        
        # Add application-specific steps
        for app in applications:
            app_name = app['name']
            if app_name == 'excel':
                steps.extend([
                    "Open Microsoft Excel application",
                    "Navigate to workbook/worksheet",
                    "Perform data operations (entry, formulas, formatting)",
                    "Save and close workbook"
                ])
            elif app_name == 'word':
                steps.extend([
                    "Open Microsoft Word application",
                    "Create or open document",
                    "Perform text operations (writing, formatting, editing)",
                    "Save and close document"
                ])
            elif app_name == 'file_explorer':
                steps.extend([
                    "Open File Explorer",
                    "Navigate to target directory",
                    "Perform file operations (copy, move, rename, delete)",
                    "Organize files and folders"
                ])
        
        # Add task-specific steps
        for task in tasks:
            task_name = task['name']
            if task_name == 'data_entry':
                steps.append("Enter data into forms or fields")
            elif task_name == 'file_management':
                steps.append("Manage files and folders")
            elif task_name == 'formatting':
                steps.append("Apply formatting to content")
            elif task_name == 'calculation':
                steps.append("Perform calculations and formulas")
        
        # Remove duplicates and return
        return list(dict.fromkeys(steps))
    
    def _generate_recommendations(self, tasks: List[Dict[str, Any]], applications: List[Dict[str, Any]], workflow_type: str) -> Dict[str, Any]:
        """Generate automation recommendations."""
        recommendations = {
            'automation_opportunities': [],
            'tools': [],
            'difficulty': 'medium',
            'time_savings': 'Unknown'
        }
        
        # Application-specific recommendations
        for app in applications:
            app_name = app['name']
            if app_name == 'excel':
                recommendations['automation_opportunities'].extend([
                    "Automate data entry with Python pandas",
                    "Create Excel macros for repetitive tasks",
                    "Use Power Query for data transformation"
                ])
                recommendations['tools'].extend(['Python pandas', 'Excel VBA', 'Power Query'])
            elif app_name == 'word':
                recommendations['automation_opportunities'].extend([
                    "Create document templates",
                    "Use mail merge for bulk documents",
                    "Automate formatting with styles"
                ])
                recommendations['tools'].extend(['Word templates', 'Mail merge', 'Python docx'])
            elif app_name == 'file_explorer':
                recommendations['automation_opportunities'].extend([
                    "Automate file organization",
                    "Batch rename files",
                    "Automate file copying and moving"
                ])
                recommendations['tools'].extend(['PowerShell scripts', 'Python os/pathlib', 'Batch files'])
        
        # Task-specific recommendations
        for task in tasks:
            task_name = task['name']
            if task_name == 'data_entry':
                recommendations['automation_opportunities'].append("Implement form automation")
                recommendations['tools'].append('Selenium WebDriver')
            elif task_name == 'calculation':
                recommendations['automation_opportunities'].append("Create calculation scripts")
                recommendations['tools'].append('Python numpy/pandas')
        
        # Remove duplicates
        recommendations['automation_opportunities'] = list(set(recommendations['automation_opportunities']))
        recommendations['tools'] = list(set(recommendations['tools']))
        
        # Determine difficulty
        if len(recommendations['tools']) > 3:
            recommendations['difficulty'] = 'hard'
        elif len(recommendations['tools']) > 1:
            recommendations['difficulty'] = 'medium'
        else:
            recommendations['difficulty'] = 'easy'
        
        return recommendations
    
    def _generate_description(self, workflow_type: str, tasks: List[Dict[str, Any]], applications: List[Dict[str, Any]]) -> str:
        """Generate a descriptive summary of the workflow."""
        app_names = [app['name'] for app in applications]
        task_names = [task['name'] for task in tasks]
        
        if app_names:
            primary_app = app_names[0]
            if primary_app == 'excel':
                return f"Excel spreadsheet workflow involving {', '.join(task_names)}"
            elif primary_app == 'word':
                return f"Word document workflow involving {', '.join(task_names)}"
            elif primary_app == 'file_explorer':
                return f"File management workflow involving {', '.join(task_names)}"
            else:
                return f"Computer workflow using {primary_app} involving {', '.join(task_names)}"
        else:
            return f"General computer workflow involving {', '.join(task_names)}"
    
    def _identify_repetitive_actions(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Identify repetitive actions from detected tasks."""
        repetitive = []
        
        for task in tasks:
            if task.get('frequency', 1) > 1:
                repetitive.append(f"{task['name']} (repeated {task['frequency']} times)")
        
        return repetitive
    
    def _calculate_ocr_confidence(self, screenshot_analyses: List[Dict[str, Any]]) -> float:
        """Calculate overall OCR confidence."""
        if not screenshot_analyses:
            return 0.0
        
        total_confidence = sum(analysis.get('confidence', 0) for analysis in screenshot_analyses)
        return total_confidence / len(screenshot_analyses)
    
    def _create_task_breakdown(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create detailed task breakdown."""
        breakdown = {
            'total_tasks': len(tasks),
            'task_frequency': sum(task.get('frequency', 1) for task in tasks),
            'high_confidence_tasks': [task for task in tasks if task.get('average_confidence', 0) > 0.7],
            'repetitive_tasks': [task for task in tasks if task.get('frequency', 1) > 1]
        }
        return breakdown
    
    def _calculate_efficiency_metrics(self, duration: int, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate efficiency metrics."""
        task_count = len(tasks)
        total_frequency = sum(task.get('frequency', 1) for task in tasks)
        
        return {
            'tasks_per_minute': task_count / (duration / 60) if duration > 0 else 0,
            'actions_per_minute': total_frequency / (duration / 60) if duration > 0 else 0,
            'average_task_duration': duration / task_count if task_count > 0 else 0
        }
    
    def _identify_learning_opportunities(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Identify learning opportunities from the workflow."""
        opportunities = []
        
        for task in tasks:
            if task.get('average_confidence', 0) < 0.5:
                opportunities.append(f"Improve {task['name']} detection accuracy")
        
        if len(tasks) > 5:
            opportunities.append("Consider breaking down complex workflows")
        
        return opportunities
    
    def _fallback_analysis(self, context: Dict[str, Any]) -> str:
        """Fallback analysis when enhanced analysis fails."""
        return json.dumps({
            "description": "Computer workflow detected",
            "workflow_type": "general",
            "complexity": "moderate",
            "automation_potential": "medium",
            "automation_score": 50,
            "estimated_time": "Unknown",
            "steps": ["Workflow analysis"],
            "detected_tasks": [],
            "applications_used": [],
            "repetitive_actions": ["General computer activity"],
            "automation_opportunities": ["Process review and optimization"],
            "recommended_tools": ["Manual analysis", "Process documentation"],
            "implementation_difficulty": "medium",
            "time_savings": "Unknown"
        }, indent=2)


# Compatibility wrapper
class LocalLLMClient:
    """Compatibility wrapper for enhanced local LLM."""
    
    def __init__(self, config):
        self.client = EnhancedLocalLLMClient(config)
        self.config = config
        logger.info("Local LLM Client initialized (using Enhanced Local LLM)")
    
    def analyze_workflow(self, context: Dict[str, Any]) -> str:
        """Analyze workflow using enhanced local LLM."""
        try:
            return self.client.analyze_workflow(context)
        except Exception as e:
            logger.error(f"Error in enhanced workflow analysis: {e}")
            return self.client._fallback_analysis(context)
