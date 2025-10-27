"""Test cases for storage functionality."""
import unittest
import os
import tempfile
from unittest.mock import Mock, patch
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from storage.config import Config
from storage.local_storage import LocalStorage
from storage.session_manager import SessionManager


class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_path = "/tmp/test_config.yaml"
    
    def test_default_config(self):
        """Test default configuration loading."""
        config = Config("/nonexistent/config.yaml")
        
        # Test some default values
        self.assertEqual(config.get('recording.max_duration_minutes'), 60)
        self.assertEqual(config.get('recording.fps'), 1)
        self.assertEqual(config.get('storage.max_storage_gb'), 5)
    
    def test_get_api_key(self):
        """Test API key retrieval."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            config = Config("/nonexistent/config.yaml")
            api_key = config.get_api_key('gemini')
            self.assertEqual(api_key, 'test_key')
    
    def test_get_nested_config(self):
        """Test nested configuration access."""
        config = Config("/nonexistent/config.yaml")
        
        # Test nested access
        fps = config.get('recording.fps')
        self.assertEqual(fps, 1)
        
        # Test non-existent key
        non_existent = config.get('non.existent.key', 'default')
        self.assertEqual(non_existent, 'default')


class TestLocalStorage(unittest.TestCase):
    """Test local storage functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock()
        self.config.get.side_effect = lambda key, default=None: {
            'storage.local_path': './test_data',
            'storage.temp_path': './test_data/temp',
            'storage.recordings_path': './test_data/recordings',
            'storage.processed_path': './test_data/processed',
            'storage.max_storage_gb': 5
        }.get(key, default)
    
    @patch('storage.local_storage.ensure_directory')
    def test_initialization(self, mock_ensure_dir):
        """Test storage initialization."""
        storage = LocalStorage(self.config)
        
        self.assertEqual(storage.base_path, './test_data')
        self.assertEqual(storage.temp_path, './test_data/temp')
        self.assertEqual(storage.max_storage_gb, 5)
        
        # Should call ensure_directory for all paths
        self.assertEqual(mock_ensure_dir.call_count, 4)
    
    def test_get_file_paths(self):
        """Test file path generation."""
        storage = LocalStorage(self.config)
        
        temp_path = storage.get_temp_file_path("test.txt")
        self.assertEqual(temp_path, './test_data/temp/test.txt')
        
        recording_path = storage.get_recording_file_path("audio.wav")
        self.assertEqual(recording_path, './test_data/recordings/audio.wav')
        
        processed_path = storage.get_processed_file_path("summary.json")
        self.assertEqual(processed_path, './test_data/processed/summary.json')


class TestSessionManager(unittest.TestCase):
    """Test session management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.storage = Mock()
        self.storage.get_processed_file_path.return_value = "/tmp/sessions.json"
        self.session_manager = SessionManager(self.storage)
    
    @patch('storage.session_manager.load_json')
    def test_create_session(self, mock_load_json):
        """Test session creation."""
        mock_load_json.return_value = []
        
        session_id = self.session_manager.create_session()
        
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(self.session_manager.current_session)
        self.assertEqual(self.session_manager.current_session['id'], session_id)
        self.assertIsNone(self.session_manager.current_session['end_time'])
    
    @patch('storage.session_manager.load_json')
    @patch('storage.session_manager.save_json')
    def test_end_session(self, mock_save_json, mock_load_json):
        """Test session ending."""
        mock_load_json.return_value = []
        
        # Create and end session
        session_id = self.session_manager.create_session()
        ended_id = self.session_manager.end_session()
        
        self.assertEqual(session_id, ended_id)
        self.assertIsNone(self.session_manager.current_session)
        mock_save_json.assert_called_once()
    
    @patch('storage.session_manager.load_json')
    def test_add_recording(self, mock_load_json):
        """Test adding recording to session."""
        mock_load_json.return_value = []
        
        self.session_manager.create_session()
        self.session_manager.add_recording("/tmp/recording.wav")
        
        recordings = self.session_manager.current_session['recordings']
        self.assertEqual(len(recordings), 1)
        self.assertEqual(recordings[0], "/tmp/recording.wav")
    
    @patch('storage.session_manager.load_json')
    def test_get_session(self, mock_load_json):
        """Test getting session by ID."""
        mock_load_json.return_value = [
            {'id': 'session1', 'duration': 300},
            {'id': 'session2', 'duration': 600}
        ]
        
        session_manager = SessionManager(self.storage)
        session = session_manager.get_session('session1')
        
        self.assertIsNotNone(session)
        self.assertEqual(session['id'], 'session1')
        self.assertEqual(session['duration'], 300)
        
        # Test non-existent session
        non_existent = session_manager.get_session('nonexistent')
        self.assertIsNone(non_existent)


if __name__ == '__main__':
    unittest.main()
