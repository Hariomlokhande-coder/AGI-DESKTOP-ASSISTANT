"""
Real-time terminal logger with action labels and workflow tracking.
"""

import time
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import threading
import queue
from collections import deque
import sys
import os

try:
    from error_handling.simple_logger import logger
except ImportError:
    from src.error_handling.simple_logger import logger


class RealTimeLogger:
    """Real-time terminal logger with action labels and workflow tracking."""
    
    def __init__(self, 
                 log_to_file: bool = True, 
                 log_file: str = "workflow_log.txt",
                 max_display_lines: int = 50):
        self.log_to_file = log_to_file
        self.log_file = log_file
        self.max_display_lines = max_display_lines
        
        # Log storage
        self.log_entries = deque(maxlen=1000)  # Keep last 1000 entries
        self.display_queue = queue.Queue()
        self.running = False
        self.display_thread = None
        
        # Action labels and formatting
        self.action_labels = {
            'app_opened': '[App Opened]',
            'app_switched': '[App Switched]',
            'typed': '[Typed]',
            'saved_file': '[Saved File]',
            'opened_file': '[Opened File]',
            'closed_file': '[Closed File]',
            'browsed_url': '[Browsed URL]',
            'searched': '[Search]',
            'calculated': '[Calculation]',
            'formatted': '[Format]',
            'copied': '[Copy]',
            'pasted': '[Paste]',
            'cut': '[Cut]',
            'undo': '[Undo]',
            'redo': '[Redo]',
            'email': '[Email]',
            'message': '[Message]',
            'chat': '[Chat]',
            'meeting': '[Meeting]',
            'system': '[System]',
            'unknown': '[Action]'
        }
        
        # Color codes for terminal output
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m'
        }
        
        # Category colors
        self.category_colors = {
            'app_switching': 'blue',
            'typing': 'green',
            'file_operations': 'yellow',
            'navigation': 'cyan',
            'editing': 'magenta',
            'calculation': 'red',
            'communication': 'white',
            'system': 'dim',
            'unknown': 'dim'
        }
        
        # Setup file logging if enabled
        if self.log_to_file:
            self._setup_file_logging()
        
        logger.info("RealTimeLogger initialized")
    
    def start_logging(self):
        """Start the real-time logging system."""
        if self.running:
            logger.warning("Real-time logging is already running")
            return
        
        self.running = True
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
        
        # Log startup message
        self.log_action('system', 'Real-time logging started', {'app_name': 'System'})
        logger.info("Real-time logging started")
    
    def stop_logging(self):
        """Stop the real-time logging system."""
        self.running = False
        if self.display_thread:
            self.display_thread.join(timeout=1)
        
        # Log shutdown message
        self.log_action('system', 'Real-time logging stopped', {'app_name': 'System'})
        logger.info("Real-time logging stopped")
    
    def log_action(self, 
                   action_type: str, 
                   content: str, 
                   metadata: Optional[Dict] = None,
                   category: Optional[str] = None,
                   confidence: Optional[float] = None):
        """Log an action with proper formatting and labels."""
        try:
            timestamp = datetime.now()
            
            # Create log entry
            log_entry = {
                'timestamp': timestamp,
                'action_type': action_type,
                'content': content,
                'metadata': metadata or {},
                'category': category or 'unknown',
                'confidence': confidence or 0.0,
                'formatted': self._format_log_entry(action_type, content, timestamp, metadata, category)
            }
            
            # Add to log entries
            self.log_entries.append(log_entry)
            
            # Add to display queue
            self.display_queue.put(log_entry)
            
            # Write to file if enabled
            if self.log_to_file:
                self._write_to_file(log_entry)
            
        except Exception as e:
            logger.error(f"Error logging action: {e}")
    
    def log_window_change(self, window_info: Dict):
        """Log a window change event."""
        app_name = window_info.get('app_name', 'Unknown App')
        window_title = window_info.get('title', 'Unknown Window')
        timestamp = window_info.get('timestamp', datetime.now())
        
        # Determine if this is a new app or window switch
        if self._is_new_app(window_info):
            action_type = 'app_opened'
        else:
            action_type = 'app_switched'
        
        # Create content preview
        content = f"{app_name} - {window_title}"
        
        # Log the action
        self.log_action(
            action_type=action_type,
            content=content,
            metadata={
                'app_name': app_name,
                'window_title': window_title,
                'process_name': window_info.get('process_name', ''),
                'pid': window_info.get('pid', 0)
            },
            category='app_switching'
        )
    
    def log_keyboard_action(self, key_event: Dict):
        """Log a keyboard action event."""
        action_type = key_event.get('type', 'unknown')
        key = key_event.get('key', '')
        content = key_event.get('content', '')
        timestamp = key_event.get('timestamp', datetime.now())
        
        # Determine action type
        if action_type == 'typing':
            log_action_type = 'typed'
            category = 'typing'
        elif action_type == 'action':
            action = key_event.get('action', 'unknown')
            log_action_type = self._map_keyboard_action(action)
            category = 'editing'
        else:
            log_action_type = 'unknown'
            category = 'unknown'
        
        # Create content
        if content:
            display_content = f"{log_action_type}: {content[:100]}"
        else:
            display_content = f"{log_action_type}: {key}"
        
        # Log the action
        self.log_action(
            action_type=log_action_type,
            content=display_content,
            metadata={
                'key': key,
                'action': key_event.get('action', ''),
                'combo': key_event.get('combo', ''),
                'modifiers': key_event.get('modifiers', set())
            },
            category=category,
            confidence=key_event.get('confidence', 0.0)
        )
    
    def log_ocr_analysis(self, analysis_result: Dict, screenshot_path: str):
        """Log OCR analysis results."""
        try:
            app_info = analysis_result.get('application', {})
            app_name = app_info.get('name', 'Unknown')
            confidence = analysis_result.get('confidence', 0.0)
            
            # Get detected tasks
            tasks = analysis_result.get('detected_tasks', [])
            if tasks:
                task_names = [task.get('name', '') for task in tasks]
                content = f"OCR detected in {app_name}: {', '.join(task_names)}"
            else:
                content = f"OCR analysis completed for {app_name}"
            
            # Log the action
            self.log_action(
                action_type='ocr_analysis',
                content=content,
                metadata={
                    'app_name': app_name,
                    'confidence': confidence,
                    'tasks': tasks,
                    'screenshot_path': screenshot_path,
                    'ui_elements': analysis_result.get('ui_elements', {}),
                    'raw_text_length': len(analysis_result.get('raw_text', ''))
                },
                category='system',
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error logging OCR analysis: {e}")
    
    def _format_log_entry(self, 
                         action_type: str, 
                         content: str, 
                         timestamp: datetime,
                         metadata: Optional[Dict] = None,
                         category: Optional[str] = None) -> str:
        """Format a log entry for display."""
        try:
            # Get action label with better formatting
            action_label = self.action_labels.get(action_type, f'[{action_type.upper().replace("_", " ")}]')
            
            # Get color for category
            color = self.category_colors.get(category or 'unknown', 'white')
            color_code = self.colors.get(color, '')
            reset_code = self.colors['reset']
            bold_code = self.colors['bold']
            
            # Format timestamp
            time_str = timestamp.strftime("%H:%M:%S")
            
            # Get app name from metadata if available
            app_name = metadata.get('app_name', '') if metadata else ''
            
            # Create enhanced content display
            if app_name and app_name != 'Unknown':
                # Show app-specific actions with detailed labels
                display_content = self._create_detailed_content(action_type, content, app_name, metadata)
            else:
                display_content = content
            
            # Format content (truncate if too long but preserve important info)
            if len(display_content) > 100:
                display_content = display_content[:97] + "..."
            
            # Create formatted line with better visual separation
            formatted = f"{color_code}{bold_code}{action_label}{reset_code} {color_code}{display_content}{reset_code} {self.colors['dim']}({time_str}){reset_code}"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting log entry: {e}")
            return f"[{action_type}] {content} ({timestamp.strftime('%H:%M:%S')})"
    
    def _create_detailed_content(self, action_type: str, content: str, app_name: str, metadata: Optional[Dict]) -> str:
        """Create detailed content with app-specific descriptions."""
        try:
            # Get window title if available
            window_title = metadata.get('window_title', '') if metadata else ''
            
            # Create app-specific detailed labels
            if action_type == 'app_opened':
                return f"Opened {app_name} - {window_title}" if window_title else f"Opened {app_name}"
            elif action_type == 'app_switched':
                return f"Switched to {app_name} - {window_title}" if window_title else f"Switched to {app_name}"
            elif action_type == 'typed':
                # For typing, show the app and brief content
                preview = content[:50] if len(content) <= 50 else content[:47] + "..."
                return f"Typing in {app_name}: {preview}"
            elif action_type in ['copied', 'pasted', 'cut']:
                return f"{action_type.title().replace('_', ' ')} in {app_name}"
            elif action_type == 'saved_file':
                return f"Saved file in {app_name}"
            elif action_type == 'opened_file':
                return f"Opened file in {app_name}"
            elif action_type == 'closed_file':
                return f"Closed file in {app_name}"
            elif action_type == 'browsed_url':
                return f"Browsed URL in {app_name}: {content}"
            elif action_type in ['searched', 'found']:
                return f"Searched in {app_name}: {content}"
            else:
                # Generic format with app name
                return f"{app_name}: {content}"
                
        except Exception as e:
            logger.error(f"Error creating detailed content: {e}")
            return content
    
    def _map_keyboard_action(self, action: str) -> str:
        """Map keyboard action to log action type."""
        action_mapping = {
            'save': 'saved_file',
            'open': 'opened_file',
            'close': 'closed_file',
            'copy': 'copied',
            'paste': 'pasted',
            'cut': 'cut',
            'undo': 'undo',
            'redo': 'redo',
            'find': 'searched',
            'search': 'searched',
            'print': 'system'
        }
        return action_mapping.get(action, 'unknown')
    
    def _is_new_app(self, window_info: Dict) -> bool:
        """Check if this is a new app (not just a window switch)."""
        if not self.log_entries:
            return True
        
        # Check last few entries for the same app
        recent_entries = list(self.log_entries)[-5:]
        current_app = window_info.get('app_name', '')
        
        for entry in recent_entries:
            if entry['metadata'].get('app_name') == current_app:
                return False
        
        return True
    
    def _display_loop(self):
        """Main display loop for real-time output."""
        while self.running:
            try:
                # Get log entry from queue
                try:
                    log_entry = self.display_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Display the log entry
                self._display_log_entry(log_entry)
                
            except Exception as e:
                logger.error(f"Error in display loop: {e}")
                time.sleep(1)
    
    def _display_log_entry(self, log_entry: Dict):
        """Display a single log entry."""
        try:
            # Print to console immediately with flush
            print(log_entry['formatted'])
            sys.stdout.flush()  # Force immediate output
            
            # Don't clear screen - let the log scroll naturally
            
        except Exception as e:
            logger.error(f"Error displaying log entry: {e}")
    
    def _display_recent_entries(self, count: int = None):
        """Display recent log entries."""
        if count is None:
            count = self.max_display_lines
        
        recent_entries = list(self.log_entries)[-count:]
        
        for entry in recent_entries:
            print(entry['formatted'])
    
    def _setup_file_logging(self):
        """Setup file logging."""
        try:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Write header to log file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"Workflow Log - Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n")
                
        except Exception as e:
            logger.error(f"Error setting up file logging: {e}")
    
    def _write_to_file(self, log_entry: Dict):
        """Write log entry to file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                # Write detailed log entry
                f.write(f"{log_entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | ")
                f.write(f"{log_entry['action_type']} | ")
                f.write(f"{log_entry['category']} | ")
                f.write(f"{log_entry['content']}\n")
                
                # Write metadata if present
                if log_entry['metadata']:
                    f.write(f"  Metadata: {log_entry['metadata']}\n")
                
                f.write("\n")
                
        except Exception as e:
            logger.error(f"Error writing to log file: {e}")
    
    def get_recent_entries(self, count: int = 20) -> List[Dict]:
        """Get recent log entries."""
        return list(self.log_entries)[-count:] if self.log_entries else []
    
    def get_entries_by_category(self, category: str, count: int = 20) -> List[Dict]:
        """Get log entries by category."""
        filtered_entries = [
            entry for entry in self.log_entries
            if entry['category'] == category
        ]
        return filtered_entries[-count:] if filtered_entries else []
    
    def get_entries_by_app(self, app_name: str, count: int = 20) -> List[Dict]:
        """Get log entries by app name."""
        filtered_entries = [
            entry for entry in self.log_entries
            if entry['metadata'].get('app_name') == app_name
        ]
        return filtered_entries[-count:] if filtered_entries else []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        if not self.log_entries:
            return {'total_entries': 0}
        
        # Count by category
        category_counts = {}
        app_counts = {}
        action_type_counts = {}
        
        for entry in self.log_entries:
            # Category counts
            category = entry['category']
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # App counts
            app_name = entry['metadata'].get('app_name', 'Unknown')
            app_counts[app_name] = app_counts.get(app_name, 0) + 1
            
            # Action type counts
            action_type = entry['action_type']
            action_type_counts[action_type] = action_type_counts.get(action_type, 0) + 1
        
        return {
            'total_entries': len(self.log_entries),
            'category_counts': category_counts,
            'app_counts': app_counts,
            'action_type_counts': action_type_counts,
            'most_active_category': max(category_counts, key=category_counts.get) if category_counts else None,
            'most_used_app': max(app_counts, key=app_counts.get) if app_counts else None
        }
    
    def clear_logs(self):
        """Clear all log entries."""
        self.log_entries.clear()
        logger.info("Log entries cleared")
    
    def export_logs(self, filename: str = None) -> str:
        """Export logs to a file."""
        if filename is None:
            filename = f"workflow_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Workflow Log Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for entry in self.log_entries:
                    f.write(f"{entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | ")
                    f.write(f"{entry['action_type']} | ")
                    f.write(f"{entry['category']} | ")
                    f.write(f"{entry['content']}\n")
                    
                    if entry['metadata']:
                        f.write(f"  Metadata: {entry['metadata']}\n")
                    
                    f.write("\n")
            
            logger.info(f"Logs exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting logs: {e}")
            return ""
