"""External LLM client for workflow analysis using OpenAI API."""

import json
import time
import logging
from typing import Dict, List, Any, Optional
import requests
import os

from ..error_handling.exceptions import LLMError
from ..error_handling.logger import logger


class ExternalLLMClient:
    """External LLM client with OpenAI API integration."""
    
    def __init__(self, config):
        self.config = config
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 2000
        self.temperature = 0.3
        
        if not self.api_key:
            logger.warning("No OpenAI API key found. Using fallback analysis.")
            self.api_key = None
    
    def analyze_workflow(self, context: Dict[str, Any]) -> str:
        """Analyze workflow using external LLM."""
        try:
            if not self.api_key:
                return self._fallback_analysis(context)
            
            # Prepare prompt
            prompt = self._create_analysis_prompt(context)
            
            # Call OpenAI API
            response = self._call_openai_api(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"External LLM analysis failed: {e}")
            return self._fallback_analysis(context)
    
    def _create_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create focused analysis prompt for LLM."""
        prompt = f"""
You are an expert workflow analyst. Analyze this desktop session for automation opportunities:

SESSION SUMMARY:
- Duration: {context.get('duration', 0)} seconds
- Screenshots: {context.get('screenshot_count', 0)}
- Audio: {context.get('audio_transcription', 'No audio')}

ANALYSIS REQUIREMENTS:
1. Identify the MAIN workflow category from: file_operations, text_operations, data_entry, navigation, browser_operations, development_tasks, communication, multimedia, data_analysis, or general
2. Assess complexity: simple (1-3 steps), moderate (4-6 steps), complex (7-10 steps), very_complex (10+ steps)
3. Calculate automation potential score (0-100) based on:
   - Repetitive actions (high score)
   - Predictable patterns (high score)
   - Manual data entry (high score)
   - Complex decision-making (low score)
4. Estimate manual completion time
5. Extract key workflow steps
6. Provide specific automation recommendations

FOCUS ON:
- Repetitive actions that can be automated
- Data entry tasks
- File operations
- Navigation patterns
- Time-consuming manual processes

Respond in JSON format:
{{
    "description": "Clear description of the main workflow",
    "workflow_type": "primary_category",
    "complexity": "simple|moderate|complex|very_complex",
    "automation_potential": "very_high|high|medium|low|very_low",
    "automation_score": 85,
    "estimated_time": "X minutes",
    "steps": ["Specific step 1", "Specific step 2", "Specific step 3"],
    "repetitive_actions": ["Action that repeats", "Another repetitive action"],
    "automation_opportunities": ["Specific automation opportunity 1", "Specific automation opportunity 2"],
    "recommended_tools": ["Tool 1", "Tool 2", "Tool 3"],
    "implementation_difficulty": "easy|medium|hard",
    "time_savings": "X minutes per execution"
}}
"""
        return prompt
    
    def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert workflow analyst. Analyze computer workflows and provide automation recommendations."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return content
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                raise LLMError(f"API request failed: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error("OpenAI API timeout")
            raise LLMError("API request timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API request error: {e}")
            raise LLMError(f"API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI API: {e}")
            raise LLMError(f"API call failed: {e}")
    
    def _fallback_analysis(self, context: Dict[str, Any]) -> str:
        """Enhanced fallback analysis with pattern recognition."""
        try:
            screenshot_count = context.get('screenshot_count', 0)
            duration = context.get('duration', 0)
            
            # Enhanced analysis based on activity patterns
            if screenshot_count > 30:
                complexity = "very_complex"
                automation_potential = "very_high"
                automation_score = 85
                workflow_type = "data_entry"
                description = f"Complex data processing workflow with {screenshot_count} interactions"
            elif screenshot_count > 20:
                complexity = "complex"
                automation_potential = "high"
                automation_score = 75
                workflow_type = "file_operations"
                description = f"File management workflow with {screenshot_count} operations"
            elif screenshot_count > 10:
                complexity = "moderate"
                automation_potential = "medium"
                automation_score = 60
                workflow_type = "text_operations"
                description = f"Text processing workflow with {screenshot_count} interactions"
            else:
                complexity = "simple"
                automation_potential = "low"
                automation_score = 30
                workflow_type = "navigation"
                description = f"Basic navigation workflow with {screenshot_count} screenshots"
            
            # Generate specific steps based on workflow type
            if workflow_type == "data_entry":
                steps = [
                    "Open data source application",
                    "Navigate to data entry form",
                    "Enter data fields systematically",
                    "Validate and save entries",
                    "Repeat for multiple records"
                ]
                repetitive_actions = ["Data field entry", "Form navigation", "Save operations"]
                automation_opportunities = ["Automated data entry", "Form filling scripts", "Data validation"]
                recommended_tools = ["Python pandas", "Selenium WebDriver", "Excel VBA macros"]
                implementation_difficulty = "medium"
                time_savings = f"{duration // 2} minutes per batch"
                
            elif workflow_type == "file_operations":
                steps = [
                    "Navigate to source directory",
                    "Select files for processing",
                    "Apply operations (copy, move, rename)",
                    "Organize processed files",
                    "Verify completion"
                ]
                repetitive_actions = ["File selection", "Directory navigation", "File operations"]
                automation_opportunities = ["Batch file processing", "Automated organization", "File renaming scripts"]
                recommended_tools = ["Python os/pathlib", "PowerShell scripts", "Batch files"]
                implementation_difficulty = "easy"
                time_savings = f"{duration // 3} minutes per batch"
                
            elif workflow_type == "text_operations":
                steps = [
                    "Open text editor/application",
                    "Navigate to content area",
                    "Enter or edit text content",
                    "Format text as needed",
                    "Save document"
                ]
                repetitive_actions = ["Text entry", "Formatting", "Save operations"]
                automation_opportunities = ["Text templates", "Auto-formatting", "Content generation"]
                recommended_tools = ["Python text processing", "Word macros", "Text templates"]
                implementation_difficulty = "easy"
                time_savings = f"{duration // 4} minutes per document"
                
            else:  # navigation or general
                steps = [
                    "Navigate between applications",
                    "Perform various interactions",
                    "Complete workflow tasks",
                    "Verify results"
                ]
                repetitive_actions = ["Application switching", "Navigation patterns"]
                automation_opportunities = ["Workflow automation", "Process optimization"]
                recommended_tools = ["Custom scripts", "RPA tools", "Workflow automation"]
                implementation_difficulty = "hard"
                time_savings = f"{duration // 5} minutes per execution"
            
            result = {
                "description": description,
                "workflow_type": workflow_type,
                "complexity": complexity,
                "automation_potential": automation_potential,
                "automation_score": automation_score,
                "estimated_time": f"{duration // 60} minutes" if duration > 60 else "Less than 1 minute",
                "steps": steps,
                "repetitive_actions": repetitive_actions,
                "automation_opportunities": automation_opportunities,
                "recommended_tools": recommended_tools,
                "implementation_difficulty": implementation_difficulty,
                "time_savings": time_savings
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Fallback analysis error: {e}")
            return json.dumps({
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
            }, indent=2)


# Compatibility wrapper
class LLMClient:
    """Compatibility wrapper for external LLM."""
    
    def __init__(self, config):
        self.client = ExternalLLMClient(config)
        self.config = config
        logger.info("LLM Client initialized (using External LLM)")
    
    def analyze_workflow(self, context: Dict[str, Any]) -> str:
        """Analyze workflow using external LLM."""
        try:
            return self.client.analyze_workflow(context)
        except Exception as e:
            logger.error(f"Error in workflow analysis: {e}")
            return self.client._fallback_analysis(context)
