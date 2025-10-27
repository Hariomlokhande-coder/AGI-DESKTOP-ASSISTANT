"""
Live analyzer for real-time task detection during recording.
"""

import time
import threading
from typing import Dict, List, Any, Optional, Callable
from queue import Queue
import cv2
import numpy as np

from ..error_handling.simple_logger import logger
from ..processing.ocr_analyzer import OCRAnalyzer
from ..llm.local_llm_enhanced import EnhancedLocalLLMClient


class LiveAnalyzer:
    """Real-time analyzer for live task detection."""
    
    def __init__(self, config):
        self.config = config
        self.ocr_analyzer = OCRAnalyzer()
        self.llm_client = EnhancedLocalLLMClient(config)
        self.is_running = False
        self.analysis_queue = Queue()
        self.results_queue = Queue()
        self.analysis_thread = None
        self.callbacks = []
        
        # Live detection settings
        self.analysis_interval = 2.0  # Analyze every 2 seconds
        self.last_analysis_time = 0
        self.detected_tasks = []
        self.current_applications = []
        
        logger.info("LiveAnalyzer initialized")
    
    def start_live_analysis(self):
        """Start live analysis thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        logger.info("Live analysis started")
    
    def stop_live_analysis(self):
        """Stop live analysis thread."""
        self.is_running = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=1.0)
        logger.info("Live analysis stopped")
    
    def add_screenshot(self, screenshot_path: str, timestamp: float):
        """Add screenshot for analysis."""
        if not self.is_running:
            return
        
        self.analysis_queue.put({
            'path': screenshot_path,
            'timestamp': timestamp
        })
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for live results."""
        self.callbacks.append(callback)
    
    def _analysis_loop(self):
        """Main analysis loop running in separate thread."""
        while self.is_running:
            try:
                # Process screenshots from queue
                if not self.analysis_queue.empty():
                    screenshot_data = self.analysis_queue.get_nowait()
                    self._analyze_screenshot(screenshot_data)
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                time.sleep(1.0)
    
    def _analyze_screenshot(self, screenshot_data: Dict[str, Any]):
        """Analyze a single screenshot."""
        try:
            current_time = time.time()
            
            # Only analyze if enough time has passed
            if current_time - self.last_analysis_time < self.analysis_interval:
                return
            
            self.last_analysis_time = current_time
            
            # Perform OCR analysis
            ocr_result = self.ocr_analyzer.analyze_screenshot(screenshot_data['path'])
            
            # Quick task detection
            tasks = self._detect_quick_tasks(ocr_result)
            applications = self._detect_applications(ocr_result)
            
            # Update current state
            self._update_detected_tasks(tasks)
            self._update_applications(applications)
            
            # Create live result
            live_result = {
                'timestamp': screenshot_data['timestamp'],
                'detected_tasks': tasks,
                'applications': applications,
                'ocr_confidence': ocr_result.get('confidence', 0),
                'live_analysis': True
            }
            
            # Notify callbacks
            for callback in self.callbacks:
                try:
                    callback(live_result)
                except Exception as e:
                    logger.error(f"Error in callback: {e}")
            
            logger.info(f"Live analysis: {len(tasks)} tasks, {len(applications)} apps detected")
            
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {e}")
    
    def _detect_quick_tasks(self, ocr_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Quick task detection from OCR results."""
        tasks = []
        
        # Get detected tasks from OCR
        detected_tasks = ocr_result.get('detected_tasks', [])
        
        # Quick pattern matching
        raw_text = ocr_result.get('raw_text', '').lower()
        ui_elements = ocr_result.get('ui_elements', {})
        
        # Detect common tasks based on text and UI elements
        task_patterns = {
            'data_entry': ['typing', 'input', 'enter', 'type', 'data'],
            'file_operations': ['save', 'open', 'file', 'folder', 'copy', 'move'],
            'formatting': ['bold', 'italic', 'underline', 'font', 'color'],
            'navigation': ['click', 'select', 'menu', 'button', 'tab'],
            'calculation': ['=', 'sum', 'average', 'formula', 'calculate']
        }
        
        for task_name, keywords in task_patterns.items():
            keyword_matches = sum(1 for keyword in keywords if keyword in raw_text)
            if keyword_matches > 0:
                tasks.append({
                    'name': task_name,
                    'confidence': min(keyword_matches * 0.3, 1.0),
                    'keywords_found': [kw for kw in keywords if kw in raw_text],
                    'timestamp': time.time()
                })
        
        # Add OCR detected tasks
        for task in detected_tasks:
            tasks.append({
                'name': task.get('name', 'unknown'),
                'confidence': task.get('confidence', 0.5),
                'keywords_found': task.get('keywords_found', []),
                'timestamp': time.time()
            })
        
        return tasks
    
    def _detect_applications(self, ocr_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect applications from OCR results."""
        applications = []
        
        # Get applications from OCR
        app_context = ocr_result.get('application', {})
        if app_context.get('name') != 'unknown':
            applications.append({
                'name': app_context['name'],
                'confidence': app_context.get('confidence', 0.5),
                'context': app_context.get('context', {}),
                'timestamp': time.time()
            })
        
        # Quick application detection based on UI elements
        ui_elements = ocr_result.get('ui_elements', {})
        app_elements = ui_elements.get('applications', [])
        
        for app in app_elements:
            applications.append({
                'name': app,
                'confidence': 0.7,
                'context': {'detected_from': 'ui_elements'},
                'timestamp': time.time()
            })
        
        return applications
    
    def _update_detected_tasks(self, new_tasks: List[Dict[str, Any]]):
        """Update the list of detected tasks."""
        # Add new tasks
        for task in new_tasks:
            # Check if similar task already exists
            existing = False
            for existing_task in self.detected_tasks:
                if (existing_task['name'] == task['name'] and 
                    time.time() - existing_task['timestamp'] < 10):  # Within 10 seconds
                    existing = True
                    # Update confidence if higher
                    if task['confidence'] > existing_task['confidence']:
                        existing_task['confidence'] = task['confidence']
                    existing_task['count'] = existing_task.get('count', 1) + 1
                    break
            
            if not existing:
                task['count'] = 1
                self.detected_tasks.append(task)
        
        # Remove old tasks (older than 30 seconds)
        current_time = time.time()
        self.detected_tasks = [
            task for task in self.detected_tasks 
            if current_time - task['timestamp'] < 30
        ]
    
    def _update_applications(self, new_applications: List[Dict[str, Any]]):
        """Update the list of detected applications."""
        # Add new applications
        for app in new_applications:
            # Check if application already exists
            existing = False
            for existing_app in self.current_applications:
                if existing_app['name'] == app['name']:
                    existing = True
                    # Update confidence if higher
                    if app['confidence'] > existing_app['confidence']:
                        existing_app['confidence'] = app['confidence']
                    existing_app['count'] = existing_app.get('count', 1) + 1
                    existing_app['last_seen'] = time.time()
                    break
            
            if not existing:
                app['count'] = 1
                app['last_seen'] = time.time()
                self.current_applications.append(app)
        
        # Remove old applications (not seen for 60 seconds)
        current_time = time.time()
        self.current_applications = [
            app for app in self.current_applications 
            if current_time - app.get('last_seen', 0) < 60
        ]
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current analysis status."""
        return {
            'is_running': self.is_running,
            'detected_tasks': self.detected_tasks,
            'current_applications': self.current_applications,
            'queue_size': self.analysis_queue.qsize()
        }
    
    def get_live_summary(self) -> str:
        """Get a live summary of detected activities."""
        if not self.detected_tasks and not self.current_applications:
            return "No activity detected yet..."
        
        summary_parts = []
        
        if self.current_applications:
            app_names = [app['name'] for app in self.current_applications]
            summary_parts.append(f"Applications: {', '.join(set(app_names))}")
        
        if self.detected_tasks:
            task_names = [task['name'] for task in self.detected_tasks]
            task_counts = {}
            for task_name in task_names:
                task_counts[task_name] = task_counts.get(task_name, 0) + 1
            
            task_summary = ', '.join([f"{name}({count})" for name, count in task_counts.items()])
            summary_parts.append(f"Tasks: {task_summary}")
        
        return " | ".join(summary_parts)
