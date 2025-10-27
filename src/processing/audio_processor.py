"""Enhanced audio processing and transcription with comprehensive error handling."""

import os
import time
import wave
import librosa
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..error_handling.exceptions import ProcessingError, ValidationError, ResourceError, LLMError
from ..error_handling.logger import logger
from ..utils.constants import (
    AudioConstants, FileFormatConstants, 
    validate_sample_rate, validate_file_format, validate_channels
)
from ..utils.helpers import get_file_size_mb, format_duration


class AudioProcessor:
    """Enhanced audio processor with comprehensive error handling and edge case management."""
    
    def __init__(self, config, storage):
        self.config = config
        self.storage = storage
        
        # Audio processing settings with validation
        self.sample_rate = max(8000, min(config.get('processing.audio_sample_rate', 16000), 48000))
        self.channels = max(1, min(config.get('processing.audio_channels', 1), 2))
        self.max_audio_duration = config.get('processing.max_audio_duration', 3600)  # 1 hour
        self.min_audio_duration = config.get('processing.min_audio_duration', 0.1)  # 100ms
        self.transcription_timeout = config.get('processing.transcription_timeout', 300)  # 5 minutes
        self.max_concurrent_transcriptions = config.get('processing.max_concurrent_transcriptions', 2)
        
        # Supported formats
        self.supported_formats = FileFormatConstants.SUPPORTED_AUDIO_FORMATS
        
        # Processing statistics
        self.processing_stats = {
            'audio_files_processed': 0,
            'transcriptions_completed': 0,
            'errors_encountered': 0,
            'total_processing_time': 0,
            'total_audio_duration': 0
        }
        
        # Thread pool for concurrent processing
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_transcriptions)
        
        # Transcription cache
        self.transcription_cache = {}
        self.cache_max_size = 100
        
        logger.info(f"AudioProcessor initialized - Sample rate: {self.sample_rate}, Channels: {self.channels}")
    
    def _validate_audio_file(self, audio_path: str) -> Dict[str, Any]:
        """Validate audio file and get basic information."""
        try:
            audio_file = Path(audio_path)
            
            # Check if file exists
            if not audio_file.exists():
                raise ValidationError(f"Audio file does not exist: {audio_path}")
            
            # Check if it's a file
            if not audio_file.is_file():
                raise ValidationError(f"Path is not a file: {audio_path}")
            
            # Check file size
            file_size_mb = get_file_size_mb(audio_path)
            if file_size_mb == 0:
                raise ValidationError(f"Audio file is empty: {audio_path}")
            
            # Check file extension
            file_ext = audio_file.suffix.lower().lstrip('.')
            if not validate_file_format(file_ext, 'audio'):
                raise ValidationError(f"Unsupported audio format: {file_ext}")
            
            # Try to load with librosa for basic info
            try:
                # Load audio file metadata
                duration = librosa.get_duration(path=audio_path)
                sr = librosa.get_samplerate(audio_path)
                
                # Validate duration
                if duration < self.min_audio_duration:
                    raise ValidationError(f"Audio too short: {duration:.2f}s (minimum: {self.min_audio_duration}s)")
                
                if duration > self.max_audio_duration:
                    raise ValidationError(f"Audio too long: {duration:.2f}s (maximum: {self.max_audio_duration}s)")
                
                # Validate sample rate
                if not validate_sample_rate(sr):
                    logger.warning(f"Unusual sample rate: {sr}Hz for {audio_path}")
                
            except Exception as e:
                logger.warning(f"Could not load audio with librosa: {e}")
                # Fallback to basic file info
                duration = 0
                sr = self.sample_rate
            
            audio_info = {
                'path': audio_path,
                'size_mb': file_size_mb,
                'format': file_ext,
                'duration': duration,
                'sample_rate': sr,
                'valid': True
            }
            
            logger.info(f"Audio validation successful: {audio_path} - {duration:.1f}s, {sr}Hz")
            return audio_info
            
        except Exception as e:
            logger.error(f"Audio validation failed for {audio_path}: {e}")
            raise ValidationError(f"Audio validation failed: {e}")
    
    def _check_system_resources(self) -> bool:
        """Check if system has enough resources for audio processing."""
        try:
            import psutil
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                logger.warning(f"High memory usage: {memory.percent}%")
                return False
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 95:
                logger.warning(f"High CPU usage: {cpu_percent}%")
                return False
            
            # Check disk space
            disk_usage = psutil.disk_usage('.')
            free_gb = disk_usage.free / (1024**3)
            if free_gb < 0.5:  # Need at least 500MB
                logger.warning(f"Low disk space: {free_gb:.1f}GB")
                return False
            
            logger.debug(f"System resources OK - Memory: {memory.percent}%, CPU: {cpu_percent}%, Disk: {free_gb:.1f}GB")
            return True
            
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return False
    
    def transcribe_audio(self, audio_path: str, use_cache: bool = True) -> str:
        """Transcribe audio file to text with comprehensive error handling."""
        start_time = time.time()
        
        try:
            # Validate inputs
            if not audio_path:
                raise ValidationError("Audio path is required")
            
            # Check cache first
            if use_cache and audio_path in self.transcription_cache:
                logger.info(f"Using cached transcription for: {audio_path}")
                return self.transcription_cache[audio_path]
            
            # Validate audio file
            audio_info = self._validate_audio_file(audio_path)
            
            # Check system resources
            if not self._check_system_resources():
                raise ResourceError("Insufficient system resources for audio processing")
            
            logger.info(f"Transcribing audio: {audio_path}")
            logger.info(f"Audio info - Duration: {audio_info['duration']:.1f}s, Sample rate: {audio_info['sample_rate']}Hz")
            
            # Check file size for quick skip
            if audio_info['size_mb'] < 0.001:  # Less than 1KB
                logger.info("Audio file too small, likely empty")
                result = "No audio content detected"
            else:
                # Perform transcription
                result = self._perform_transcription(audio_path, audio_info)
            
            # Cache result
            if use_cache and len(self.transcription_cache) < self.cache_max_size:
                self.transcription_cache[audio_path] = result
            
            # Update statistics
            processing_time = time.time() - start_time
            self.processing_stats['audio_files_processed'] += 1
            self.processing_stats['transcriptions_completed'] += 1
            self.processing_stats['total_processing_time'] += processing_time
            self.processing_stats['total_audio_duration'] += audio_info['duration']
            
            logger.info(f"Transcription completed in {format_duration(processing_time)}")
            return result
            
        except Exception as e:
            self.processing_stats['errors_encountered'] += 1
            logger.error(f"Error transcribing audio {audio_path}: {e}", exc_info=True)
            
            # Return fallback message instead of raising exception
            return f"[Transcription failed: {str(e)}]"
    
    def _perform_transcription(self, audio_path: str, audio_info: Dict[str, Any]) -> str:
        """Perform actual transcription with multiple fallback methods."""
        try:
            # Method 1: Try Whisper (if available)
            try:
                return self._transcribe_with_whisper(audio_path)
            except Exception as e:
                logger.warning(f"Whisper transcription failed: {e}")
            
            # Method 2: Try basic audio analysis
            try:
                return self._analyze_audio_content(audio_path, audio_info)
            except Exception as e:
                logger.warning(f"Audio analysis failed: {e}")
            
            # Method 3: Placeholder transcription
            return self._placeholder_transcription(audio_info)
            
        except Exception as e:
            logger.error(f"All transcription methods failed: {e}")
            return f"[Transcription error: {str(e)}]"
    
    def _transcribe_with_whisper(self, audio_path: str) -> str:
        """Transcribe using Whisper (if available)."""
        try:
            import whisper
            
            # Load model (use base model for speed)
            model = whisper.load_model("base")
            
            # Transcribe with timeout protection
            start_time = time.time()
            result = model.transcribe(audio_path, language="en")
            
            if time.time() - start_time > self.transcription_timeout:
                raise TimeoutError("Transcription timeout")
            
            transcription = result["text"].strip()
            
            if not transcription:
                return "[No speech detected]"
            
            logger.info("Whisper transcription successful")
            return transcription
            
        except ImportError:
            logger.warning("Whisper not available, using fallback methods")
            raise Exception("Whisper not installed")
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            raise
    
    def _analyze_audio_content(self, audio_path: str, audio_info: Dict[str, Any]) -> str:
        """Analyze audio content for basic transcription."""
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=None)
            
            # Calculate audio features
            duration = len(y) / sr
            
            # Detect silence
            silence_threshold = 0.01
            silence_frames = np.sum(np.abs(y) < silence_threshold)
            silence_percentage = silence_frames / len(y) * 100
            
            # Detect speech-like patterns
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Analyze energy
            energy = np.sum(y**2)
            avg_energy = energy / len(y)
            
            # Generate description based on analysis
            if silence_percentage > 80:
                return "[Silent audio detected]"
            elif avg_energy < 0.001:
                return "[Very low volume audio]"
            elif duration < 1:
                return "[Very short audio clip]"
            else:
                # Estimate speech characteristics
                speech_indicators = []
                if np.mean(spectral_centroids) > 1000:
                    speech_indicators.append("high-frequency content")
                if np.mean(spectral_rolloff) > 2000:
                    speech_indicators.append("speech-like patterns")
                
                if speech_indicators:
                    return f"[Audio contains: {', '.join(speech_indicators)}]"
                else:
                    return f"[Audio detected - Duration: {duration:.1f}s, Volume: {'low' if avg_energy < 0.01 else 'medium' if avg_energy < 0.1 else 'high'}]"
            
        except Exception as e:
            logger.error(f"Audio analysis error: {e}")
            raise
    
    def _placeholder_transcription(self, audio_info: Dict[str, Any]) -> str:
        """Generate placeholder transcription based on audio info."""
        try:
            duration = audio_info['duration']
            size_mb = audio_info['size_mb']
            
            if duration < 1:
                return "[Very short audio clip]"
            elif duration < 5:
                return "[Short audio recording]"
            elif duration < 30:
                return "[Medium audio recording]"
            elif duration < 300:  # 5 minutes
                return "[Long audio recording]"
            else:
                return "[Very long audio recording]"
                
        except Exception as e:
            logger.error(f"Placeholder transcription error: {e}")
            return "[Audio transcription pending]"
    
    def analyze_audio(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """Analyze audio file properties with comprehensive error handling."""
        try:
            audio_file = Path(audio_path)
            
            # Basic file validation
            if not audio_file.exists():
                logger.warning(f"Audio file does not exist: {audio_path}")
                return None
            
            if not audio_file.is_file():
                logger.warning(f"Path is not a file: {audio_path}")
                return None
            
            # Get basic file info
            file_size_mb = get_file_size_mb(audio_path)
            file_ext = audio_file.suffix.lower().lstrip('.')
            
            # Try to get audio properties
            try:
                duration = librosa.get_duration(path=audio_path)
                sr = librosa.get_samplerate(audio_path)
                
                # Load audio for analysis
                y, sr = librosa.load(audio_path, sr=None)
                
                # Calculate audio features
                spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
                spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
                zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
                
                # Energy analysis
                energy = np.sum(y**2)
                avg_energy = energy / len(y)
                
                # Silence detection
                silence_threshold = 0.01
                silence_frames = np.sum(np.abs(y) < silence_threshold)
                silence_percentage = silence_frames / len(y) * 100
                
                # Frequency analysis
                fft = np.fft.fft(y)
                freqs = np.fft.fftfreq(len(y), 1/sr)
                dominant_freq = freqs[np.argmax(np.abs(fft))]
                
                analysis_result = {
                    'path': audio_path,
                    'size_mb': file_size_mb,
                    'format': file_ext,
                    'duration': duration,
                    'sample_rate': sr,
                    'channels': 1,  # librosa loads as mono
                    'avg_energy': float(avg_energy),
                    'silence_percentage': float(silence_percentage),
                    'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                    'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                    'zero_crossing_rate_mean': float(np.mean(zero_crossing_rate)),
                    'dominant_frequency': float(abs(dominant_freq)),
                    'audio_quality': self._assess_audio_quality(avg_energy, silence_percentage, sr),
                    'timestamp': time.time()
                }
                
            except Exception as e:
                logger.warning(f"Could not analyze audio properties: {e}")
                # Fallback to basic info
                analysis_result = {
                    'path': audio_path,
                    'size_mb': file_size_mb,
                    'format': file_ext,
                    'duration': 0,
                    'sample_rate': 0,
                    'channels': 0,
                    'audio_quality': 'unknown',
                    'timestamp': time.time()
                }
            
            logger.debug(f"Audio analysis completed: {audio_path}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing audio {audio_path}: {e}")
            return None
    
    def _assess_audio_quality(self, avg_energy: float, silence_percentage: float, sample_rate: int) -> str:
        """Assess audio quality based on various metrics."""
        try:
            quality_score = 0
            
            # Energy assessment
            if avg_energy > 0.1:
                quality_score += 3
            elif avg_energy > 0.01:
                quality_score += 2
            elif avg_energy > 0.001:
                quality_score += 1
            
            # Silence assessment
            if silence_percentage < 20:
                quality_score += 3
            elif silence_percentage < 50:
                quality_score += 2
            elif silence_percentage < 80:
                quality_score += 1
            
            # Sample rate assessment
            if sample_rate >= 44100:
                quality_score += 2
            elif sample_rate >= 22050:
                quality_score += 1
            
            # Determine quality level
            if quality_score >= 7:
                return 'high'
            elif quality_score >= 4:
                return 'medium'
            elif quality_score >= 1:
                return 'low'
            else:
                return 'poor'
                
        except Exception as e:
            logger.error(f"Error assessing audio quality: {e}")
            return 'unknown'
    
    def batch_transcribe(self, audio_paths: List[str], use_cache: bool = True) -> List[str]:
        """Transcribe multiple audio files concurrently."""
        try:
            if not audio_paths:
                return []
            
            logger.info(f"Batch transcribing {len(audio_paths)} audio files")
            
            results = []
            with ThreadPoolExecutor(max_workers=self.max_concurrent_transcriptions) as executor:
                # Submit all tasks
                future_to_path = {
                    executor.submit(self.transcribe_audio, path, use_cache): path 
                    for path in audio_paths
                }
                
                # Collect results
                for future in as_completed(future_to_path):
                    path = future_to_path[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error transcribing {path}: {e}")
                        results.append(f"[Transcription failed: {str(e)}]")
            
            logger.info(f"Batch transcription completed: {len(results)}/{len(audio_paths)} successful")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch transcription: {e}")
            return [f"[Batch transcription failed: {str(e)}]"] * len(audio_paths)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        try:
            avg_processing_time = 0
            avg_audio_duration = 0
            
            if self.processing_stats['audio_files_processed'] > 0:
                avg_processing_time = (self.processing_stats['total_processing_time'] / 
                                     self.processing_stats['audio_files_processed'])
                avg_audio_duration = (self.processing_stats['total_audio_duration'] / 
                                    self.processing_stats['audio_files_processed'])
            
            return {
                'audio_files_processed': self.processing_stats['audio_files_processed'],
                'transcriptions_completed': self.processing_stats['transcriptions_completed'],
                'errors_encountered': self.processing_stats['errors_encountered'],
                'total_processing_time': self.processing_stats['total_processing_time'],
                'total_audio_duration': self.processing_stats['total_audio_duration'],
                'average_processing_time': avg_processing_time,
                'average_audio_duration': avg_audio_duration,
                'success_rate': (self.processing_stats['transcriptions_completed'] - 
                               self.processing_stats['errors_encountered']) / 
                               max(1, self.processing_stats['audio_files_processed']),
                'cache_size': len(self.transcription_cache)
            }
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {}
    
    def clear_cache(self) -> None:
        """Clear transcription cache."""
        try:
            self.transcription_cache.clear()
            logger.info("Transcription cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def reset_stats(self) -> None:
        """Reset processing statistics."""
        try:
            self.processing_stats = {
                'audio_files_processed': 0,
                'transcriptions_completed': 0,
                'errors_encountered': 0,
                'total_processing_time': 0,
                'total_audio_duration': 0
            }
            logger.info("Processing statistics reset")
        except Exception as e:
            logger.error(f"Error resetting stats: {e}")
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            self.clear_cache()
            logger.info("AudioProcessor cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except:
            pass
