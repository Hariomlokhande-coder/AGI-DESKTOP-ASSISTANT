"""Test cases for processing functionality."""
import unittest
import os
import tempfile
from unittest.mock import Mock, patch
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from processing.video_processor import VideoProcessor
from processing.audio_processor import AudioProcessor
from processing.json_generator import JSONGenerator
from processing.cleanup import CleanupManager


class TestVideoProcessor(unittest.TestCase):
    """Test video processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock()
        self.config.get.side_effect = lambda key, default=None: {
            'processing.frame_resize_width': 1280,
            'processing.frame_resize_height': 720
        }.get(key, default)
        
        self.storage = Mock()
        self.storage.temp_path = "/tmp"
        
        self.processor = VideoProcessor(self.config, self.storage)
    
    def test_initialization(self):
        """Test processor initialization."""
        self.assertEqual(self.processor.resize_width, 1280)
        self.assertEqual(self.processor.resize_height, 720)
    
    def test_extract_frames_file_not_found(self):
        """Test extracting frames from non-existent file."""
        with self.assertRaises(Exception):  # ProcessingError
            self.processor.extract_frames("/nonexistent/video.mp4")
    
    @patch('processing.video_processor.cv2')
    def test_analyze_frame(self, mock_cv2):
        """Test frame analysis."""
        mock_cv2.imread.return_value = Mock()
        mock_cv2.cvtColor.return_value = Mock()
        mock_cv2.cvtColor.return_value.mean.return_value = 128.5
        
        result = self.processor.analyze_frame("/tmp/frame.jpg")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['brightness'], 128.5)


class TestAudioProcessor(unittest.TestCase):
    """Test audio processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock()
        self.storage = Mock()
        self.processor = AudioProcessor(self.config, self.storage)
    
    def test_transcribe_audio_file_not_found(self):
        """Test transcribing non-existent audio file."""
        result = self.processor.transcribe_audio("/nonexistent/audio.wav")
        self.assertEqual(result, "")
    
    @patch('processing.audio_processor.os.path.exists')
    @patch('processing.audio_processor.os.path.getsize')
    def test_transcribe_audio_small_file(self, mock_getsize, mock_exists):
        """Test transcribing very small audio file."""
        mock_exists.return_value = True
        mock_getsize.return_value = 500  # Less than 1KB
        
        result = self.processor.transcribe_audio("/tmp/small.wav")
        self.assertEqual(result, "No audio captured")
    
    @patch('processing.audio_processor.os.path.exists')
    @patch('processing.audio_processor.os.path.getsize')
    def test_analyze_audio(self, mock_getsize, mock_exists):
        """Test audio analysis."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024  # 1MB
        
        result = self.processor.analyze_audio("/tmp/audio.wav")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['size_mb'], 1.0)
        self.assertTrue(result['exists'])


class TestJSONGenerator(unittest.TestCase):
    """Test JSON generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.storage = Mock()
        self.storage.get_processed_file_path.return_value = "/tmp/summary.json"
        self.generator = JSONGenerator(self.storage)
    
    @patch('processing.json_generator.save_json')
    def test_generate_session_summary(self, mock_save_json):
        """Test session summary generation."""
        session_data = {
            'id': 'test_session',
            'start_time': '2024-01-01T10:00:00',
            'end_time': '2024-01-01T10:05:00',
            'duration': 300
        }
        
        frames_data = [{'path': '/tmp/frame1.jpg'}, {'path': '/tmp/frame2.jpg'}]
        audio_data = {'transcription': 'Test transcription'}
        workflows = [{'description': 'Test workflow', 'automation_potential': 'High'}]
        
        result = self.generator.generate_session_summary(
            session_data, frames_data, audio_data, workflows
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['session_id'], 'test_session')
        self.assertEqual(len(result['capture_data']['frames']), 2)
        self.assertEqual(len(result['detected_workflows']), 1)
        mock_save_json.assert_called_once()


class TestCleanupManager(unittest.TestCase):
    """Test cleanup functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.storage = Mock()
        self.storage.temp_path = "/tmp"
        self.storage.processed_path = "/tmp/processed"
        
        self.config = Mock()
        self.config.get.return_value = True  # auto_delete
        
        self.cleanup = CleanupManager(self.storage, self.config)
    
    @patch('processing.cleanup.os.path.exists')
    @patch('processing.cleanup.os.listdir')
    def test_cleanup_temp_directory(self, mock_listdir, mock_exists):
        """Test temp directory cleanup."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        
        # This would normally delete files, but we're just testing the logic
        self.cleanup.cleanup_temp_directory()
        
        mock_exists.assert_called_with("/tmp")
        mock_listdir.assert_called_with("/tmp")


if __name__ == '__main__':
    unittest.main()
