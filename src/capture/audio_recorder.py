"""Enhanced audio recording functionality with comprehensive error handling."""
import wave
import os
import time
import threading
import queue
from typing import List, Dict, Optional, Tuple
import pyaudio
from threading import Thread, Event, Lock
from ..error_handling.exceptions import RecordingError, DeviceError
from ..error_handling.logger import logger


class AudioRecorder:
    """Enhanced audio recorder with comprehensive error handling and device management."""
    
    def __init__(self, config, storage):
        self.config = config
        self.storage = storage
        self.sample_rate = max(8000, min(config.get('recording.audio_sample_rate', 16000), 48000))  # Clamp 8-48kHz
        self.channels = config.get('recording.audio_channels', 1)  # Mono by default
        self.chunk_size = config.get('recording.audio_chunk_size', 1024)
        self.format = pyaudio.paInt16
        self.is_recording = False
        self.stop_event = Event()
        self.recording_thread = None
        self.frames = []
        self.frame_lock = Lock()
        self.audio = None
        self.stream = None
        self.output_path = None
        self.recording_start_time = None
        self.total_chunks_recorded = 0
        self.failed_chunks = 0
        self.max_failed_chunks = 50
        self.audio_queue = queue.Queue(maxsize=1000)  # Buffer for audio data
        self.device_info = None
        self.supported_formats = None
        
    def _detect_audio_devices(self) -> List[Dict]:
        """Detect available audio input devices."""
        try:
            if not self.audio:
                self.audio = pyaudio.PyAudio()
            
            devices = []
            device_count = self.audio.get_device_count()
            
            for i in range(device_count):
                try:
                    device_info = self.audio.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:  # Has input capability
                        devices.append({
                            'index': i,
                            'name': device_info['name'],
                            'channels': device_info['maxInputChannels'],
                            'sample_rate': device_info['defaultSampleRate'],
                            'latency': device_info['defaultLowInputLatency']
                        })
                except Exception as e:
                    logger.warning(f"Error getting device info for device {i}: {e}")
                    continue
            
            logger.info(f"Detected {len(devices)} audio input devices")
            return devices
            
        except Exception as e:
            logger.error(f"Error detecting audio devices: {e}")
            return []
    
    def _select_best_device(self) -> Optional[Dict]:
        """Select the best audio input device."""
        try:
            devices = self._detect_audio_devices()
            if not devices:
                logger.warning("No audio input devices found")
                return None
            
            # Prefer default device or first available
            try:
                default_device = self.audio.get_default_input_device_info()
                for device in devices:
                    if device['index'] == default_device['index']:
                        logger.info(f"Selected default audio device: {device['name']}")
                        return device
            except Exception as e:
                logger.warning(f"Could not get default device: {e}")
            
            # Fallback to first device
            selected_device = devices[0]
            logger.info(f"Selected audio device: {selected_device['name']}")
            return selected_device
            
        except Exception as e:
            logger.error(f"Error selecting audio device: {e}")
            return None
    
    def _test_device_capabilities(self, device_index: int) -> bool:
        """Test if device supports required audio format."""
        try:
            if not self.audio:
                return False
            
            # Test if device supports our format
            is_supported = self.audio.is_format_supported(
                rate=self.sample_rate,
                input_device=device_index,
                input_channels=self.channels,
                input_format=self.format
            )
            
            if is_supported:
                logger.info(f"Device {device_index} supports required format")
                return True
            else:
                logger.warning(f"Device {device_index} does not support required format")
                return False
                
        except Exception as e:
            logger.error(f"Error testing device capabilities: {e}")
            return False
    
    def _check_audio_permissions(self) -> bool:
        """Check if we have audio recording permissions."""
        try:
            # Try to initialize PyAudio
            if not self.audio:
                self.audio = pyaudio.PyAudio()
            
            # Try to get device count (this will fail if no permissions)
            device_count = self.audio.get_device_count()
            if device_count == 0:
                logger.warning("No audio devices available")
                return False
            
            logger.info("Audio permissions check passed")
            return True
            
        except Exception as e:
            logger.error(f"Audio permissions check failed: {e}")
            return False
    
    def _validate_audio_settings(self) -> bool:
        """Validate audio recording settings."""
        try:
            # Check sample rate
            if self.sample_rate < 8000 or self.sample_rate > 48000:
                logger.error(f"Invalid sample rate: {self.sample_rate}")
                return False
            
            # Check channels
            if self.channels < 1 or self.channels > 2:
                logger.error(f"Invalid channel count: {self.channels}")
                return False
            
            # Check chunk size
            if self.chunk_size < 256 or self.chunk_size > 4096:
                logger.error(f"Invalid chunk size: {self.chunk_size}")
                return False
            
            logger.info(f"Audio settings validated - Rate: {self.sample_rate}, Channels: {self.channels}, Chunk: {self.chunk_size}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating audio settings: {e}")
            return False
    
    def start_recording(self, output_path: str) -> None:
        """Start audio recording with comprehensive error handling."""
        if self.is_recording:
            raise RecordingError("Audio recording already in progress")
        
        try:
            # Validate output path
            if not output_path:
                raise RecordingError("Output path is required")
            
            # Validate audio settings
            if not self._validate_audio_settings():
                raise RecordingError("Invalid audio settings")
            
            # Check permissions
            if not self._check_audio_permissions():
                raise RecordingError("No audio recording permissions")
            
            # Initialize PyAudio
            if not self.audio:
                self.audio = pyaudio.PyAudio()
            
            # Select device
            self.device_info = self._select_best_device()
            if not self.device_info:
                raise RecordingError("No suitable audio input device found")
            
            # Test device capabilities
            if not self._test_device_capabilities(self.device_info['index']):
                raise RecordingError(f"Audio device {self.device_info['name']} does not support required format")
            
            # Initialize recording state
            self.is_recording = True
            self.stop_event.clear()
            self.frames = []
            self.output_path = output_path
            self.recording_start_time = time.time()
            self.total_chunks_recorded = 0
            self.failed_chunks = 0
            
            # Clear audio queue
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break
            
            # Try to open stream
            try:
                self.stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=self.device_info['index'],
                    frames_per_buffer=self.chunk_size,
                    stream_callback=None
                )
                
                if not self.stream.is_active():
                    raise RecordingError("Audio stream is not active")
                
            except Exception as e:
                logger.error(f"Failed to open audio stream: {e}")
                raise RecordingError(f"Failed to open audio stream: {e}")
            
            # Start recording thread
            self.recording_thread = Thread(target=self._record_loop, daemon=True)
            self.recording_thread.start()
            
            logger.info(f"Started audio recording: {output_path}")
            logger.info(f"Audio settings - Device: {self.device_info['name']}, Rate: {self.sample_rate}, Channels: {self.channels}")
            
        except Exception as e:
            self.is_recording = False
            self._cleanup_audio_resources()
            logger.error(f"Failed to start audio recording: {e}", exc_info=True)
            raise RecordingError(f"Failed to start audio recording: {e}")
    
    def stop_recording(self) -> Optional[str]:
        """Stop audio recording with comprehensive error handling."""
        if not self.is_recording:
            logger.warning("No audio recording in progress to stop")
            return None
        
        try:
            logger.info("Stopping audio recording...")
            
            # Signal stop
            self.stop_event.set()
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=10)  # Wait up to 10 seconds
                
                if self.recording_thread.is_alive():
                    logger.warning("Audio recording thread did not stop gracefully")
            
            # Process remaining audio data in queue
            self._process_remaining_audio()
            
            # Close stream
            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except Exception as e:
                    logger.warning(f"Error closing audio stream: {e}")
                finally:
                    self.stream = None
            
            # Save audio file if we have data
            audio_path = None
            if self.frames:
                audio_path = self._save_audio()
            
            # Log statistics
            duration = time.time() - self.recording_start_time if self.recording_start_time else 0
            logger.info(f"Audio recording stopped - Duration: {duration:.1f}s, Chunks: {self.total_chunks_recorded}, Failed: {self.failed_chunks}")
            
            self.is_recording = False
            return audio_path
            
        except Exception as e:
            logger.error(f"Error stopping audio recording: {e}", exc_info=True)
            self.is_recording = False
            return None
        finally:
            self._cleanup_audio_resources()
    
    def _record_loop(self) -> None:
        """Enhanced main audio recording loop with comprehensive error handling."""
        try:
            logger.info("Audio recording loop started")
            
            while not self.stop_event.is_set():
                try:
                    # Check for too many failed chunks
                    if self.failed_chunks >= self.max_failed_chunks:
                        logger.error(f"Too many failed audio chunks ({self.failed_chunks}), stopping recording")
                        break
                    
                    # Read audio data
                    try:
                        data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                        if not data:
                            self.failed_chunks += 1
                            logger.warning(f"Empty audio data received (attempt {self.failed_chunks})")
                            continue
                        
                        # Add to queue
                        try:
                            self.audio_queue.put_nowait((data, time.time()))
                        except queue.Full:
                            logger.warning("Audio queue full, dropping chunk")
                            continue
                        
                        # Process audio data from queue
                        self._process_audio_queue()
                        
                        self.total_chunks_recorded += 1
                        
                        # Log progress every 1000 chunks
                        if self.total_chunks_recorded % 1000 == 0:
                            logger.info(f"Recorded {self.total_chunks_recorded} audio chunks")
                        
                    except Exception as e:
                        self.failed_chunks += 1
                        logger.warning(f"Error reading audio data (attempt {self.failed_chunks}): {e}")
                        if self.failed_chunks >= self.max_failed_chunks:
                            break
                        time.sleep(0.1)  # Brief pause before retry
                
                except Exception as e:
                    self.failed_chunks += 1
                    logger.error(f"Error in audio recording loop iteration: {e}")
                    if self.failed_chunks >= self.max_failed_chunks:
                        break
                    time.sleep(0.1)
            
            logger.info("Audio recording loop ended")
            
        except Exception as e:
            logger.error(f"Error in audio recording loop: {e}", exc_info=True)
            self.failed_chunks += 1
    
    def _process_audio_queue(self) -> None:
        """Process audio data from the queue."""
        try:
            while not self.audio_queue.empty():
                try:
                    data, timestamp = self.audio_queue.get_nowait()
                    
                    with self.frame_lock:
                        self.frames.append(data)
                        
                except queue.Empty:
                    break
                except Exception as e:
                    logger.error(f"Error processing audio data: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing audio queue: {e}")
    
    def _process_remaining_audio(self) -> None:
        """Process any remaining audio data in the queue."""
        try:
            logger.info("Processing remaining audio data...")
            while not self.audio_queue.empty():
                self._process_audio_queue()
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
        except Exception as e:
            logger.error(f"Error processing remaining audio: {e}")
    
    def _save_audio(self) -> Optional[str]:
        """Save audio frames to WAV file with comprehensive error handling."""
        if not self.frames:
            logger.warning("No audio frames to save")
            return None
        
        try:
            logger.info(f"Saving {len(self.frames)} audio chunks to file...")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            # Calculate total duration
            total_samples = len(self.frames) * self.chunk_size
            duration = total_samples / self.sample_rate
            
            # Save to WAV file
            with wave.open(self.output_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                
                # Write all frames
                audio_data = b''.join(self.frames)
                wf.writeframes(audio_data)
            
            # Verify file was created and has content
            if not os.path.exists(self.output_path):
                raise RecordingError("Audio file was not created")
            
            file_size = os.path.getsize(self.output_path)
            if file_size == 0:
                raise RecordingError("Audio file is empty")
            
            logger.info(f"Audio saved successfully: {self.output_path} ({file_size} bytes, {duration:.1f}s)")
            return self.output_path
            
        except Exception as e:
            logger.error(f"Error saving audio: {e}", exc_info=True)
            raise RecordingError(f"Failed to save audio: {e}")
    
    def _cleanup_audio_resources(self) -> None:
        """Cleanup audio resources."""
        try:
            if self.audio:
                self.audio.terminate()
                self.audio = None
        except Exception as e:
            logger.error(f"Error cleaning up audio resources: {e}")
    
    def get_recording_stats(self) -> Dict:
        """Get current audio recording statistics."""
        try:
            duration = 0
            if self.recording_start_time:
                duration = time.time() - self.recording_start_time
            
            return {
                'is_recording': self.is_recording,
                'duration': duration,
                'total_chunks': self.total_chunks_recorded,
                'failed_chunks': self.failed_chunks,
                'frames_in_memory': len(self.frames),
                'queue_size': self.audio_queue.qsize(),
                'sample_rate': self.sample_rate,
                'channels': self.channels,
                'device_info': self.device_info
            }
        except Exception as e:
            logger.error(f"Error getting audio recording stats: {e}")
            return {}
    
    def get_available_devices(self) -> List[Dict]:
        """Get list of available audio input devices."""
        try:
            return self._detect_audio_devices()
        except Exception as e:
            logger.error(f"Error getting available devices: {e}")
            return []
    
    def test_device(self, device_index: int) -> bool:
        """Test if a specific device works with current settings."""
        try:
            if not self.audio:
                self.audio = pyaudio.PyAudio()
            
            # Test device capabilities
            return self._test_device_capabilities(device_index)
            
        except Exception as e:
            logger.error(f"Error testing device {device_index}: {e}")
            return False
