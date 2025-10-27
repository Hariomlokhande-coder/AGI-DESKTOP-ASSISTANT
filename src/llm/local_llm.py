"""Local LLM client for offline workflow analysis."""

import json
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..error_handling.exceptions import LLMError, ProcessingError
from ..error_handling.logger import logger


class LocalLLMClient:
    """Enhanced local LLM client with comprehensive error handling and pattern-based analysis."""
    
    def __init__(self, config):
        self.config = config
        self.timeout = config.get('llm.timeout_seconds', 30)
        self.max_retries = config.get('llm.max_retries', 3)
        self.retry_delay = config.get('llm.retry_delay_seconds', 1)
        
        # Load patterns and heuristics for local analysis
        self.patterns = self._load_patterns()
        self.heuristics = self._load_heuristics()
        
        logger.info("LocalLLMClient initialized successfully")
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load workflow patterns for analysis."""
        try:
            patterns_file = Path("config/patterns.json")
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns = json.load(f)
                logger.info(f"Loaded {len(patterns)} workflow patterns")
                return patterns
            else:
                logger.warning("Patterns file not found, using default patterns")
                return self._get_default_patterns()
        except Exception as e:
            logger.error(f"Error loading patterns: {e}")
            return self._get_default_patterns()
    
    def _get_default_patterns(self) -> Dict[str, Any]:
        """Get default workflow patterns."""
        return {
            'file_operations': [
                'create', 'read', 'write', 'delete', 'copy', 'move', 'save', 'edit'
            ],
            'text_operations': [
                'type', 'edit', 'format', 'copy', 'paste', 'cut', 'select'
            ],
            'navigation': [
                'click', 'scroll', 'switch', 'open', 'close', 'navigate', 'search'
            ],
            'browser_operations': [
                'load', 'refresh', 'navigate', 'search', 'bookmark', 'download'
            ],
            'development_tasks': [
                'code', 'debug', 'test', 'compile', 'deploy', 'commit'
            ],
            'communication': [
                'email', 'message', 'chat', 'call', 'send', 'receive'
            ],
            'multimedia': [
                'play', 'record', 'edit', 'upload', 'download', 'stream'
            ],
            'data_analysis': [
                'analyze', 'process', 'filter', 'sort', 'query', 'report'
            ]
        }
    
    def _load_heuristics(self) -> Dict[str, Any]:
        """Load analysis heuristics."""
        return {
            'complexity_levels': {
                'simple': {'steps': 1, 'automation': 'high'},
                'moderate': {'steps': 3, 'automation': 'medium'},
                'complex': {'steps': 5, 'automation': 'low'},
                'very_complex': {'steps': 10, 'automation': 'very_low'}
            },
            'automation_potential': {
                'very_high': 90,
                'high': 70,
                'medium': 50,
                'low': 30,
                'very_low': 10
            }
        }
    
    def analyze_text(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Analyze text using pattern matching and heuristics."""
        try:
            if not text or len(text.strip()) < 10:
                return self._generate_simple_analysis(text)
            
            # Extract keywords and patterns
            keywords = self._extract_keywords(text)
            patterns_found = self._match_patterns(keywords)
            
            # Determine complexity
            complexity = self._assess_complexity(keywords, patterns_found)
            
            # Generate analysis
            analysis = self._generate_analysis(text, keywords, patterns_found, complexity, context)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in local text analysis: {e}")
            return self._generate_fallback_analysis(text)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        try:
            # Simple keyword extraction
            words = text.lower().split()
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could'}
            
            keywords = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Remove duplicates
            return list(set(keywords))
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def _match_patterns(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Match keywords to workflow patterns."""
        try:
            matches = {}
            
            for category, patterns in self.patterns.items():
                matches[category] = []
                for keyword in keywords:
                    for pattern in patterns:
                        if pattern in keyword or keyword in pattern:
                            matches[category].append(keyword)
                            break
            
            return matches
            
        except Exception as e:
            logger.error(f"Error matching patterns: {e}")
            return {}
    
    def _assess_complexity(self, keywords: List[str], patterns: Dict[str, List[str]]) -> str:
        """Assess workflow complexity."""
        try:
            # Count unique categories with matches
            matching_categories = [cat for cat, matches in patterns.items() if matches]
            num_categories = len(matching_categories)
            
            # Assess complexity
            if num_categories == 0:
                return 'simple'
            elif num_categories <= 2:
                return 'moderate'
            elif num_categories <= 4:
                return 'complex'
            else:
                return 'very_complex'
                
        except Exception as e:
            logger.error(f"Error assessing complexity: {e}")
            return 'moderate'
    
    def _generate_analysis(self, text: str, keywords: List[str], patterns: Dict[str, List[str]], 
                          complexity: str, context: Optional[Dict[str, Any]]) -> str:
        """Generate workflow analysis."""
        try:
            # Identify primary workflow type
            primary_categories = []
            for category, matches in patterns.items():
                if matches:
                    primary_categories.append(category)
            
            workflow_type = primary_categories[0] if primary_categories else 'general'
            
            # Determine automation potential
            automation_score = self._calculate_automation_score(keywords, patterns, complexity)
            
            # Generate description
            description = self._generate_description(text, keywords, workflow_type, complexity)
            
            # Generate steps
            steps = self._generate_steps(text, keywords, patterns, complexity)
            
            # Compile analysis
            analysis = {
                'description': description,
                'workflow_type': workflow_type,
                'complexity': complexity,
                'automation_potential': self._automation_score_to_label(automation_score),
                'automation_score': automation_score,
                'key_activities': keywords[:10],
                'steps': steps,
                'estimated_time': self._estimate_time(complexity, len(steps)),
                'recommendations': self._generate_recommendations(workflow_type, complexity, automation_score)
            }
            
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return self._generate_fallback_analysis(text)
    
    def _calculate_automation_score(self, keywords: List[str], patterns: Dict[str, List[str]], 
                                    complexity: str) -> int:
        """Calculate automation potential score."""
        try:
            score = 50  # Default medium score
            
            # Adjust based on complexity
            complexity_scores = {
                'simple': 20,
                'moderate': 0,
                'complex': -15,
                'very_complex': -30
            }
            score += complexity_scores.get(complexity, 0)
            
            # Adjust based on detected patterns
            repetitive_patterns = ['file_operations', 'text_operations']
            for category in repetitive_patterns:
                if category in patterns and patterns[category]:
                    score += 10
            
            # Bounds check
            return max(10, min(90, score))
            
        except Exception as e:
            logger.error(f"Error calculating automation score: {e}")
            return 50
    
    def _automation_score_to_label(self, score: int) -> str:
        """Convert automation score to label."""
        if score >= 80:
            return 'very_high'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        elif score >= 20:
            return 'low'
        else:
            return 'very_low'
    
    def _generate_description(self, text: str, keywords: List[str], workflow_type: str, 
                             complexity: str) -> str:
        """Generate workflow description."""
        try:
            # Basic description based on workflow type
            descriptions = {
                'file_operations': f"{complexity.capitalize()} file management workflow",
                'text_operations': f"{complexity.capitalize()} text editing and processing workflow",
                'navigation': f"{complexity.capitalize()} interface navigation and interaction workflow",
                'browser_operations': f"{complexity.capitalize()} web browsing and content workflow",
                'development_tasks': f"{complexity.capitalize()} software development workflow",
                'communication': f"{complexity.capitalize()} communication and messaging workflow",
                'multimedia': f"{complexity.capitalize()} media content workflow",
                'data_analysis': f"{complexity.capitalize()} data processing and analysis workflow",
                'general': f"{complexity.capitalize()} general computer workflow"
            }
            
            return descriptions.get(workflow_type, descriptions['general'])
            
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return f"{complexity.capitalize()} computer workflow detected"
    
    def _generate_steps(self, text: str, keywords: List[str], patterns: Dict[str, List[str]], 
                       complexity: str) -> List[str]:
        """Generate workflow steps."""
        try:
            steps = []
            
            # Extract key actions from keywords
            key_actions = []
            for category, matches in patterns.items():
                for match in matches[:3]:  # Top 3 from each category
                    key_actions.append(match)
            
            # If no patterns found, use keywords
            if not key_actions:
                key_actions = keywords[:5]
            
            # Generate steps
            for i, action in enumerate(key_actions, 1):
                steps.append(f"Step {i}: Perform {action} operation")
            
            # Ensure at least some steps
            if not steps:
                steps = [
                    "Step 1: Analyze system state",
                    "Step 2: Perform required operations",
                    "Step 3: Verify results"
                ]
            
            return steps[:10]  # Limit to 10 steps
            
        except Exception as e:
            logger.error(f"Error generating steps: {e}")
            return ["Workflow analysis in progress"]
    
    def _estimate_time(self, complexity: str, num_steps: int) -> str:
        """Estimate workflow time."""
        base_time = {
            'simple': 5,
            'moderate': 15,
            'complex': 30,
            'very_complex': 60
        }
        
        minutes = base_time.get(complexity, 15) + (num_steps * 2)
        return f"{minutes} minutes"
    
    def _generate_recommendations(self, workflow_type: str, complexity: str, 
                                  automation_score: int) -> List[str]:
        """Generate workflow recommendations."""
        recommendations = []
        
        # Automation recommendations
        if automation_score >= 70:
            recommendations.append("This workflow has high automation potential - consider scripting")
        elif automation_score >= 50:
            recommendations.append("This workflow has moderate automation potential - consider partial automation")
        else:
            recommendations.append("This workflow has low automation potential - manual execution may be optimal")
        
        # Complexity recommendations
        if complexity == 'very_complex':
            recommendations.append("Consider breaking this workflow into smaller sub-workflows")
        elif complexity in ['complex', 'moderate']:
            recommendations.append("Document this workflow for future reference")
        
        # Workflow-specific recommendations
        if workflow_type == 'file_operations':
            recommendations.append("Consider using batch operations or scripts for efficiency")
        elif workflow_type == 'text_operations':
            recommendations.append("Consider using templates or macros")
        
        return recommendations
    
    def _generate_simple_analysis(self, text: str) -> str:
        """Generate simple analysis for short text."""
        return json.dumps({
            'description': 'Basic computer activity detected',
            'workflow_type': 'general',
            'complexity': 'simple',
            'automation_potential': 'medium',
            'automation_score': 50,
            'steps': ['General computer activity'],
            'estimated_time': '5 minutes',
            'recommendations': ['Continue monitoring for patterns']
        }, indent=2)
    
    def _generate_fallback_analysis(self, text: str) -> str:
        """Generate fallback analysis on error."""
        return json.dumps({
            'description': 'Workflow detected but analysis incomplete',
            'workflow_type': 'general',
            'complexity': 'moderate',
            'automation_potential': 'medium',
            'automation_score': 50,
            'steps': ['Workflow step analysis'],
            'estimated_time': 'Unknown',
            'recommendations': ['Review workflow manually']
        }, indent=2)


# Compatibility wrapper for existing code
class LLMClient:
    """Compatibility wrapper that uses LocalLLMClient."""
    
    def __init__(self, config):
        self.client = LocalLLMClient(config)
        self.config = config
        logger.info("LLM Client initialized (using LocalLLM)")
    
    def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using local analysis."""
        try:
            # Use local analysis instead of API call
            return self.client.analyze_text(prompt)
        except Exception as e:
            logger.error(f"Error in LLM content generation: {e}")
            raise LLMError(f"Failed to generate content: {e}")
    
    def analyze_workflow(self, data: Dict[str, Any]) -> str:
        """Analyze workflow using local patterns."""
        try:
            # Convert workflow data to text for analysis
            text = self._format_workflow_data(data)
            return self.client.analyze_text(text, context=data)
        except Exception as e:
            logger.error(f"Error in workflow analysis: {e}")
            return self.client._generate_fallback_analysis(str(data))
    
    def _format_workflow_data(self, data: Dict[str, Any]) -> str:
        """Format workflow data as text."""
        try:
            text_parts = []
            
            if 'description' in data:
                text_parts.append(data['description'])
            
            if 'steps' in data:
                text_parts.append("Steps: " + ", ".join(str(step) for step in data['steps']))
            
            if 'screenshots' in data:
                text_parts.append(f"Screenshots: {len(data['screenshots'])}")
            
            if 'audio' in data:
                audio = data['audio']
                if 'transcription' in audio:
                    text_parts.append(audio['transcription'])
            
            return " ".join(text_parts)
            
        except Exception as e:
            logger.error(f"Error formatting workflow data: {e}")
            return str(data)
