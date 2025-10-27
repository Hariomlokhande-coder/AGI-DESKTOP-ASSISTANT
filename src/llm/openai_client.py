"""OpenAI API client for LLM integration."""
import openai
from ..error_handling.exceptions import LLMError
from ..error_handling.logger import logger


class OpenAIClient:
    """Client for OpenAI API."""
    
    def __init__(self, config):
        self.config = config
        self.api_key = config.get_api_key('openai')
        self.model_name = config.get('llm.model', 'gpt-3.5-turbo')
        self.temperature = config.get('llm.temperature', 0.3)
        self.max_tokens = config.get('llm.max_tokens', 2000)
        
        if not self.api_key:
            logger.warning("OpenAI API key not found")
            self.client = None
        else:
            try:
                openai.api_key = self.api_key
                self.client = openai
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
    
    def analyze_workflow(self, context):
        """Analyze workflow from context data."""
        if not self.client:
            logger.warning("OpenAI client not available, using fallback")
            return self._fallback_analysis(context)
        
        try:
            prompt = self._build_workflow_prompt(context)
            response = self.client.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            workflows = self._parse_workflow_response(response.choices[0].message.content)
            logger.info(f"Detected {len(workflows)} workflows")
            return workflows
        except Exception as e:
            logger.error(f"Error analyzing workflow with OpenAI: {e}")
            return self._fallback_analysis(context)
    
    def _build_workflow_prompt(self, context):
        """Build prompt for workflow analysis."""
        prompt = f"""You are an AI assistant analyzing user computer activity to identify repetitive, automatable workflows.

Given the following context from a user's recording session:

Session Duration: {context.get('duration', 0)} seconds
Screenshots captured: {context.get('screenshot_count', 0)}
Audio transcription: {context.get('audio_transcription', 'N/A')}

Based on this information, identify any repetitive workflows or patterns that could be automated.

For each workflow, provide:
1. A clear description of the workflow
2. The steps involved
3. Automation potential (High/Medium/Low)

Format your response as a list of workflows. Be specific and practical.
"""
        return prompt
    
    def _parse_workflow_response(self, response_text):
        """Parse LLM response into structured workflows."""
        workflows = []
        
        # Simple parsing - split by lines and look for numbered items
        lines = response_text.split('\n')
        current_workflow = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for workflow indicators
            if any(indicator in line.lower() for indicator in ['workflow', 'task', 'pattern']):
                if current_workflow:
                    workflows.append(current_workflow)
                current_workflow = {
                    'description': line,
                    'steps': [],
                    'automation_potential': 'Medium'
                }
            elif current_workflow and (line.startswith('-') or line.startswith('•') or any(char.isdigit() for char in line[:3])):
                current_workflow['steps'].append(line.lstrip('- •0123456789.'))
        
        if current_workflow:
            workflows.append(current_workflow)
        
        return workflows if workflows else self._get_default_workflows()
    
    def _fallback_analysis(self, context):
        """Fallback analysis when API is not available."""
        logger.info("Using fallback workflow analysis")
        return self._get_default_workflows()
    
    def _get_default_workflows(self):
        """Get default workflow suggestions."""
        return [
            {
                'description': 'File Management Workflow',
                'steps': [
                    'Opening files from specific folders',
                    'Organizing documents',
                    'Moving files between directories'
                ],
                'automation_potential': 'High'
            },
            {
                'description': 'Data Entry Workflow',
                'steps': [
                    'Opening spreadsheet application',
                    'Entering repetitive data',
                    'Saving and formatting'
                ],
                'automation_potential': 'High'
            }
        ]
