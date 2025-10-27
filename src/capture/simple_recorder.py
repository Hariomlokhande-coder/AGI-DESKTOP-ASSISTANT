"""Simplified screen and audio recording."""

import os
import time
import logging
from pathlib import Path
from typing import List, Optional

try:
    import mss
    import cv2
    import numpy as np
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    print("Warning: mss and opencv-python not available. Screen recording disabled.")

try:
    import pyaudio
    import wave
    import threading
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Warning: pyaudio not available. Audio recording disabled.")


class SimpleScreenRecorder:
    """Simplified screen recorder."""
    
    def __init__(self):
        self.screenshots = []
        self.recording = False
        self.output_dir = Path("user_data/screenshots")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def start_recording(self):
        """Start screen recording."""
        if not MSS_AVAILABLE:
            print("Screen recording not available - mss not installed")
            return False
        
        try:
            self.recording = True
            self.screenshots = []
            print("Screen recording started")
            return True
        except Exception as e:
            print(f"Failed to start screen recording: {e}")
            return False
    
    def stop_recording(self):
        """Stop screen recording."""
        self.recording = False
        print("Screen recording stopped")
    
    def capture_screenshot(self):
        """Capture a single screenshot."""
        if not MSS_AVAILABLE or not self.recording:
            return None
        
        try:
            with mss.mss() as sct:
                # Get the primary monitor
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Save screenshot
                timestamp = int(time.time() * 1000)
                filename = f"screenshot_{timestamp}.jpg"
                filepath = self.output_dir / filename
                
                cv2.imwrite(str(filepath), img)
                self.screenshots.append(str(filepath))
                
                return str(filepath)
                
        except Exception as e:
            print(f"Screenshot capture failed: {e}")
            return None
    
    def get_screenshots(self) -> List[str]:
        """Get list of captured screenshots."""
        return self.screenshots


class SimpleAudioRecorder:
    """Simplified audio recorder."""
    
    def __init__(self):
        self.recording = False
        self.audio_frames = []
        self.audio_thread = None
        self.output_dir = Path("user_data/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def start_recording(self):
        """Start audio recording."""
        if not PYAUDIO_AVAILABLE:
            print("Audio recording not available - pyaudio not installed")
            return False
        
        try:
            self.recording = True
            self.audio_frames = []
            
            # Start audio recording thread
            self.audio_thread = threading.Thread(target=self._record_audio)
            self.audio_thread.start()
            
            print("Audio recording started")
            return True
        except Exception as e:
            print(f"Failed to start audio recording: {e}")
            return False
    
    def stop_recording(self):
        """Stop audio recording."""
        self.recording = False
        if self.audio_thread:
            self.audio_thread.join()
        
        # Save audio file
        self._save_audio()
        print("Audio recording stopped")
    
    def _record_audio(self):
        """Record audio in background thread."""
        try:
            p = pyaudio.PyAudio()
            
            # Audio settings
            chunk = 1024
            format = pyaudio.paInt16
            channels = 1
            rate = 16000
            
            stream = p.open(
                format=format,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk
            )
            
            while self.recording:
                data = stream.read(chunk)
                self.audio_frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            print(f"Audio recording error: {e}")
    
    def _save_audio(self):
        """Save recorded audio to file."""
        if not self.audio_frames:
            return
        
        try:
            timestamp = int(time.time() * 1000)
            filename = f"audio_{timestamp}.wav"
            filepath = self.output_dir / filename
            
            p = pyaudio.PyAudio()
            
            with wave.open(str(filepath), 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(16000)
                wf.writeframes(b''.join(self.audio_frames))
            
            p.terminate()
            self.audio_path = str(filepath)
            
        except Exception as e:
            print(f"Failed to save audio: {e}")
    
    def get_audio_path(self) -> Optional[str]:
        """Get path to recorded audio file."""
        return getattr(self, 'audio_path', None)


# Simplified recorders for the main application
class ScreenshotCapture(SimpleScreenRecorder):
    """Screenshot capture for main app with indefinite recording."""
    
    def __init__(self):
        super().__init__()
        self.recording_thread = None
        self.interval = 2  # Capture every 2 seconds
        self.capture_count = 0
    
    def start_recording(self):
        """Start continuous screenshot capture."""
        if not super().start_recording():
            return False
        
        # Reset capture count
        self.capture_count = 0
        
        # Start capture thread
        self.recording_thread = threading.Thread(target=self._capture_loop)
        self.recording_thread.start()
        return True
    
    def stop_recording(self):
        """Stop screenshot capture."""
        super().stop_recording()
        if self.recording_thread:
            self.recording_thread.join()
    
    def _capture_loop(self):
        """Continuous capture loop for indefinite recording."""
        while self.recording:
            try:
                screenshot_path = self.capture_screenshot()
                if screenshot_path:
                    self.capture_count += 1
                    # Log progress every 10 screenshots
                    if self.capture_count % 10 == 0:
                        print(f"Captured {self.capture_count} screenshots...")
                
                time.sleep(self.interval)
            except Exception as e:
                print(f"Screenshot capture error: {e}")
                time.sleep(self.interval)
    
    def get_capture_count(self):
        """Get number of screenshots captured."""
        return self.capture_count


class AudioRecorder(SimpleAudioRecorder):
    """Audio recorder for main app."""
    pass
