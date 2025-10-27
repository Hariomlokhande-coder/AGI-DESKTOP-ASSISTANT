"""
Screenshot capture system for OCR analysis and workflow monitoring.
"""

import time
import os
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime
import threading
import queue
from pathlib import Path

try:
    import mss
    import mss.windows
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

from PIL import Image
import numpy as np

try:
    from error_handling.simple_logger import logger
except ImportError:
    from src.error_handling.simple_logger import logger


class ScreenshotCapture:
    """Capture screenshots for OCR analysis and workflow monitoring."""
    
    def __init__(self, output_dir: str = "screenshots", callback: Optional[Callable] = None):
        self.output_dir = Path(output_dir)
        self.callback = callback
        self.capture_count = 0
        self.captures = []
        self.capture_queue = queue.Queue()
        self.processing_thread = None
        self.running = False
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Capture settings
        self.max_captures = 1000  # Maximum number of captures to keep in memory
        self.capture_interval = 1.0  # Minimum interval between captures
        self.last_capture_time = 0
        
        # Image quality settings
        self.image_quality = 85
        self.max_image_size = (1920, 1080)  # Resize large images
        
        logger.info(f"ScreenshotCapture initialized with output dir: {self.output_dir}")
    
    def start_capture_service(self):
        """Start the background capture processing service."""
        if self.running:
            logger.warning("Screenshot capture service is already running")
            return
        
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_capture_queue, daemon=True)
        self.processing_thread.start()
        logger.info("Screenshot capture service started")
    
    def stop_capture_service(self):
        """Stop the background capture processing service."""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=2)
        logger.info("Screenshot capture service stopped")
    
    def capture_active_window(self, save_to_disk: bool = True) -> Optional[Dict]:
        """Capture the currently active window."""
        if not WIN32_AVAILABLE:
            logger.error("win32gui not available for window capture")
            return None
        
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None
            
            return self.capture_window(hwnd, save_to_disk)
        except Exception as e:
            logger.error(f"Error capturing active window: {e}")
            return None
    
    def capture_window(self, hwnd: int, save_to_disk: bool = True) -> Optional[Dict]:
        """Capture a specific window by handle."""
        if not WIN32_AVAILABLE or not MSS_AVAILABLE:
            logger.error("Required libraries not available for window capture")
            return None
        
        try:
            # Get window rectangle
            rect = win32gui.GetWindowRect(hwnd)
            if not rect:
                return None
            
            x, y, x2, y2 = rect
            width = x2 - x
            height = y2 - y
            
            # Skip if window is too small or invalid
            if width < 50 or height < 50:
                return None
            
            # Check capture interval
            current_time = time.time()
            if current_time - self.last_capture_time < self.capture_interval:
                return None
            
            # Capture screenshot
            with mss.mss() as sct:
                monitor = {
                    "top": y,
                    "left": x,
                    "width": width,
                    "height": height
                }
                
                screenshot = sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Resize if too large
                if img.size[0] > self.max_image_size[0] or img.size[1] > self.max_image_size[1]:
                    img.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
                
                # Create capture info
                capture_info = {
                    'hwnd': hwnd,
                    'timestamp': datetime.now(),
                    'time': current_time,
                    'size': img.size,
                    'rect': rect,
                    'window_title': win32gui.GetWindowText(hwnd),
                    'image': img,
                    'saved': False
                }
                
                # Save to disk if requested
                if save_to_disk:
                    filename = self._generate_filename(capture_info)
                    filepath = self.output_dir / filename
                    
                    # Save image
                    img.save(filepath, 'PNG', quality=self.image_quality)
                    capture_info['filepath'] = str(filepath)
                    capture_info['saved'] = True
                    
                    logger.info(f"Screenshot saved: {filename}")
                
                # Add to captures
                self._add_capture(capture_info)
                self.last_capture_time = current_time
                
                # Call callback
                if self.callback:
                    self.callback(capture_info)
                
                return capture_info
                
        except Exception as e:
            logger.error(f"Error capturing window {hwnd}: {e}")
            return None
    
    def capture_full_screen(self, save_to_disk: bool = True) -> Optional[Dict]:
        """Capture the full screen."""
        if not MSS_AVAILABLE:
            logger.error("mss not available for screen capture")
            return None
        
        try:
            current_time = time.time()
            
            # Check capture interval
            if current_time - self.last_capture_time < self.capture_interval:
                return None
            
            with mss.mss() as sct:
                # Get the primary monitor
                monitor = sct.monitors[1]  # Index 0 is all monitors, 1 is primary
                
                screenshot = sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Resize if too large
                if img.size[0] > self.max_image_size[0] or img.size[1] > self.max_image_size[1]:
                    img.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
                
                # Create capture info
                capture_info = {
                    'hwnd': None,
                    'timestamp': datetime.now(),
                    'time': current_time,
                    'size': img.size,
                    'rect': (monitor['left'], monitor['top'], monitor['width'], monitor['height']),
                    'window_title': 'Full Screen',
                    'image': img,
                    'saved': False
                }
                
                # Save to disk if requested
                if save_to_disk:
                    filename = self._generate_filename(capture_info)
                    filepath = self.output_dir / filename
                    
                    # Save image
                    img.save(filepath, 'PNG', quality=self.image_quality)
                    capture_info['filepath'] = str(filepath)
                    capture_info['saved'] = True
                    
                    logger.info(f"Full screen screenshot saved: {filename}")
                
                # Add to captures
                self._add_capture(capture_info)
                self.last_capture_time = current_time
                
                # Call callback
                if self.callback:
                    self.callback(capture_info)
                
                return capture_info
                
        except Exception as e:
            logger.error(f"Error capturing full screen: {e}")
            return None
    
    def capture_window_async(self, hwnd: int, save_to_disk: bool = True):
        """Queue a window capture for background processing."""
        if not self.running:
            self.start_capture_service()
        
        capture_request = {
            'type': 'window',
            'hwnd': hwnd,
            'save_to_disk': save_to_disk,
            'timestamp': datetime.now()
        }
        
        self.capture_queue.put(capture_request)
    
    def capture_full_screen_async(self, save_to_disk: bool = True):
        """Queue a full screen capture for background processing."""
        if not self.running:
            self.start_capture_service()
        
        capture_request = {
            'type': 'full_screen',
            'save_to_disk': save_to_disk,
            'timestamp': datetime.now()
        }
        
        self.capture_queue.put(capture_request)
    
    def _process_capture_queue(self):
        """Process the capture queue in background thread."""
        while self.running:
            try:
                # Get capture request with timeout
                try:
                    request = self.capture_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process the request
                if request['type'] == 'window':
                    self.capture_window(request['hwnd'], request['save_to_disk'])
                elif request['type'] == 'full_screen':
                    self.capture_full_screen(request['save_to_disk'])
                
                self.capture_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing capture queue: {e}")
                time.sleep(1)
    
    def _generate_filename(self, capture_info: Dict) -> str:
        """Generate filename for screenshot."""
        self.capture_count += 1
        timestamp = capture_info['timestamp'].strftime("%Y%m%d_%H%M%S")
        window_title = capture_info['window_title'].replace(' ', '_').replace('\\', '_').replace('/', '_')
        window_title = ''.join(c for c in window_title if c.isalnum() or c in '_-')[:30]
        
        return f"screenshot_{self.capture_count}_{timestamp}_{window_title}.png"
    
    def _add_capture(self, capture_info: Dict):
        """Add capture to the list."""
        self.captures.append(capture_info)
        
        # Keep only recent captures
        if len(self.captures) > self.max_captures:
            # Remove oldest capture
            old_capture = self.captures.pop(0)
            
            # Clean up old image from memory
            if 'image' in old_capture:
                del old_capture['image']
    
    def get_recent_captures(self, limit: int = 10) -> List[Dict]:
        """Get recent captures."""
        return self.captures[-limit:] if self.captures else []
    
    def get_capture_by_timestamp(self, timestamp: datetime) -> Optional[Dict]:
        """Get capture by timestamp."""
        for capture in self.captures:
            if capture['timestamp'] == timestamp:
                return capture
        return None
    
    def cleanup_old_captures(self, max_age_hours: int = 24):
        """Clean up old capture files."""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            cleaned_count = 0
            for capture in self.captures[:]:
                if current_time - capture['time'] > max_age_seconds:
                    # Remove from memory
                    self.captures.remove(capture)
                    
                    # Delete file if it exists
                    if capture.get('saved') and 'filepath' in capture:
                        try:
                            os.remove(capture['filepath'])
                            cleaned_count += 1
                        except OSError:
                            pass
                    
                    # Clean up image from memory
                    if 'image' in capture:
                        del capture['image']
            
            logger.info(f"Cleaned up {cleaned_count} old captures")
            
        except Exception as e:
            logger.error(f"Error cleaning up old captures: {e}")
    
    def get_capture_stats(self) -> Dict:
        """Get capture statistics."""
        if not self.captures:
            return {'total_captures': 0, 'total_size': 0, 'avg_size': 0}
        
        total_size = sum(capture['size'][0] * capture['size'][1] for capture in self.captures)
        avg_size = total_size / len(self.captures) if self.captures else 0
        
        return {
            'total_captures': len(self.captures),
            'total_size': total_size,
            'avg_size': avg_size,
            'capture_count': self.capture_count
        }
    
    def clear_captures(self):
        """Clear all captures from memory."""
        for capture in self.captures:
            if 'image' in capture:
                del capture['image']
        
        self.captures.clear()
        logger.info("All captures cleared from memory")


class WorkflowAnalyzer:
    """Analyze captured screenshots for workflow patterns."""
    
    def __init__(self, ocr_analyzer=None):
        self.ocr_analyzer = ocr_analyzer
        self.workflow_patterns = []
        self.analysis_cache = {}
        
        logger.info("WorkflowAnalyzer initialized")
    
    def analyze_capture(self, capture_info: Dict) -> Dict:
        """Analyze a captured screenshot for workflow patterns."""
        try:
            if not capture_info.get('image'):
                return {'error': 'No image data available'}
            
            # Check cache first
            cache_key = f"{capture_info['timestamp']}_{capture_info['size']}"
            if cache_key in self.analysis_cache:
                return self.analysis_cache[cache_key]
            
            # Perform OCR analysis if available
            ocr_result = None
            if self.ocr_analyzer and capture_info.get('saved'):
                ocr_result = self.ocr_analyzer.analyze_screenshot(capture_info['filepath'])
            
            # Analyze workflow patterns
            workflow_analysis = {
                'timestamp': capture_info['timestamp'],
                'window_title': capture_info['window_title'],
                'size': capture_info['size'],
                'ocr_result': ocr_result,
                'workflow_indicators': self._detect_workflow_indicators(capture_info, ocr_result),
                'action_suggestions': self._suggest_actions(capture_info, ocr_result)
            }
            
            # Cache result
            self.analysis_cache[cache_key] = workflow_analysis
            
            return workflow_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing capture: {e}")
            return {'error': str(e)}
    
    def _detect_workflow_indicators(self, capture_info: Dict, ocr_result: Optional[Dict]) -> List[str]:
        """Detect workflow indicators from the capture."""
        indicators = []
        
        # Basic window analysis
        window_title = capture_info['window_title'].lower()
        
        if 'excel' in window_title:
            indicators.append('spreadsheet_work')
        elif 'word' in window_title:
            indicators.append('document_work')
        elif 'chrome' in window_title or 'firefox' in window_title or 'edge' in window_title:
            indicators.append('web_browsing')
        elif 'notepad' in window_title:
            indicators.append('text_editing')
        elif 'explorer' in window_title:
            indicators.append('file_management')
        
        # OCR-based analysis
        if ocr_result and 'application' in ocr_result:
            app_name = ocr_result['application'].get('name', '')
            if app_name:
                indicators.append(f'app_{app_name}')
            
            # Detect specific activities
            if 'detected_tasks' in ocr_result:
                for task in ocr_result['detected_tasks']:
                    indicators.append(f'task_{task.get("name", "")}')
        
        return indicators
    
    def _suggest_actions(self, capture_info: Dict, ocr_result: Optional[Dict]) -> List[str]:
        """Suggest possible actions based on the capture."""
        suggestions = []
        
        window_title = capture_info['window_title'].lower()
        
        if 'excel' in window_title:
            suggestions.extend(['data_entry', 'formula_creation', 'chart_creation'])
        elif 'word' in window_title:
            suggestions.extend(['text_editing', 'formatting', 'document_review'])
        elif 'chrome' in window_title or 'firefox' in window_title:
            suggestions.extend(['web_search', 'url_navigation', 'form_filling'])
        elif 'notepad' in window_title:
            suggestions.extend(['text_editing', 'note_taking', 'code_writing'])
        
        return suggestions
