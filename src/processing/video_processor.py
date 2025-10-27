"""Enhanced video processing and frame extraction with comprehensive error handling."""

import cv2
import os
import numpy as np
import time
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from ..error_handling.exceptions import ProcessingError, ValidationError, ResourceError
from ..error_handling.logger import logger
from ..utils.constants import (
    RecordingConstants, FileFormatConstants, 
    validate_fps, validate_quality, validate_file_format
)
from ..utils.helpers import ensure_directory, get_file_size_mb, format_duration


class VideoProcessor:
    """Enhanced video processor with comprehensive error handling and edge case management."""
    
    def __init__(self, config, storage):
        self.config = config
        self.storage = storage
        
        # Video processing settings with validation
        self.resize_width = max(320, min(config.get('processing.frame_resize_width', 1280), 3840))
        self.resize_height = max(240, min(config.get('processing.frame_resize_height', 720), 2160))
        self.quality = max(1, min(config.get('processing.frame_quality', 85), 100))
        self.max_frames_per_video = config.get('processing.max_frames_per_video', 1000)
        self.frame_extraction_timeout = config.get('processing.frame_extraction_timeout', 300)  # 5 minutes
        self.max_concurrent_extractions = config.get('processing.max_concurrent_extractions', 4)
        
        # Supported formats
        self.supported_formats = FileFormatConstants.SUPPORTED_VIDEO_FORMATS
        
        # Processing statistics
        self.processing_stats = {
            'videos_processed': 0,
            'frames_extracted': 0,
            'errors_encountered': 0,
            'total_processing_time': 0
        }
        
        # Thread pool for concurrent processing
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_extractions)
        
        logger.info(f"VideoProcessor initialized - Resize: {self.resize_width}x{self.resize_height}, Quality: {self.quality}")
    
    def _validate_video_file(self, video_path: str) -> Dict[str, Any]:
        """Validate video file and get basic information."""
        try:
            video_file = Path(video_path)
            
            # Check if file exists
            if not video_file.exists():
                raise ValidationError(f"Video file does not exist: {video_path}")
            
            # Check if it's a file
            if not video_file.is_file():
                raise ValidationError(f"Path is not a file: {video_path}")
            
            # Check file size
            file_size_mb = get_file_size_mb(video_path)
            if file_size_mb == 0:
                raise ValidationError(f"Video file is empty: {video_path}")
            
            # Check file extension
            file_ext = video_file.suffix.lower().lstrip('.')
            if not validate_file_format(file_ext, 'video'):
                raise ValidationError(f"Unsupported video format: {file_ext}")
            
            # Try to open with OpenCV
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                cap.release()
                raise ValidationError(f"Cannot open video file: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            # Validate video properties
            if fps <= 0:
                logger.warning(f"Invalid FPS ({fps}) for video: {video_path}")
                fps = 30  # Default fallback
            
            if frame_count <= 0:
                raise ValidationError(f"Invalid frame count ({frame_count}) for video: {video_path}")
            
            if width <= 0 or height <= 0:
                raise ValidationError(f"Invalid dimensions ({width}x{height}) for video: {video_path}")
            
            video_info = {
                'path': video_path,
                'size_mb': file_size_mb,
                'format': file_ext,
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration': duration,
                'valid': True
            }
            
            logger.info(f"Video validation successful: {video_path} - {width}x{height}, {fps:.1f}fps, {duration:.1f}s")
            return video_info
            
        except Exception as e:
            logger.error(f"Video validation failed for {video_path}: {e}")
            raise ValidationError(f"Video validation failed: {e}")
    
    def _check_system_resources(self) -> bool:
        """Check if system has enough resources for video processing."""
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
            if free_gb < 1:  # Need at least 1GB
                logger.warning(f"Low disk space: {free_gb:.1f}GB")
                return False
            
            logger.debug(f"System resources OK - Memory: {memory.percent}%, CPU: {cpu_percent}%, Disk: {free_gb:.1f}GB")
            return True
            
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return False
    
    def extract_frames(self, video_path: str, output_dir: Optional[str] = None, 
                      interval: float = 5.0, max_frames: Optional[int] = None) -> List[Dict[str, Any]]:
        """Extract frames from video with comprehensive error handling."""
        start_time = time.time()
        
        try:
            # Validate inputs
            if not video_path:
                raise ValidationError("Video path is required")
            
            if interval <= 0:
                raise ValidationError(f"Invalid interval: {interval}")
            
            # Validate video file
            video_info = self._validate_video_file(video_path)
            
            # Check system resources
            if not self._check_system_resources():
                raise ResourceError("Insufficient system resources for video processing")
            
            # Set output directory
            if output_dir is None:
                output_dir = self.storage.temp_path
            
            # Ensure output directory exists
            output_path = Path(output_dir)
            ensure_directory(output_path)
            
            # Calculate frame extraction parameters
            fps = video_info['fps']
            frame_interval = max(1, int(fps * interval))
            total_frames = video_info['frame_count']
            
            if max_frames is None:
                max_frames = min(self.max_frames_per_video, total_frames // frame_interval)
            else:
                max_frames = min(max_frames, self.max_frames_per_video)
            
            logger.info(f"Extracting frames from {video_path}")
            logger.info(f"Parameters - FPS: {fps:.1f}, Interval: {interval}s, Max frames: {max_frames}")
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ProcessingError(f"Failed to open video: {video_path}")
            
            frames_data = []
            frame_count = 0
            saved_count = 0
            failed_extractions = 0
            max_failed_extractions = 10
            
            try:
                while saved_count < max_frames and frame_count < total_frames:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Extract frame at specified interval
                    if frame_count % frame_interval == 0:
                        try:
                            # Validate frame
                            if frame is None or frame.size == 0:
                                failed_extractions += 1
                                logger.warning(f"Empty frame at position {frame_count}")
                                if failed_extractions >= max_failed_extractions:
                                    logger.error("Too many failed frame extractions")
                                    break
                                continue
                            
                            # Resize frame
                            resized_frame = self._resize_frame(frame)
                            if resized_frame is None:
                                failed_extractions += 1
                                continue
                            
                            # Save frame
                            filename = f"frame_{saved_count:04d}_{int(frame_count/fps)}s.jpg"
                            filepath = output_path / filename
                            
                            success = cv2.imwrite(str(filepath), resized_frame, 
                                                [cv2.IMWRITE_JPEG_QUALITY, self.quality])
                            
                            if not success:
                                failed_extractions += 1
                                logger.warning(f"Failed to save frame {saved_count}")
                                if failed_extractions >= max_failed_extractions:
                                    break
                                continue
                            
                            # Verify saved frame
                            if not filepath.exists() or filepath.stat().st_size == 0:
                                failed_extractions += 1
                                logger.warning(f"Saved frame is empty: {filepath}")
                                continue
                            
                            frames_data.append({
                                'path': str(filepath),
                                'frame_number': frame_count,
                                'timestamp': frame_count / fps,
                                'size_bytes': filepath.stat().st_size,
                                'resolution': f"{resized_frame.shape[1]}x{resized_frame.shape[0]}"
                            })
                            
                            saved_count += 1
                            failed_extractions = 0  # Reset counter on success
                            
                            # Log progress
                            if saved_count % 50 == 0:
                                logger.info(f"Extracted {saved_count} frames...")
                            
                        except Exception as e:
                            failed_extractions += 1
                            logger.error(f"Error processing frame {frame_count}: {e}")
                            if failed_extractions >= max_failed_extractions:
                                break
                    
                    frame_count += 1
                    
                    # Check timeout
                    if time.time() - start_time > self.frame_extraction_timeout:
                        logger.warning(f"Frame extraction timeout reached")
                        break
            
            finally:
                cap.release()
            
            # Update statistics
            processing_time = time.time() - start_time
            self.processing_stats['videos_processed'] += 1
            self.processing_stats['frames_extracted'] += saved_count
            self.processing_stats['total_processing_time'] += processing_time
            
            logger.info(f"Frame extraction completed: {saved_count} frames in {format_duration(processing_time)}")
            logger.info(f"Success rate: {saved_count}/{frame_count} frames")
            
            return frames_data
            
        except Exception as e:
            self.processing_stats['errors_encountered'] += 1
            logger.error(f"Error extracting frames from {video_path}: {e}", exc_info=True)
            raise ProcessingError(f"Failed to extract frames: {e}")
    
    def _resize_frame(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Resize frame with validation."""
        try:
            if frame is None or frame.size == 0:
                return None
            
            # Get current dimensions
            height, width = frame.shape[:2]
            
            # Skip resize if already correct size
            if width == self.resize_width and height == self.resize_height:
                return frame
            
            # Calculate aspect ratio preserving resize
            aspect_ratio = width / height
            target_aspect_ratio = self.resize_width / self.resize_height
            
            if abs(aspect_ratio - target_aspect_ratio) < 0.01:
                # Direct resize
                resized = cv2.resize(frame, (self.resize_width, self.resize_height), 
                                   interpolation=cv2.INTER_AREA)
            else:
                # Crop to maintain aspect ratio
                if aspect_ratio > target_aspect_ratio:
                    # Crop width
                    new_width = int(height * target_aspect_ratio)
                    start_x = (width - new_width) // 2
                    cropped = frame[:, start_x:start_x + new_width]
                else:
                    # Crop height
                    new_height = int(width / target_aspect_ratio)
                    start_y = (height - new_height) // 2
                    cropped = frame[start_y:start_y + new_height, :]
                
                resized = cv2.resize(cropped, (self.resize_width, self.resize_height), 
                                   interpolation=cv2.INTER_AREA)
            
            return resized
            
        except Exception as e:
            logger.error(f"Error resizing frame: {e}")
            return None
    
    def analyze_frame(self, frame_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a single frame with comprehensive error handling."""
        try:
            frame_file = Path(frame_path)
            
            # Validate frame file
            if not frame_file.exists():
                logger.warning(f"Frame file does not exist: {frame_path}")
                return None
            
            if not frame_file.is_file():
                logger.warning(f"Path is not a file: {frame_path}")
                return None
            
            # Load frame
            frame = cv2.imread(str(frame_file))
            if frame is None:
                logger.warning(f"Failed to load frame: {frame_path}")
                return None
            
            # Basic frame analysis
            height, width = frame.shape[:2]
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate various metrics
            brightness = float(gray.mean())
            contrast = float(gray.std())
            
            # Detect edges for activity analysis
            edges = cv2.Canny(gray, 50, 150)
            edge_density = float(np.sum(edges > 0) / (width * height))
            
            # Color analysis
            bgr_mean = np.mean(frame, axis=(0, 1))
            dominant_color = {
                'blue': float(bgr_mean[0]),
                'green': float(bgr_mean[1]),
                'red': float(bgr_mean[2])
            }
            
            # File information
            file_size = frame_file.stat().st_size
            
            analysis_result = {
                'path': frame_path,
                'resolution': f"{width}x{height}",
                'file_size_bytes': file_size,
                'brightness': brightness,
                'contrast': contrast,
                'edge_density': edge_density,
                'dominant_color': dominant_color,
                'activity_level': 'high' if edge_density > 0.1 else 'medium' if edge_density > 0.05 else 'low',
                'timestamp': time.time()
            }
            
            logger.debug(f"Frame analysis completed: {frame_path}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing frame {frame_path}: {e}")
            return None
    
    def batch_analyze_frames(self, frame_paths: List[str], max_workers: Optional[int] = None) -> List[Dict[str, Any]]:
        """Analyze multiple frames concurrently."""
        try:
            if not frame_paths:
                return []
            
            if max_workers is None:
                max_workers = min(self.max_concurrent_extractions, len(frame_paths))
            
            logger.info(f"Analyzing {len(frame_paths)} frames with {max_workers} workers")
            
            results = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_path = {
                    executor.submit(self.analyze_frame, path): path 
                    for path in frame_paths
                }
                
                # Collect results
                for future in as_completed(future_to_path):
                    path = future_to_path[future]
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                    except Exception as e:
                        logger.error(f"Error analyzing frame {path}: {e}")
            
            logger.info(f"Frame analysis completed: {len(results)}/{len(frame_paths)} successful")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch frame analysis: {e}")
            return []
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        try:
            avg_processing_time = 0
            if self.processing_stats['videos_processed'] > 0:
                avg_processing_time = (self.processing_stats['total_processing_time'] / 
                                     self.processing_stats['videos_processed'])
            
            return {
                'videos_processed': self.processing_stats['videos_processed'],
                'frames_extracted': self.processing_stats['frames_extracted'],
                'errors_encountered': self.processing_stats['errors_encountered'],
                'total_processing_time': self.processing_stats['total_processing_time'],
                'average_processing_time': avg_processing_time,
                'success_rate': (self.processing_stats['videos_processed'] - 
                               self.processing_stats['errors_encountered']) / 
                               max(1, self.processing_stats['videos_processed'])
            }
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {}
    
    def reset_stats(self) -> None:
        """Reset processing statistics."""
        try:
            self.processing_stats = {
                'videos_processed': 0,
                'frames_extracted': 0,
                'errors_encountered': 0,
                'total_processing_time': 0
            }
            logger.info("Processing statistics reset")
        except Exception as e:
            logger.error(f"Error resetting stats: {e}")
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            logger.info("VideoProcessor cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except:
            pass
