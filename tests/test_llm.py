"""Test cases for LLM functionality."""
import unittest
import os
from unittest.mock import Mock, patch
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from llm.gemini_client import GeminiClient
from llm.workflow_analyzer import WorkflowAnalyzer
from llm.model_adapter import ModelAdapter


class TestGeminiClient(unittest.TestCase):
    """Test Gemini client functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock()
        self.config.get_api_key.return_value = "test_api_key"
        self.config.get.side_effect = lambda key, default=None: {
            'llm.model': 'gemini-2.0-flash-exp',
            'llm.temperature': 0.3,
            'llm.max_tokens': 2000
        }.get(key, default)
    
    @patch('llm.gemini_client.genai')
    def test_initialization_with_api_key(self, mock_genai):
        """Test client initialization with API key."""
        client = GeminiClient(self.config)
        
        self.assertIsNotNone(client.client)
        mock_genai.configure.assert_called_once_with(api_key="test_api_key")
        mock_genai.GenerativeModel.assert_called_once_with('gemini-2.0-flash-exp')
    
    def test_initialization_without_api_key(self):
        """Test client initialization without API key."""
        self.config.get_api_key.return_value = ""
        
        client = GeminiClient(self.config)
        
        self.assertIsNone(client.client)
    
    def test_fallback_analysis(self):
        """Test fallback analysis when API is not available."""
        self.config.get_api_key.return_value = ""
        client = GeminiClient(self.config)
        
        context = {'duration': 300, 'screenshot_count': 10}
        workflows = client._fallback_analysis(context)
        
        self.assertIsInstance(workflows, list)
        self.assertGreater(len(workflows), 0)
    
    def test_get_default_workflows(self):
        """Test default workflow generation."""
        self.config.get_api_key.return_value = ""
        client = GeminiClient(self.config)
        
        workflows = client._get_default_workflows()
        
        self.assertIsInstance(workflows, list)
        self.assertEqual(len(workflows), 2)
        
        # Check workflow structure
        for workflow in workflows:
            self.assertIn('description', workflow)
            self.assertIn('steps', workflow)
            self.assertIn('automation_potential', workflow)


class TestWorkflowAnalyzer(unittest.TestCase):
    """Test workflow analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock()
        self.analyzer = WorkflowAnalyzer(self.config)
    
    @patch.object(WorkflowAnalyzer, '__init__', lambda self, config: None)
    def test_detect_patterns(self):
        """Test pattern detection."""
        analyzer = WorkflowAnalyzer(None)
        
        screenshots = [{'path': f'/tmp/shot{i}.png'} for i in range(10)]
        patterns = analyzer.detect_patterns(screenshots)
        
        self.assertIsInstance(patterns, list)
        if len(screenshots) > 5:
            self.assertGreater(len(patterns), 0)
    
    @patch.object(WorkflowAnalyzer, '__init__', lambda self, config: None)
    def test_generate_workflow_recommendations(self):
        """Test workflow recommendation generation."""
        analyzer = WorkflowAnalyzer(None)
        
        workflows = [
            {
                'description': 'File management workflow',
                'automation_potential': 'High',
                'steps': ['Open file', 'Edit file', 'Save file']
            }
        ]
        
        recommendations = analyzer.generate_workflow_recommendations(workflows)
        
        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), 1)
        
        rec = recommendations[0]
        self.assertEqual(rec['workflow'], 'File management workflow')
        self.assertEqual(rec['automation_potential'], 'High')
        self.assertIn('recommended_tools', rec)


class TestModelAdapter(unittest.TestCase):
    """Test model adaptation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.storage = Mock()
        self.storage.get_processed_file_path.return_value = "/tmp/patterns.json"
        self.adapter = ModelAdapter(self.storage)
    
    @patch.object(ModelAdapter, '__init__', lambda self, storage: None)
    def test_is_similar_workflow(self):
        """Test workflow similarity detection."""
        adapter = ModelAdapter(None)
        
        workflow1 = {'description': 'File management task'}
        workflow2 = {'description': 'File organization workflow'}
        
        result = adapter._is_similar_workflow(workflow1, workflow2)
        self.assertTrue(result)
        
        workflow3 = {'description': 'Web browsing activity'}
        result = adapter._is_similar_workflow(workflow1, workflow3)
        self.assertFalse(result)
    
    @patch.object(ModelAdapter, '__init__', lambda self, storage: None)
    def test_get_top_workflows(self):
        """Test getting top workflows."""
        adapter = ModelAdapter(None)
        adapter.patterns = {
            'workflows': [
                {'description': 'Workflow A', 'count': 5},
                {'description': 'Workflow B', 'count': 10},
                {'description': 'Workflow C', 'count': 3}
            ]
        }
        
        top_workflows = adapter.get_top_workflows(2)
        
        self.assertEqual(len(top_workflows), 2)
        self.assertEqual(top_workflows[0]['description'], 'Workflow B')
        self.assertEqual(top_workflows[1]['description'], 'Workflow A')


if __name__ == '__main__':
    unittest.main()
