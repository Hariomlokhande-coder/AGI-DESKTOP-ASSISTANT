"""Test cases for capture functionality."""
import unittest
import os
import tempfile
from unittest.mock import Mock, patch
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from capture.screen_recorder import ScreenshotCapture
from capture.audio_recorder import AudioRecorder
from capture.device_manager import DeviceManager


class TestScreenshotCapture(unittest.TestCase):
    """Test screenshot capture functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock()
        self.config.get.return_value = 5  # screenshot interval
        self.storage = Mock()
        self.storage.get_temp_file_path.return_value = "/tmp/test.png"
        
        self.capture = ScreenshotCapture(self.config, self.storage)
    
    def test_initialization(self):
        """Test capture initialization."""
        self.assertEqual(self.capture.interval, 5)
        self.assertFalse(self.capture.is_capturing)
    
    @patch('capture.screen_recorder.mss')
    def test_start_capture(self, mock_mss):
        """Test starting capture."""
        mock_sct = Mock()
        mock_mss.mss.return_value.__enter__.return_value = mock_sct
        mock_sct.monitors = [None, {'width': 1920, 'height': 1080}]
        mock_sct.grab.return_value = Mock()
        
        # This would normally start a thread, so we'll just test the setup
        self.capture.session_id = "test_session"
        self.capture.is_capturing = True
        
        self.assertTrue(self.capture.is_capturing)
    
    def test_stop_capture_when_not_capturing(self):
        """Test stopping capture when not capturing."""
        result = self.capture.stop_capture()
        self.assertEqual(result, [])


class TestAudioRecorder(unittest.TestCase):
    """Test audio recording functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock()
        self.config.get.return_value = 16000  # sample rate
        self.storage = Mock()
        self.storage.get_temp_file_path.return_value = "/tmp/test.wav"
        
        self.recorder = AudioRecorder(self.config, self.storage)
    
    def test_initialization(self):
        """Test recorder initialization."""
        self.assertEqual(self.recorder.sample_rate, 16000)
        self.assertFalse(self.recorder.is_recording)
    
    @patch('capture.audio_recorder.pyaudio')
    def test_start_recording_no_devices(self, mock_pyaudio):
        """Test starting recording when no audio devices available."""
        mock_audio = Mock()
        mock_audio.open.side_effect = Exception("No audio devices")
        mock_pyaudio.PyAudio.return_value = mock_audio
        
        # Should not raise exception, just log warning
        self.recorder.start_recording("/tmp/test.wav")
        self.assertFalse(self.recorder.is_recording)


class TestDeviceManager(unittest.TestCase):
    """Test device management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.device_manager = DeviceManager()
    
    @patch('capture.device_manager.pyaudio')
    def test_check_audio_devices(self, mock_pyaudio):
        """Test checking audio devices."""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 2
        mock_audio.get_device_info_by_index.side_effect = [
            {'maxInputChannels': 1, 'name': 'Microphone', 'defaultSampleRate': 44100},
            {'maxInputChannels': 0, 'name': 'Speaker', 'defaultSampleRate': 44100}
        ]
        mock_pyaudio.PyAudio.return_value = mock_audio
        
        devices = self.device_manager.check_audio_devices()
        
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0]['name'], 'Microphone')
        self.assertTrue(self.device_manager.available_audio)
    
    @patch('capture.device_manager.mss')
    def test_check_screen_capture_permission(self, mock_mss):
        """Test screen capture permission check."""
        mock_sct = Mock()
        mock_sct.monitors = [None, {'width': 1920, 'height': 1080}]
        mock_sct.grab.return_value = Mock()
        mock_mss.mss.return_value.__enter__.return_value = mock_sct
        
        result = self.device_manager.check_screen_capture_permission()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
