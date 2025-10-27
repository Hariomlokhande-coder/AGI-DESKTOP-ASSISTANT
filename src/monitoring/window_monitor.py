"""
Real-time window monitoring system for tracking active applications.
"""

import time
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime
import threading
import psutil
import win32gui
import win32process
import win32con
from ctypes import windll

try:
    from error_handling.simple_logger import logger
except ImportError:
    from src.error_handling.simple_logger import logger


class WindowMonitor:
    """Monitor active windows and application switches in real-time."""
    
    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback
        self.running = False
        self.current_window = None
        self.window_history = []
        self.monitor_thread = None
        self.last_check_time = 0
        self.check_interval = 0.5  # Check every 500ms
        
        # Application name mappings
        self.app_mappings = {
            'excel.exe': 'Microsoft Excel',
            'winword.exe': 'Microsoft Word',
            'chrome.exe': 'Google Chrome',
            'firefox.exe': 'Mozilla Firefox',
            'msedge.exe': 'Microsoft Edge',
            'notepad.exe': 'Notepad',
            'notepad++.exe': 'Notepad++',
            'code.exe': 'Visual Studio Code',
            'devenv.exe': 'Visual Studio',
            'outlook.exe': 'Microsoft Outlook',
            'teams.exe': 'Microsoft Teams',
            'explorer.exe': 'File Explorer',
            'calc.exe': 'Calculator',
            'mspaint.exe': 'Paint',
            'powershell.exe': 'PowerShell',
            'cmd.exe': 'Command Prompt'
        }
        
        logger.info("WindowMonitor initialized")
    
    def start_monitoring(self):
        """Start the window monitoring in a separate thread."""
        if self.running:
            logger.warning("Window monitoring is already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Window monitoring started")
    
    def stop_monitoring(self):
        """Stop the window monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        logger.info("Window monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                current_time = time.time()
                if current_time - self.last_check_time >= self.check_interval:
                    self._check_window_change()
                    self.last_check_time = current_time
                time.sleep(0.1)  # Small sleep to prevent excessive CPU usage
            except Exception as e:
                logger.error(f"Error in window monitoring loop: {e}")
                time.sleep(1)
    
    def _check_window_change(self):
        """Check if the active window has changed."""
        try:
            # Get the currently active window
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return
            
            # Get window title and process info
            window_title = win32gui.GetWindowText(hwnd)
            if not window_title:
                return
            
            # Get process information
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                process_name = process.name().lower()
                process_path = process.exe()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "unknown"
                process_path = "unknown"
            
            # Map process name to application name
            app_name = self.app_mappings.get(process_name, process_name.title())
            
            # Create window info
            window_info = {
                'hwnd': hwnd,
                'title': window_title,
                'process_name': process_name,
                'app_name': app_name,
                'process_path': process_path,
                'timestamp': datetime.now(),
                'pid': pid
            }
            
            # Check if window has changed
            if self.current_window is None or self._is_different_window(window_info):
                self._handle_window_change(window_info)
                self.current_window = window_info
                
        except Exception as e:
            logger.error(f"Error checking window change: {e}")
    
    def _is_different_window(self, new_window: Dict) -> bool:
        """Check if the new window is different from current."""
        if not self.current_window:
            return True
        
        # Compare by hwnd (most reliable)
        if new_window['hwnd'] != self.current_window['hwnd']:
            return True
        
        # Also compare title in case window content changed significantly
        if new_window['title'] != self.current_window['title']:
            return True
        
        return False
    
    def _handle_window_change(self, window_info: Dict):
        """Handle a window change event."""
        try:
            # Add to history
            self.window_history.append(window_info)
            
            # Keep only last 100 windows in history
            if len(self.window_history) > 100:
                self.window_history = self.window_history[-100:]
            
            # Log the window change - detailed label
            timestamp = window_info['timestamp'].strftime("%H:%M:%S")
            app_name = window_info['app_name']
            window_title = window_info['title']
            
            # Determine if this is opening a new app or switching
            is_new_app = self._is_new_app(window_info)
            action_label = f"[APP OPENED] Opened {app_name}" if is_new_app else f"[APP SWITCHED] Switched to {app_name}"
            
            logger.info(f"{action_label} - {window_title} ({timestamp})")
            
            # Call callback if provided
            if self.callback:
                self.callback(window_info)
                
        except Exception as e:
            logger.error(f"Error handling window change: {e}")
    
    def _is_new_app(self, window_info: Dict) -> bool:
        """Check if this is a new app (not previously seen recently)."""
        if not self.window_history or len(self.window_history) <= 1:
            return True
        
        # Check last few windows
        recent_count = min(5, len(self.window_history) - 1)
        current_app = window_info['app_name']
        
        for i in range(-recent_count, 0):
            if self.window_history[i]['app_name'] == current_app:
                return False
        
        return True
    
    def get_current_window(self) -> Optional[Dict]:
        """Get information about the current active window."""
        return self.current_window
    
    def get_window_history(self, limit: int = 10) -> List[Dict]:
        """Get recent window history."""
        return self.window_history[-limit:] if self.window_history else []
    
    def get_application_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics for different applications."""
        stats = {}
        for window in self.window_history:
            app_name = window['app_name']
            stats[app_name] = stats.get(app_name, 0) + 1
        return stats
    
    def is_window_visible(self, hwnd: int) -> bool:
        """Check if a window is visible."""
        try:
            return win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != ""
        except:
            return False
    
    def get_window_rect(self, hwnd: int) -> Optional[tuple]:
        """Get window rectangle coordinates."""
        try:
            return win32gui.GetWindowRect(hwnd)
        except:
            return None
    
    def bring_window_to_front(self, hwnd: int):
        """Bring a window to the front."""
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            logger.error(f"Error bringing window to front: {e}")


class WindowCapture:
    """Capture screenshots of specific windows."""
    
    def __init__(self):
        self.capture_count = 0
        logger.info("WindowCapture initialized")
    
    def capture_window(self, hwnd: int, save_path: Optional[str] = None) -> Optional[str]:
        """Capture a screenshot of the specified window."""
        try:
            import mss
            import mss.windows
            
            # Get window rectangle
            rect = win32gui.GetWindowRect(hwnd)
            if not rect:
                return None
            
            x, y, x2, y2 = rect
            width = x2 - x
            height = y2 - y
            
            # Skip if window is too small
            if width < 100 or height < 100:
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
                
                # Save screenshot
                if save_path is None:
                    self.capture_count += 1
                    save_path = f"screenshot_{self.capture_count}_{int(time.time())}.png"
                
                # Convert to PIL Image and save
                from PIL import Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                img.save(save_path)
                
                logger.info(f"Window screenshot saved: {save_path}")
                return save_path
                
        except Exception as e:
            logger.error(f"Error capturing window: {e}")
            return None
    
    def capture_active_window(self, save_path: Optional[str] = None) -> Optional[str]:
        """Capture the currently active window."""
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            return self.capture_window(hwnd, save_path)
        return None
