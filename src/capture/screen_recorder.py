"""Enhanced screen recording functionality with comprehensive error handling."""
import time
import os
import threading
import queue
import psutil
from typing import List, Dict, Optional, Tuple
import mss
import cv2
import numpy as np
from threading import Thread, Event, Lock
from ..error_handling.exceptions import RecordingError, StorageError
from ..error_handling.logger import logger


class ScreenRecorder:
    """Enhanced screen recorder with comprehensive error handling and edge case management."""
    
    def __init__(self, config, storage):
        self.config = config
        self.storage = storage
        self.fps = max(1, min(config.get('recording.fps', 1), 30))  # Clamp between 1-30 FPS
        self.screenshot_interval = max(1, config.get('recording.screenshot_interval_seconds', 5))
        self.is_recording = False
        self.stop_event = Event()
        self.recording_thread = None
        self.frames = []
        self.frame_lock = Lock()
        self.sct = None
        self.max_frames = config.get('recording.max_frames', 10000)  # Prevent memory overflow
        self.frame_queue = queue.Queue(maxsize=100)  # Buffer for frames
        self.monitor_info = None
        self.recording_start_time = None
        self.total_frames_captured = 0
        self.failed_captures = 0
        self.max_failed_captures = 10  # Stop if too many failures
        
    def _detect_monitors(self) -> List[Dict]:
        """Detect available monitors with error handling."""
        try:
            with mss.mss() as sct:
                monitors = []
                for i, monitor in enumerate(sct.monitors):
                    if i == 0:  # Skip the "All monitors" entry
                        continue
                    monitors.append({
                        'index': i,
                        'left': monitor['left'],
                        'top': monitor['top'],
                        'width': monitor['width'],
                        'height': monitor['height']
                    })
                logger.info(f"Detected {len(monitors)} monitors")
                return monitors
        except Exception as e:
            logger.error(f"Error detecting monitors: {e}")
            return []
    
    def _select_best_monitor(self) -> Optional[Dict]:
        """Select the best monitor for recording."""
        try:
            monitors = self._detect_monitors()
            if not monitors:
                logger.warning("No monitors detected")
                return None
            
            # Select primary monitor (usually the first one)
            primary_monitor = monitors[0]
            logger.info(f"Selected monitor: {primary_monitor['width']}x{primary_monitor['height']}")
            return primary_monitor
            
        except Exception as e:
            logger.error(f"Error selecting monitor: {e}")
            return None
    
    def _check_system_resources(self) -> bool:
        """Check if system has enough resources for recording."""
        try:
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
            
            logger.info(f"System resources OK - Memory: {memory.percent}%, CPU: {cpu_percent}%, Disk: {free_gb:.1f}GB")
            return True
            
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return False
    
    def start_recording(self, output_path: str) -> None:
        """Start screen recording with comprehensive error handling."""
        if self.is_recording:
            raise RecordingError("Recording already in progress")
        
        try:
            # Validate output path
            if not output_path:
                raise RecordingError("Output path is required")
            
            # Check system resources
            if not self._check_system_resources():
                raise RecordingError("Insufficient system resources for recording")
            
            # Select monitor
            self.monitor_info = self._select_best_monitor()
            if not self.monitor_info:
                raise RecordingError("No suitable monitor found for recording")
            
            # Initialize recording state
            self.is_recording = True
            self.stop_event.clear()
            self.frames = []
            self.output_path = output_path
            self.recording_start_time = time.time()
            self.total_frames_captured = 0
            self.failed_captures = 0
            
            # Clear frame queue
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break
            
            # Start recording thread
            self.recording_thread = Thread(target=self._record_loop, daemon=True)
            self.recording_thread.start()
            
            logger.info(f"Started screen recording: {output_path}")
            logger.info(f"Recording settings - FPS: {self.fps}, Monitor: {self.monitor_info['width']}x{self.monitor_info['height']}")
            
        except Exception as e:
            self.is_recording = False
            logger.error(f"Failed to start recording: {e}", exc_info=True)
            raise RecordingError(f"Failed to start recording: {e}")
    
    def stop_recording(self) -> Optional[str]:
        """Stop screen recording with comprehensive error handling."""
        if not self.is_recording:
            logger.warning("No recording in progress to stop")
            return None
        
        try:
            logger.info("Stopping screen recording...")
            
            # Signal stop
            self.stop_event.set()
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=10)  # Wait up to 10 seconds
                
                if self.recording_thread.is_alive():
                    logger.warning("Recording thread did not stop gracefully")
            
            # Process remaining frames in queue
            self._process_remaining_frames()
            
            # Save frames to video if we have any
            video_path = None
            if self.frames:
                video_path = self._save_video()
            
            # Log statistics
            duration = time.time() - self.recording_start_time if self.recording_start_time else 0
            logger.info(f"Recording stopped - Duration: {duration:.1f}s, Frames: {self.total_frames_captured}, Failed: {self.failed_captures}")
            
            self.is_recording = False
            return video_path
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}", exc_info=True)
            self.is_recording = False
            raise RecordingError(f"Failed to stop recording: {e}")
    
    def _record_loop(self) -> None:
        """Enhanced main recording loop with comprehensive error handling."""
        try:
            with mss.mss() as sct:
                self.sct = sct
                monitor = sct.monitors[self.monitor_info['index']]
                frame_count = 0
                last_frame_time = 0
                target_frame_time = 1.0 / self.fps
                
                logger.info("Recording loop started")
                
                while not self.stop_event.is_set():
                    try:
                        current_time = time.time()
                        
                        # Check if it's time for next frame
                        if current_time - last_frame_time < target_frame_time:
                            time.sleep(0.001)  # Small sleep to prevent busy waiting
                            continue
                        
                        # Check for too many failed captures
                        if self.failed_captures >= self.max_failed_captures:
                            logger.error(f"Too many failed captures ({self.failed_captures}), stopping recording")
                            break
                        
                        # Check memory usage periodically
                        if frame_count % 100 == 0:  # Check every 100 frames
                            memory = psutil.virtual_memory()
                            if memory.percent > 95:
                                logger.warning(f"Memory usage too high ({memory.percent}%), stopping recording")
                                break
                        
                        # Capture screenshot
                        screenshot = sct.grab(monitor)
                        if screenshot is None:
                            self.failed_captures += 1
                            logger.warning(f"Failed to capture screenshot (attempt {self.failed_captures})")
                            continue
                        
                        # Convert to numpy array
                        frame = np.array(screenshot)
                        if frame.size == 0:
                            self.failed_captures += 1
                            logger.warning(f"Empty frame captured (attempt {self.failed_captures})")
                            continue
                        
                        # Convert BGRA to BGR
                        if len(frame.shape) == 3 and frame.shape[2] == 4:
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        
                        # Add frame to queue
                        try:
                            self.frame_queue.put_nowait((frame, current_time))
                        except queue.Full:
                            logger.warning("Frame queue full, dropping frame")
                            continue
                        
                        # Process frames from queue
                        self._process_frame_queue()
                        
                        frame_count += 1
                        self.total_frames_captured += 1
                        last_frame_time = current_time
                        
                        # Log progress every 100 frames
                        if frame_count % 100 == 0:
                            logger.info(f"Captured {frame_count} frames")
                        
                    except Exception as e:
                        self.failed_captures += 1
                        logger.error(f"Error in recording loop iteration: {e}")
                        if self.failed_captures >= self.max_failed_captures:
                            break
                        time.sleep(0.1)  # Brief pause before retry
                
                logger.info("Recording loop ended")
                
        except Exception as e:
            logger.error(f"Error in recording loop: {e}", exc_info=True)
            self.failed_captures += 1
    
    def _process_frame_queue(self) -> None:
        """Process frames from the queue."""
        try:
            while not self.frame_queue.empty():
                try:
                    frame, timestamp = self.frame_queue.get_nowait()
                    
                    with self.frame_lock:
                        if len(self.frames) >= self.max_frames:
                            # Remove oldest frame to prevent memory overflow
                            self.frames.pop(0)
                        
                        self.frames.append({
                            'frame': frame,
                            'timestamp': timestamp,
                            'index': len(self.frames)
                        })
                        
                except queue.Empty:
                    break
                except Exception as e:
                    logger.error(f"Error processing frame: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing frame queue: {e}")
    
    def _process_remaining_frames(self) -> None:
        """Process any remaining frames in the queue."""
        try:
            logger.info("Processing remaining frames...")
            while not self.frame_queue.empty():
                self._process_frame_queue()
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
        except Exception as e:
            logger.error(f"Error processing remaining frames: {e}")
    
    def _save_video(self) -> Optional[str]:
        """Save frames to video file with comprehensive error handling."""
        if not self.frames:
            logger.warning("No frames to save")
            return None
        
        try:
            logger.info(f"Saving {len(self.frames)} frames to video...")
            
            # Get frame dimensions
            first_frame = self.frames[0]['frame']
            height, width = first_frame.shape[:2]
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                self.output_path,
                fourcc,
                self.fps,
                (width, height)
            )
            
            if not out.isOpened():
                raise RecordingError("Failed to initialize video writer")
            
            # Write frames
            frames_written = 0
            for frame_data in self.frames:
                try:
                    frame = frame_data['frame']
                    out.write(frame)
                    frames_written += 1
                except Exception as e:
                    logger.warning(f"Error writing frame {frame_data['index']}: {e}")
                    continue
            
            out.release()
            
            # Verify file was created and has content
            if not os.path.exists(self.output_path):
                raise RecordingError("Video file was not created")
            
            file_size = os.path.getsize(self.output_path)
            if file_size == 0:
                raise RecordingError("Video file is empty")
            
            logger.info(f"Video saved successfully: {self.output_path} ({file_size} bytes, {frames_written} frames)")
            return self.output_path
            
        except Exception as e:
            logger.error(f"Error saving video: {e}", exc_info=True)
            raise RecordingError(f"Failed to save video: {e}")
    
    def get_recording_stats(self) -> Dict:
        """Get current recording statistics."""
        try:
            duration = 0
            if self.recording_start_time:
                duration = time.time() - self.recording_start_time
            
            return {
                'is_recording': self.is_recording,
                'duration': duration,
                'total_frames': self.total_frames_captured,
                'failed_captures': self.failed_captures,
                'frames_in_memory': len(self.frames),
                'queue_size': self.frame_queue.qsize(),
                'fps': self.fps,
                'monitor_info': self.monitor_info
            }
        except Exception as e:
            logger.error(f"Error getting recording stats: {e}")
            return {}


class ScreenshotCapture:
    """Enhanced screenshot capture with comprehensive error handling and edge case management."""
    
    def __init__(self, config, storage):
        self.config = config
        self.storage = storage
        self.interval = max(1, config.get('recording.screenshot_interval_seconds', 5))
        self.is_capturing = False
        self.stop_event = Event()
        self.capture_thread = None
        self.screenshots = []
        self.screenshot_lock = Lock()
        self.max_screenshots = config.get('recording.max_screenshots', 1000)
        self.session_id = None
        self.capture_start_time = None
        self.total_captures = 0
        self.failed_captures = 0
        self.max_failed_captures = 20
        self.monitor_info = None
        self.sct = None
        
    def _detect_monitors(self) -> List[Dict]:
        """Detect available monitors."""
        try:
            with mss.mss() as sct:
                monitors = []
                for i, monitor in enumerate(sct.monitors):
                    if i == 0:  # Skip the "All monitors" entry
                        continue
                    monitors.append({
                        'index': i,
                        'left': monitor['left'],
                        'top': monitor['top'],
                        'width': monitor['width'],
                        'height': monitor['height']
                    })
                return monitors
        except Exception as e:
            logger.error(f"Error detecting monitors: {e}")
            return []
    
    def _select_best_monitor(self) -> Optional[Dict]:
        """Select the best monitor for capture."""
        try:
            monitors = self._detect_monitors()
            if not monitors:
                return None
            
            # Select primary monitor
            return monitors[0]
        except Exception as e:
            logger.error(f"Error selecting monitor: {e}")
            return None
    
    def _check_disk_space(self) -> bool:
        """Check if there's enough disk space for screenshots."""
        try:
            import shutil
            total, used, free = shutil.disk_usage('.')
            free_gb = free / (1024**3)
            
            # Estimate space needed (assuming 1MB per screenshot)
            estimated_needed = (self.max_screenshots * 1) / 1024  # MB to GB
            
            if free_gb < estimated_needed + 0.1:  # Need estimated space + 100MB buffer
                logger.warning(f"Insufficient disk space: {free_gb:.1f}GB available, need ~{estimated_needed:.1f}GB")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking disk space: {e}")
            return False
    
    def start_capture(self, session_id: str) -> None:
        """Start capturing screenshots with comprehensive error handling."""
        if self.is_capturing:
            raise RecordingError("Capture already in progress")
        
        try:
            # Validate session ID
            if not session_id:
                raise RecordingError("Session ID is required")
            
            # Check disk space
            if not self._check_disk_space():
                raise RecordingError("Insufficient disk space for screenshots")
            
            # Select monitor
            self.monitor_info = self._select_best_monitor()
            if not self.monitor_info:
                raise RecordingError("No suitable monitor found for capture")
            
            # Initialize capture state
            self.is_capturing = True
            self.stop_event.clear()
            self.screenshots = []
            self.session_id = session_id
            self.capture_start_time = time.time()
            self.total_captures = 0
            self.failed_captures = 0
            
            # Start capture thread
            self.capture_thread = Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            logger.info(f"Started screenshot capture for session: {session_id}")
            logger.info(f"Capture settings - Interval: {self.interval}s, Monitor: {self.monitor_info['width']}x{self.monitor_info['height']}")
            
        except Exception as e:
            self.is_capturing = False
            logger.error(f"Failed to start capture: {e}", exc_info=True)
            raise RecordingError(f"Failed to start capture: {e}")
    
    def stop_capture(self) -> List[Dict]:
        """Stop capturing screenshots and return captured data."""
        if not self.is_capturing:
            logger.warning("No capture in progress to stop")
            return []
        
        try:
            logger.info("Stopping screenshot capture...")
            
            # Signal stop
            self.stop_event.set()
            
            # Wait for capture thread to finish
            if self.capture_thread and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=10)
                
                if self.capture_thread.is_alive():
                    logger.warning("Capture thread did not stop gracefully")
            
            # Get final screenshots
            with self.screenshot_lock:
                screenshots_copy = self.screenshots.copy()
            
            # Log statistics
            duration = time.time() - self.capture_start_time if self.capture_start_time else 0
            logger.info(f"Capture stopped - Duration: {duration:.1f}s, Screenshots: {self.total_captures}, Failed: {self.failed_captures}")
            
            self.is_capturing = False
            return screenshots_copy
            
        except Exception as e:
            logger.error(f"Error stopping capture: {e}", exc_info=True)
            self.is_capturing = False
            return []
    
    def _capture_loop(self) -> None:
        """Enhanced main capture loop with comprehensive error handling."""
        try:
            with mss.mss() as sct:
                self.sct = sct
                monitor = sct.monitors[self.monitor_info['index']]
                counter = 0
                last_capture_time = 0
                
                logger.info("Capture loop started")
                
                while not self.stop_event.is_set():
                    try:
                        current_time = time.time()
                        
                        # Check if it's time for next capture
                        if current_time - last_capture_time < self.interval:
                            time.sleep(0.1)  # Small sleep to prevent busy waiting
                            continue
                        
                        # Check for too many failed captures
                        if self.failed_captures >= self.max_failed_captures:
                            logger.error(f"Too many failed captures ({self.failed_captures}), stopping capture")
                            break
                        
                        # Check if we've reached max screenshots
                        with self.screenshot_lock:
                            if len(self.screenshots) >= self.max_screenshots:
                                logger.warning(f"Maximum screenshots reached ({self.max_screenshots}), stopping capture")
                                break
                        
                        # Capture screenshot
                        screenshot = sct.grab(monitor)
                        if screenshot is None:
                            self.failed_captures += 1
                            logger.warning(f"Failed to capture screenshot (attempt {self.failed_captures})")
                            continue
                        
                        # Convert to numpy array
                        frame = np.array(screenshot)
                        if frame.size == 0:
                            self.failed_captures += 1
                            logger.warning(f"Empty frame captured (attempt {self.failed_captures})")
                            continue
                        
                        # Convert BGRA to BGR
                        if len(frame.shape) == 3 and frame.shape[2] == 4:
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        
                        # Save screenshot
                        filename = f"screenshot_{self.session_id}_{counter:04d}.png"
                        filepath = self.storage.get_temp_file_path(filename)
                        
                        try:
                            success = cv2.imwrite(filepath, frame)
                            if not success:
                                self.failed_captures += 1
                                logger.warning(f"Failed to save screenshot {filename}")
                                continue
                        except Exception as e:
                            self.failed_captures += 1
                            logger.warning(f"Error saving screenshot {filename}: {e}")
                            continue
                        
                        # Add to screenshots list
                        screenshot_data = {
                            'path': filepath,
                            'timestamp': current_time,
                            'index': counter,
                            'filename': filename,
                            'size': os.path.getsize(filepath) if os.path.exists(filepath) else 0
                        }
                        
                        with self.screenshot_lock:
                            self.screenshots.append(screenshot_data)
                        
                        counter += 1
                        self.total_captures += 1
                        last_capture_time = current_time
                        
                        # Log progress every 50 screenshots
                        if counter % 50 == 0:
                            logger.info(f"Captured {counter} screenshots")
                        
                    except Exception as e:
                        self.failed_captures += 1
                        logger.error(f"Error in capture loop iteration: {e}")
                        if self.failed_captures >= self.max_failed_captures:
                            break
                        time.sleep(0.5)  # Longer pause before retry
                
                logger.info("Capture loop ended")
                
        except Exception as e:
            logger.error(f"Error in capture loop: {e}", exc_info=True)
            self.failed_captures += 1
    
    def get_capture_stats(self) -> Dict:
        """Get current capture statistics."""
        try:
            duration = 0
            if self.capture_start_time:
                duration = time.time() - self.capture_start_time
            
            with self.screenshot_lock:
                screenshots_count = len(self.screenshots)
            
            return {
                'is_capturing': self.is_capturing,
                'duration': duration,
                'total_captures': self.total_captures,
                'failed_captures': self.failed_captures,
                'screenshots_in_memory': screenshots_count,
                'interval': self.interval,
                'session_id': self.session_id,
                'monitor_info': self.monitor_info
            }
        except Exception as e:
            logger.error(f"Error getting capture stats: {e}")
            return {}
