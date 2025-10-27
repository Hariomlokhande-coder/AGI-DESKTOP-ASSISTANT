"""
Main workflow monitoring system that coordinates all components.
"""

import time
import logging
import signal
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
import queue

# Changed from relative imports to absolute imports
from monitoring.window_monitor import WindowMonitor, WindowCapture
from monitoring.keyboard_monitor import KeyboardMonitor, KeyboardActionClassifier
from monitoring.screenshot_capture import ScreenshotCapture, WorkflowAnalyzer
from monitoring.action_classifier import ActionClassifier
from monitoring.real_time_logger import RealTimeLogger
from processing.ocr_analyzer import OCRAnalyzer
from error_handling.simple_logger import logger

class WorkflowMonitor:
    """Main workflow monitoring system that coordinates all components."""
    
    def __init__(self, 
                 enable_ocr: bool = True,
                 enable_screenshots: bool = True,
                 screenshot_interval: float = 5.0,
                 log_to_file: bool = True):
        
        self.enable_ocr = enable_ocr
        self.enable_screenshots = enable_screenshots
        self.screenshot_interval = screenshot_interval
        self.log_to_file = log_to_file
        
        # Initialize components
        self.ocr_analyzer = None
        self.window_monitor = None
        self.keyboard_monitor = None
        self.screenshot_capture = None
        self.action_classifier = None
        self.real_time_logger = None
        self.workflow_analyzer = None
        
        # Control flags
        self.running = False
        self.monitor_thread = None
        self.screenshot_thread = None
        
        # Event queues
        self.event_queue = queue.Queue()
        self.screenshot_queue = queue.Queue()
        
        # Statistics
        self.stats = {
            'start_time': None,
            'total_events': 0,
            'window_changes': 0,
            'keyboard_events': 0,
            'screenshots_taken': 0,
            'ocr_analyses': 0
        }
        
        # Initialize components
        self._initialize_components()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        logger.info("WorkflowMonitor initialized")
    
    def _initialize_components(self):
        """Initialize all monitoring components."""
        try:
            # Initialize OCR analyzer if enabled
            if self.enable_ocr:
                self.ocr_analyzer = OCRAnalyzer()
                logger.info("OCR analyzer initialized")
            
            # Initialize window monitor
            self.window_monitor = WindowMonitor(callback=self._on_window_change)
            logger.info("Window monitor initialized")
            
            # Initialize keyboard monitor
            self.keyboard_monitor = KeyboardMonitor(callback=self._on_keyboard_event)
            logger.info("Keyboard monitor initialized")
            
            # Initialize screenshot capture
            if self.enable_screenshots:
                self.screenshot_capture = ScreenshotCapture(
                    output_dir="screenshots",
                    callback=self._on_screenshot_captured
                )
                logger.info("Screenshot capture initialized")
            
            # Initialize action classifier
            self.action_classifier = ActionClassifier()
            logger.info("Action classifier initialized")
            
            # Initialize real-time logger
            self.real_time_logger = RealTimeLogger(
                log_to_file=self.log_to_file,
                log_file="workflow_log.txt"
            )
            logger.info("Real-time logger initialized")
            
            # Initialize workflow analyzer
            self.workflow_analyzer = WorkflowAnalyzer(self.ocr_analyzer)
            logger.info("Workflow analyzer initialized")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.stop_monitoring()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start_monitoring(self):
        """Start the workflow monitoring system."""
        if self.running:
            logger.warning("Workflow monitoring is already running")
            return
        
        try:
            self.running = True
            self.stats['start_time'] = datetime.now()
            
            # Start real-time logger
            self.real_time_logger.start_logging()
            
            # Start window monitoring
            self.window_monitor.start_monitoring()
            
            # Start keyboard monitoring
            if not self.keyboard_monitor.start_monitoring():
                logger.warning("Keyboard monitoring failed to start")
            
            # Start screenshot capture service
            if self.enable_screenshots and self.screenshot_capture:
                self.screenshot_capture.start_capture_service()
            
            # Start main monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            # Start screenshot thread if enabled
            if self.enable_screenshots:
                self.screenshot_thread = threading.Thread(target=self._screenshot_loop, daemon=True)
                self.screenshot_thread.start()
            
            logger.info("Workflow monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Error starting workflow monitoring: {e}")
            self.stop_monitoring()
            raise
    
    def stop_monitoring(self):
        """Stop the workflow monitoring system."""
        if not self.running:
            return
        
        logger.info("Stopping workflow monitoring...")
        self.running = False
        
        # Stop all components
        if self.window_monitor:
            self.window_monitor.stop_monitoring()
        
        if self.keyboard_monitor:
            self.keyboard_monitor.stop_monitoring()
        
        if self.screenshot_capture:
            self.screenshot_capture.stop_capture_service()
        
        if self.real_time_logger:
            self.real_time_logger.stop_logging()
        
        # Wait for threads to finish
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        if self.screenshot_thread:
            self.screenshot_thread.join(timeout=2)
        
        # End current workflow session
        if self.action_classifier:
            self.action_classifier.end_current_session()
        
        logger.info("Workflow monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Process events from queue
                self._process_event_queue()
                
                # Update statistics
                self._update_statistics()
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(1)
    
    def _screenshot_loop(self):
        """Screenshot capture loop."""
        last_screenshot_time = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check if it's time to take a screenshot
                if current_time - last_screenshot_time >= self.screenshot_interval:
                    # Capture active window
                    if self.screenshot_capture:
                        self.screenshot_capture.capture_active_window(save_to_disk=True)
                        last_screenshot_time = current_time
                        self.stats['screenshots_taken'] += 1
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in screenshot loop: {e}")
                time.sleep(5)
    
    def _process_event_queue(self):
        """Process events from the event queue."""
        try:
            while not self.event_queue.empty():
                event = self.event_queue.get_nowait()
                self._handle_event(event)
                self.event_queue.task_done()
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error processing event queue: {e}")
    
    def _handle_event(self, event: Dict):
        """Handle a single event."""
        try:
            event_type = event.get('type', 'unknown')
            
            if event_type == 'window_change':
                self._handle_window_change_event(event)
            elif event_type == 'keyboard_event':
                self._handle_keyboard_event(event)
            elif event_type == 'screenshot_captured':
                self._handle_screenshot_event(event)
            else:
                logger.warning(f"Unknown event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error handling event: {e}")
    
    def _on_window_change(self, window_info: Dict):
        """Callback for window change events."""
        try:
            # Log window change
            self.real_time_logger.log_window_change(window_info)
            
            # Classify the action
            if self.action_classifier:
                classified_action = self.action_classifier.classify_action({
                    'type': 'window_change',
                    'content': f"Switched to {window_info.get('app_name', 'Unknown')}",
                    'app_name': window_info.get('app_name', ''),
                    'timestamp': window_info.get('timestamp', datetime.now()),
                    'metadata': window_info
                })
                
                # Log classified action
                self.real_time_logger.log_action(
                    action_type='app_switched',
                    content=f"{window_info.get('app_name', 'Unknown')} - {window_info.get('title', '')}",
                    metadata=window_info,
                    category=classified_action['primary_category'],
                    confidence=classified_action['confidence']
                )
            
            # Add to event queue
            self.event_queue.put({
                'type': 'window_change',
                'data': window_info,
                'timestamp': datetime.now()
            })
            
            self.stats['window_changes'] += 1
            
        except Exception as e:
            logger.error(f"Error handling window change: {e}")
    
    def _on_keyboard_event(self, key_event: Dict):
        """Callback for keyboard events."""
        try:
            # Log keyboard event
            self.real_time_logger.log_keyboard_action(key_event)
            
            # Classify the action
            if self.action_classifier:
                classified_action = self.action_classifier.classify_action({
                    'type': key_event.get('type', 'keyboard'),
                    'content': key_event.get('content', ''),
                    'app_name': self._get_current_app_name(),
                    'timestamp': key_event.get('timestamp', datetime.now()),
                    'metadata': key_event
                })
                
                # Log classified action
                self.real_time_logger.log_action(
                    action_type=classified_action['subcategory'],
                    content=key_event.get('content', ''),
                    metadata=key_event,
                    category=classified_action['primary_category'],
                    confidence=classified_action['confidence']
                )
            
            # Add to event queue
            self.event_queue.put({
                'type': 'keyboard_event',
                'data': key_event,
                'timestamp': datetime.now()
            })
            
            self.stats['keyboard_events'] += 1
            
        except Exception as e:
            logger.error(f"Error handling keyboard event: {e}")
    
    def _on_screenshot_captured(self, capture_info: Dict):
        """Callback for screenshot capture events."""
        try:
            # Perform OCR analysis if enabled
            if self.enable_ocr and self.ocr_analyzer and capture_info.get('saved'):
                analysis_result = self.ocr_analyzer.analyze_screenshot(capture_info['filepath'])
                
                # Log OCR analysis
                self.real_time_logger.log_ocr_analysis(analysis_result, capture_info['filepath'])
                
                # Analyze workflow
                if self.workflow_analyzer:
                    workflow_analysis = self.workflow_analyzer.analyze_capture(capture_info)
                    
                    # Log workflow insights
                    if workflow_analysis.get('workflow_indicators'):
                        indicators = workflow_analysis['workflow_indicators']
                        self.real_time_logger.log_action(
                            action_type='workflow_analysis',
                            content=f"Workflow detected: {', '.join(indicators)}",
                            metadata={
                                'indicators': indicators,
                                'screenshot_path': capture_info['filepath'],
                                'app_name': capture_info.get('window_title', 'Unknown')
                            },
                            category='system'
                        )
                
                self.stats['ocr_analyses'] += 1
            
            # Add to event queue
            self.event_queue.put({
                'type': 'screenshot_captured',
                'data': capture_info,
                'timestamp': datetime.now()
            })
            
        except Exception as e:
            logger.error(f"Error handling screenshot capture: {e}")
    
    def _handle_window_change_event(self, event: Dict):
        """Handle window change event."""
        # Additional processing can be added here
        pass
    
    def _handle_keyboard_event(self, event: Dict):
        """Handle keyboard event."""
        # Additional processing can be added here
        pass
    
    def _handle_screenshot_event(self, event: Dict):
        """Handle screenshot event."""
        # Additional processing can be added here
        pass
    
    def _get_current_app_name(self) -> str:
        """Get the current active application name."""
        if self.window_monitor:
            current_window = self.window_monitor.get_current_window()
            if current_window:
                return current_window.get('app_name', 'Unknown')
        return 'Unknown'
    
    def _update_statistics(self):
        """Update monitoring statistics."""
        self.stats['total_events'] = (
            self.stats['window_changes'] + 
            self.stats['keyboard_events'] + 
            self.stats['screenshots_taken']
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current monitoring statistics."""
        stats = self.stats.copy()
        
        # Add runtime
        if stats['start_time']:
            stats['runtime_seconds'] = (datetime.now() - stats['start_time']).total_seconds()
        
        # Add component statistics
        if self.action_classifier:
            stats['action_summary'] = self.action_classifier.get_action_summary()
        
        if self.real_time_logger:
            stats['log_statistics'] = self.real_time_logger.get_statistics()
        
        return stats
    
    def get_workflow_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent workflow sessions."""
        if self.action_classifier:
            return self.action_classifier.get_workflow_sessions(limit)
        return []
    
    def get_recent_actions(self, limit: int = 50) -> List[Dict]:
        """Get recent actions."""
        if self.real_time_logger:
            return self.real_time_logger.get_recent_entries(limit)
        return []
    
    def export_logs(self, filename: str = None) -> str:
        """Export logs to a file."""
        if self.real_time_logger:
            return self.real_time_logger.export_logs(filename)
        return ""
    
    def clear_logs(self):
        """Clear all logs."""
        if self.real_time_logger:
            self.real_time_logger.clear_logs()
        
        if self.action_classifier:
            self.action_classifier.clear_history()
    
    def is_running(self) -> bool:
        """Check if monitoring is running."""
        return self.running


def main():
    """Main function to run the workflow monitor."""
    print("=" * 70)
    print("WORKFLOW MONITOR - Real-time Application and Action Tracking")
    print("=" * 70)
    print("\nStarting monitoring... Press Ctrl+C to stop")
    print("\nYou will see detailed action labels as you work:")
    print("  [APP OPENED] Opened Microsoft Excel - Workbook1.xlsx")
    print("  [TYPING] Typing in Microsoft Excel: data entry...")
    print("  [FILE ACTION] Saved file - Ctrl+S")
    print("\n" + "=" * 70 + "\n")
    
    try:
        # Create and start monitor
        monitor = WorkflowMonitor(
            enable_ocr=True,
            enable_screenshots=True,
            screenshot_interval=5.0,
            log_to_file=True
        )
        
        monitor.start_monitoring()
        
        # Keep running until interrupted
        import threading
        last_stats_time = 0
        
        while monitor.is_running():
            time.sleep(1)
            
            # Print statistics every 30 seconds
            current_time = time.time()
            if current_time - last_stats_time >= 30:
                stats = monitor.get_statistics()
                runtime = stats.get('runtime_seconds', 0)
                hours, remainder = divmod(runtime, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                print(f"\n{'=' * 70}")
                print(f"[STATS] Runtime: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d} | "
                      f"Events: {stats['total_events']} | "
                      f"Windows: {stats['window_changes']} | "
                      f"Keyboard: {stats['keyboard_events']} | "
                      f"Screenshots: {stats['screenshots_taken']}")
                print('=' * 70 + "\n")
                last_stats_time = current_time
    
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'monitor' in locals():
            monitor.stop_monitoring()
        
        print("\n" + "=" * 70)
        print("Workflow monitoring stopped.")
        print("Logs saved to: workflow_log.txt")
        print("=" * 70)


if __name__ == "__main__":
    main()
