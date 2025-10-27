#!/usr/bin/env python3
"""
AGE Agent - Automated Workflow Detection and Analysis
Simplified version with external LLM integration
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                                 QWidget, QPushButton, QTextEdit, QLabel, QProgressBar,
                                 QMessageBox, QSystemTrayIcon, QMenu, QAction)
    from PyQt5.QtCore import QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QIcon
except ImportError as e:
    print(f"Error importing PyQt5: {e}")
    print("Please install PyQt5: pip install PyQt5")
    sys.exit(1)

# Import our modules
try:
    from src.capture.simple_recorder import ScreenshotCapture, AudioRecorder
    from src.capture.live_analyzer import LiveAnalyzer
    from src.llm.workflow_analyzer import WorkflowAnalyzer
    from src.storage.simple_config import config
    from src.error_handling.simple_logger import logger
    from src.ui.enhanced_dashboard import EnhancedDashboard
except ImportError as e:
    print(f"Import error: {e}")
    print("Please check your Python path and module structure")
    sys.exit(1)


class RecordingWorker(QThread):
    """Worker thread for recording operations with indefinite duration."""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    live_detection = pyqtSignal(dict)  # New signal for live detection
    
    def __init__(self, live_analyzer=None):
        super().__init__()
        self.screenshots = []
        self.audio_path = None
        self.running = False
        self.start_time = None
        self.live_analyzer = live_analyzer
        self.screenshot_count = 0
    
    def run(self):
        """Run indefinite recording process."""
        try:
            self.running = True
            self.start_time = time.time()
            self.progress.emit("Starting indefinite recording...")
            
            # Initialize recorders
            screen_recorder = ScreenshotCapture()
            audio_recorder = AudioRecorder()
            
            # Start recording
            screen_recorder.start_recording()
            audio_recorder.start_recording()
            
            self.progress.emit("Recording in progress... (Press Stop to end)")
            
            # Record indefinitely until manually stopped
            while self.running:
                time.sleep(1)
                elapsed = int(time.time() - self.start_time)
                minutes = elapsed // 60
                seconds = elapsed % 60
                
                # Get latest screenshots for live analysis
                current_screenshots = screen_recorder.get_screenshots()
                if len(current_screenshots) > self.screenshot_count:
                    # New screenshots available
                    new_screenshots = current_screenshots[self.screenshot_count:]
                    self.screenshot_count = len(current_screenshots)
                    
                    # Send new screenshots for live analysis
                    if self.live_analyzer and new_screenshots:
                        for screenshot in new_screenshots:
                            self.live_analyzer.add_screenshot(screenshot, time.time())
                
                self.progress.emit(f"Recording... {minutes:02d}:{seconds:02d} (Press Stop to end)")
            
            # Stop recording
            screen_recorder.stop_recording()
            audio_recorder.stop_recording()
            
            # Get results
            self.screenshots = screen_recorder.get_screenshots()
            self.audio_path = audio_recorder.get_audio_path()
            duration = int(time.time() - self.start_time)
            
            result = {
                'screenshots': self.screenshots,
                'audio_path': self.audio_path,
                'duration': duration
            }
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(f"Recording error: {str(e)}")
    
    def stop(self):
        """Stop recording."""
        self.running = False


class AnalysisWorker(QThread):
    """Worker thread for workflow analysis."""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, session_data, screenshots, audio_path):
        super().__init__()
        self.session_data = session_data
        self.screenshots = screenshots
        self.audio_path = audio_path
    
    def run(self):
        """Run analysis process."""
        try:
            self.progress.emit("Analyzing workflow...")
            
            # Initialize analyzer
            analyzer = WorkflowAnalyzer(config)
            
            # Analyze session
            workflows = analyzer.analyze_session(
                self.session_data, 
                self.screenshots, 
                "No audio transcription available"  # Provide default text
            )
            
            # Ensure workflows is valid
            if not workflows:
                workflows = [{
                    'description': 'Computer activity detected',
                    'workflow_type': 'general',
                    'complexity': 'simple',
                    'automation_potential': 'low',
                    'automation_score': 25,
                    'steps': ['Computer activity was captured'],
                    'estimated_time': 'Unknown',
                    'repetitive_actions': ['General computer usage'],
                    'automation_opportunities': ['Review captured activity'],
                    'recommended_tools': ['Manual analysis'],
                    'implementation_difficulty': 'easy',
                    'time_savings': 'Unknown'
                }]
            
            result = {
                'workflows': workflows,
                'session_data': self.session_data,
                'screenshots': self.screenshots
            }
            
            self.progress.emit("Analysis complete!")
            self.finished.emit(result)
            
        except Exception as e:
            logger.error(f"Analysis worker error: {e}", exc_info=True)
            # Provide fallback result even if analysis fails
            fallback_workflows = [{
                'description': 'Computer activity detected (analysis failed)',
                'workflow_type': 'general',
                'complexity': 'simple',
                'automation_potential': 'low',
                'automation_score': 25,
                'steps': ['Computer activity was captured'],
                'estimated_time': 'Unknown',
                'repetitive_actions': ['General computer usage'],
                'automation_opportunities': ['Review captured activity'],
                'recommended_tools': ['Manual analysis'],
                'implementation_difficulty': 'easy',
                'time_savings': 'Unknown'
            }]
            
            result = {
                'workflows': fallback_workflows,
                'session_data': self.session_data,
                'screenshots': self.screenshots
            }
            
            self.progress.emit("Analysis complete (fallback)")
            self.finished.emit(result)


class AGEAgentMainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AGE Agent - Workflow Analyzer")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize components
        self.recording_worker = None
        self.analysis_worker = None
        self.is_recording = False
        self.session_data = None
        self.screenshots = []
        self.audio_path = None
        self.current_analysis = None
        self.enhanced_dashboard = None
        self.live_analyzer = LiveAnalyzer(config)
        self.live_detection_enabled = True
        
        # Setup UI
        self.setup_ui()
        self.setup_tray()
        
        # Setup live analyzer callback
        self.live_analyzer.add_callback(self.on_live_detection)
        
        # Initialize logger
        logger.info("AGE Agent started")
    
    def setup_ui(self):
        """Setup user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Title
        title = QLabel("AGE Agent - Indefinite Workflow Capture")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Record your workflow indefinitely - click Stop when finished")
        instructions.setStyleSheet("font-size: 12px; color: #666; margin: 5px; font-style: italic;")
        layout.addWidget(instructions)
        
        # Recording controls
        controls_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Recording")
        self.start_btn.clicked.connect(self.start_recording)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.stop_btn = QPushButton("Stop Recording")
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        self.analyze_btn = QPushButton("Analyze Workflow")
        self.analyze_btn.clicked.connect(self.analyze_workflow)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        self.enhanced_dashboard_btn = QPushButton("Enhanced Dashboard")
        self.enhanced_dashboard_btn.clicked.connect(self.show_enhanced_dashboard)
        self.enhanced_dashboard_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(self.analyze_btn)
        controls_layout.addWidget(self.enhanced_dashboard_btn)
        layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to record workflow indefinitely")
        self.status_label.setStyleSheet("font-size: 12px; color: #666; margin: 5px;")
        layout.addWidget(self.status_label)
        
        # Live detection status
        self.live_status_label = QLabel("Live Detection: Ready")
        self.live_status_label.setStyleSheet("font-size: 11px; color: #4CAF50; margin: 3px; font-weight: bold;")
        layout.addWidget(self.live_status_label)
        
        # Live detection toggle
        self.live_toggle_btn = QPushButton("Toggle Live Detection")
        self.live_toggle_btn.clicked.connect(self.toggle_live_detection)
        self.live_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 5px 10px;
                font-size: 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        layout.addWidget(self.live_toggle_btn)
        
        # Results area
        results_label = QLabel("Workflow Analysis Results:")
        results_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(results_label)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.results_text)
        
        # Store session data
        self.session_data = None
        self.screenshots = []
        self.audio_path = None
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        # Ctrl+R to start/stop recording
        self.record_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self.record_shortcut.activated.connect(self.toggle_recording)
        
        # Ctrl+E to stop recording (emergency stop)
        self.stop_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        self.stop_shortcut.activated.connect(self.emergency_stop)
    
    def toggle_recording(self):
        """Toggle recording with keyboard shortcut."""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def emergency_stop(self):
        """Emergency stop recording."""
        if self.is_recording:
            self.stop_recording()
            self.status_label.setText("Emergency stop activated!")
    
    def setup_tray(self):
        """Setup system tray icon."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setToolTip("AGE Agent - Indefinite Recording")
            
            # Create tray menu
            tray_menu = QMenu()
            
            show_action = QAction("Show", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            if self.is_recording:
                stop_action = QAction("Stop Recording", self)
                stop_action.triggered.connect(self.stop_recording)
                tray_menu.addAction(stop_action)
            
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
    
    def start_recording(self):
        """Start recording workflow."""
        try:
            self.is_recording = True
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.analyze_btn.setEnabled(False)
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Start recording worker (indefinite duration)
            self.recording_worker = RecordingWorker(self.live_analyzer if self.live_detection_enabled else None)
            self.recording_worker.progress.connect(self.update_status)
            self.recording_worker.finished.connect(self.recording_finished)
            self.recording_worker.error.connect(self.recording_error)
            self.recording_worker.live_detection.connect(self.on_live_detection)
            self.recording_worker.start()
            
            # Start live analysis if enabled
            if self.live_detection_enabled:
                self.live_analyzer.start_live_analysis()
            
            self.status_label.setText("Recording started...")
            logger.info("Recording started")
            
        except Exception as e:
            self.show_error(f"Failed to start recording: {str(e)}")
            self.reset_ui()
    
    def stop_recording(self):
        """Stop recording workflow."""
        try:
            if self.recording_worker:
                self.recording_worker.stop()
                self.recording_worker.wait()
            
            # Stop live analysis
            if self.live_detection_enabled:
                self.live_analyzer.stop_live_analysis()
            
            self.is_recording = False
            self.reset_ui()
            self.status_label.setText("Recording stopped")
            logger.info("Recording stopped")
            
        except Exception as e:
            self.show_error(f"Failed to stop recording: {str(e)}")
            self.reset_ui()
    
    def recording_finished(self, result):
        """Handle recording completion."""
        try:
            self.session_data = result
            self.screenshots = result.get('screenshots', [])
            self.audio_path = result.get('audio_path')
            
            self.reset_ui()
            self.analyze_btn.setEnabled(True)
            duration_minutes = self.session_data.get('duration', 0) // 60
            duration_seconds = self.session_data.get('duration', 0) % 60
            self.status_label.setText(f"Recording complete! Captured {len(self.screenshots)} screenshots in {duration_minutes:02d}:{duration_seconds:02d}")
            
            logger.info(f"Recording completed: {len(self.screenshots)} screenshots in {duration_minutes:02d}:{duration_seconds:02d}")
            
        except Exception as e:
            self.show_error(f"Error processing recording: {str(e)}")
            self.reset_ui()
    
    def recording_error(self, error_msg):
        """Handle recording error."""
        self.show_error(f"Recording error: {error_msg}")
        self.reset_ui()
    
    def analyze_workflow(self):
        """Analyze recorded workflow."""
        try:
            if not self.session_data:
                self.show_error("No recording data to analyze")
                return
            
            self.analyze_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            # Start analysis worker
            self.analysis_worker = AnalysisWorker(
                self.session_data, 
                self.screenshots, 
                self.audio_path
            )
            self.analysis_worker.progress.connect(self.update_status)
            self.analysis_worker.finished.connect(self.analysis_finished)
            self.analysis_worker.error.connect(self.analysis_error)
            self.analysis_worker.start()
            
            self.status_label.setText("Analyzing workflow...")
            logger.info("Workflow analysis started")
            
        except Exception as e:
            self.show_error(f"Failed to start analysis: {str(e)}")
            self.reset_ui()
    
    def analysis_finished(self, result):
        """Handle analysis completion."""
        try:
            workflows = result.get('workflows', [])
            
            # Store analysis data for enhanced dashboard
            self.current_analysis = result
            
            # Display results
            self.display_results(workflows)
            
            self.reset_ui()
            self.status_label.setText(f"Analysis complete! Found {len(workflows)} workflows")
            
            logger.info(f"Analysis completed: {len(workflows)} workflows found")
            
        except Exception as e:
            self.show_error(f"Error processing analysis: {str(e)}")
            self.reset_ui()
    
    def analysis_error(self, error_msg):
        """Handle analysis error."""
        self.show_error(f"Analysis error: {error_msg}")
        self.reset_ui()
    
    def display_results(self, workflows):
        """Display enhanced analysis results with detailed breakdown."""
        try:
            if not workflows:
                self.results_text.setText("No workflows detected in the recording.")
                return
            
            # Ensure workflows is a list
            if not isinstance(workflows, list):
                workflows = [workflows] if workflows else []
            
            # Validate each workflow has required fields
            valid_workflows = []
            for workflow in workflows:
                if isinstance(workflow, dict):
                    # Ensure required fields exist
                    if 'description' not in workflow:
                        workflow['description'] = 'Computer activity detected'
                    if 'workflow_type' not in workflow:
                        workflow['workflow_type'] = 'general'
                    if 'complexity' not in workflow:
                        workflow['complexity'] = 'moderate'
                    if 'automation_potential' not in workflow:
                        workflow['automation_potential'] = 'medium'
                    if 'automation_score' not in workflow:
                        workflow['automation_score'] = 50
                    if 'steps' not in workflow:
                        workflow['steps'] = ['Computer activity was captured']
                    if 'estimated_time' not in workflow:
                        workflow['estimated_time'] = 'Unknown'
                    
                    valid_workflows.append(workflow)
            
            if not valid_workflows:
                self.results_text.setText("No valid workflows detected in the recording.")
                return
            
            # Get detailed analysis
            try:
                from src.llm.workflow_analyzer import WorkflowAnalyzer
                analyzer = WorkflowAnalyzer(config)
                
                # Ensure we have valid session data
                if self.session_data is None:
                    self.session_data = {'duration': 0}
                if self.screenshots is None:
                    self.screenshots = []
                
                detailed_analysis = analyzer.get_detailed_analysis(
                    self.session_data, 
                    self.screenshots, 
                    "No audio transcription available"
                )
            except Exception as e:
                logger.error(f"Failed to get detailed analysis: {e}")
                detailed_analysis = None
            
            results_text = "🎯 COMPREHENSIVE WORKFLOW ANALYSIS\n"
            results_text += "=" * 60 + "\n\n"
            
            # Add detailed analysis if available
            if detailed_analysis:
                results_text += "📊 SESSION SUMMARY\n"
                results_text += "-" * 30 + "\n"
                session_summary = detailed_analysis.get('session_summary', {})
                results_text += f"⏱️  Total Duration: {session_summary.get('total_duration', 'Unknown')}\n"
                results_text += f"🖱️  Total Interactions: {session_summary.get('total_interactions', 0)}\n"
                results_text += f"📈 Activity Rate: {session_summary.get('activity_rate', 'Unknown')}\n"
                results_text += f"🏷️  Session Type: {session_summary.get('session_type', 'Unknown')}\n"
                results_text += f"⚡ Complexity Level: {session_summary.get('complexity_level', 'Unknown')}\n\n"
                
                # Add activity patterns
                activity_patterns = detailed_analysis.get('activity_patterns', {})
                if activity_patterns:
                    results_text += "🔍 ACTIVITY PATTERNS\n"
                    results_text += "-" * 30 + "\n"
                    patterns = activity_patterns.get('detected_patterns', [])
                    for pattern in patterns:
                        results_text += f"• {pattern}\n"
                    results_text += f"🎯 Workflow Intensity: {activity_patterns.get('workflow_intensity', 'Unknown')}\n\n"
                
                # Add automation analysis
                automation_analysis = detailed_analysis.get('automation_analysis', {})
                if automation_analysis:
                    results_text += "🤖 AUTOMATION ANALYSIS\n"
                    results_text += "-" * 30 + "\n"
                    automation_scores = automation_analysis.get('automation_scores', {})
                    results_text += f"📊 Overall Score: {automation_scores.get('overall_score', 'Unknown')}\n"
                    results_text += f"🔄 Repetition Score: {automation_scores.get('repetition_score', 'Unknown')}\n"
                    results_text += f"⚙️  Complexity Score: {automation_scores.get('complexity_score', 'Unknown')}\n"
                    results_text += f"📈 Frequency Score: {automation_scores.get('frequency_score', 'Unknown')}\n"
                    results_text += f"🎯 Recommended Approach: {automation_analysis.get('recommended_approach', 'Unknown')}\n\n"
            
            # Add workflow details
            results_text += "📋 WORKFLOW DETAILS\n"
            results_text += "=" * 60 + "\n\n"
            
            for i, workflow in enumerate(valid_workflows, 1):
                results_text += f"📋 WORKFLOW {i}\n"
                results_text += "-" * 30 + "\n"
                
                # Basic info
                results_text += f"📝 Description: {workflow.get('description', 'Unknown')}\n"
                results_text += f"🏷️  Type: {workflow.get('workflow_type', 'general').upper()}\n"
                results_text += f"⚡ Complexity: {workflow.get('complexity', 'moderate').upper()}\n"
                results_text += f"🤖 Automation Potential: {workflow.get('automation_potential', 'medium').upper()}\n"
                results_text += f"📊 Automation Score: {workflow.get('automation_score', 50)}/100\n"
                results_text += f"⏱️  Estimated Time: {workflow.get('estimated_time', 'Unknown')}\n\n"
                
                # Steps
                steps = workflow.get('steps', [])
                if steps:
                    results_text += "📋 WORKFLOW STEPS:\n"
                    for j, step in enumerate(steps, 1):
                        results_text += f"   {j}. {step}\n"
                    results_text += "\n"
                
                # Repetitive actions
                repetitive = workflow.get('repetitive_actions', [])
                if repetitive:
                    results_text += "🔄 REPETITIVE ACTIONS:\n"
                    for action in repetitive:
                        results_text += f"   • {action}\n"
                    results_text += "\n"
                
                # Automation opportunities
                opportunities = workflow.get('automation_opportunities', [])
                if opportunities:
                    results_text += "🚀 AUTOMATION OPPORTUNITIES:\n"
                    for opp in opportunities:
                        results_text += f"   • {opp}\n"
                    results_text += "\n"
                
                # Recommended tools
                tools = workflow.get('recommended_tools', [])
                if tools:
                    results_text += "🛠️  RECOMMENDED TOOLS:\n"
                    for tool in tools:
                        results_text += f"   • {tool}\n"
                    results_text += "\n"
                
                # Implementation details
                difficulty = workflow.get('implementation_difficulty', 'medium')
                time_savings = workflow.get('time_savings', 'Unknown')
                results_text += f"⚙️  Implementation Difficulty: {difficulty.upper()}\n"
                results_text += f"💾 Time Savings: {time_savings}\n\n"
                
                # Legacy recommendations
                recommendations = workflow.get('recommendations', [])
                if recommendations:
                    results_text += "💡 ADDITIONAL RECOMMENDATIONS:\n"
                    for rec in recommendations:
                        results_text += f"   • {rec}\n"
                    results_text += "\n"
                
                results_text += "=" * 60 + "\n\n"
            
            # Add detailed analysis sections
            if detailed_analysis:
                # Add workflow breakdown
                workflow_breakdown = detailed_analysis.get('workflow_breakdown', {})
                if workflow_breakdown:
                    results_text += "\n🔧 WORKFLOW BREAKDOWN\n"
                    results_text += "-" * 30 + "\n"
                    phases = workflow_breakdown.get('workflow_phases', [])
                    for phase in phases:
                        results_text += f"📋 {phase.get('name', 'Unknown Phase')}\n"
                        results_text += f"   Interactions: {phase.get('estimated_interactions', 0)}\n"
                        results_text += f"   Description: {phase.get('description', 'Unknown')}\n"
                        results_text += f"   Automation Potential: {phase.get('automation_potential', 'Unknown')}\n\n"
                
                # Add optimization recommendations
                optimization_recommendations = detailed_analysis.get('optimization_recommendations', [])
                if optimization_recommendations:
                    results_text += "💡 OPTIMIZATION RECOMMENDATIONS\n"
                    results_text += "-" * 30 + "\n"
                    for rec in optimization_recommendations:
                        results_text += f"🎯 Priority: {rec.get('priority', 'Unknown')}\n"
                        results_text += f"📂 Category: {rec.get('category', 'Unknown')}\n"
                        results_text += f"💡 Recommendation: {rec.get('recommendation', 'Unknown')}\n"
                        results_text += f"📈 Expected Benefit: {rec.get('expected_benefit', 'Unknown')}\n"
                        results_text += f"⚙️  Implementation Effort: {rec.get('implementation_effort', 'Unknown')}\n\n"
                
                # Add debugging information
                debugging_info = detailed_analysis.get('debugging_info', {})
                if debugging_info:
                    results_text += "🔍 DEBUGGING INFORMATION\n"
                    results_text += "-" * 30 + "\n"
                    results_text += f"🕐 Analysis Timestamp: {debugging_info.get('analysis_timestamp', 'Unknown')}\n"
                    context_data = debugging_info.get('context_data', {})
                    results_text += f"📊 Screenshot Count: {context_data.get('screenshot_count', 0)}\n"
                    results_text += f"⏱️  Duration: {context_data.get('duration', 0)} seconds\n"
                    results_text += f"🎤 Audio Length: {context_data.get('audio_length', 0)} characters\n"
                    results_text += f"📁 Has Screenshots: {context_data.get('has_screenshots', False)}\n"
                    
                    potential_issues = debugging_info.get('potential_issues', [])
                    if potential_issues:
                        results_text += "\n⚠️  Potential Issues:\n"
                        for issue in potential_issues:
                            results_text += f"   • {issue}\n"
                    
                    recommendations = debugging_info.get('recommendations', [])
                    if recommendations:
                        results_text += "\n💡 Recommendations:\n"
                        for rec in recommendations:
                            results_text += f"   • {rec}\n"
                    results_text += "\n"
            
            # Summary
            total_workflows = len(valid_workflows)
            avg_score = sum(w.get('automation_score', 50) for w in valid_workflows) / total_workflows
            high_potential = sum(1 for w in valid_workflows if w.get('automation_score', 50) >= 70)
            
            results_text += "📊 FINAL SUMMARY\n"
            results_text += "-" * 20 + "\n"
            results_text += f"Total Workflows: {total_workflows}\n"
            results_text += f"Average Automation Score: {avg_score:.1f}/100\n"
            results_text += f"High Potential Workflows: {high_potential}\n"
            results_text += f"Recommended Focus: {'High automation potential workflows' if high_potential > 0 else 'Process optimization'}\n"
            
            self.results_text.setText(results_text)
            
        except Exception as e:
            self.results_text.setText(f"Error displaying results: {str(e)}")
    
    def update_status(self, message):
        """Update status message."""
        self.status_label.setText(message)
    
    def reset_ui(self):
        """Reset UI to initial state."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def show_error(self, message):
        """Show error message."""
        QMessageBox.critical(self, "Error", message)
        logger.error(message)
    
    def closeEvent(self, event):
        """Handle application close."""
        if self.is_recording:
            reply = QMessageBox.question(
                self, 
                "Confirm Exit", 
                "Recording is in progress. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        # Stop any running workers
        if self.recording_worker and self.recording_worker.isRunning():
            self.recording_worker.stop()
            self.recording_worker.wait()
        
        if self.analysis_worker and self.analysis_worker.isRunning():
            self.analysis_worker.quit()
            self.analysis_worker.wait()
        
        logger.info("AGE Agent closed")
        event.accept()
    
    def show_enhanced_dashboard(self):
        """Show the enhanced dashboard with detailed analysis."""
        try:
            if not self.current_analysis:
                self.show_error("No analysis data available. Please run analysis first.")
                return
            
            # Create or update enhanced dashboard
            if not self.enhanced_dashboard:
                self.enhanced_dashboard = EnhancedDashboard()
            
            # Update dashboard with current analysis
            self.enhanced_dashboard.update_analysis_data(self.current_analysis)
            
            # Show dashboard
            self.enhanced_dashboard.show()
            self.enhanced_dashboard.raise_()
            self.enhanced_dashboard.activateWindow()
            
            logger.info("Enhanced dashboard opened")
            
        except Exception as e:
            self.show_error(f"Failed to open enhanced dashboard: {str(e)}")
            logger.error(f"Error opening enhanced dashboard: {e}")
    
    def toggle_live_detection(self):
        """Toggle live detection on/off."""
        self.live_detection_enabled = not self.live_detection_enabled
        
        if self.live_detection_enabled:
            self.live_status_label.setText("Live Detection: ON")
            self.live_status_label.setStyleSheet("font-size: 11px; color: #4CAF50; margin: 3px; font-weight: bold;")
            self.live_toggle_btn.setText("Disable Live Detection")
            logger.info("Live detection enabled")
        else:
            self.live_status_label.setText("Live Detection: OFF")
            self.live_status_label.setStyleSheet("font-size: 11px; color: #f44336; margin: 3px; font-weight: bold;")
            self.live_toggle_btn.setText("Enable Live Detection")
            self.live_analyzer.stop_live_analysis()
            logger.info("Live detection disabled")
    
    def on_live_detection(self, detection_result):
        """Handle live detection results."""
        try:
            # Update live status display
            summary = self.live_analyzer.get_live_summary()
            self.live_status_label.setText(f"Live Detection: {summary}")
            
            # Update status with live info
            if self.is_recording:
                tasks = detection_result.get('detected_tasks', [])
                apps = detection_result.get('applications', [])
                
                if tasks or apps:
                    task_names = [task['name'] for task in tasks]
                    app_names = [app['name'] for app in apps]
                    live_info = f" | Live: {', '.join(set(task_names))} | Apps: {', '.join(set(app_names))}"
                    current_status = self.status_label.text()
                    if "Live:" not in current_status:
                        self.status_label.setText(current_status + live_info)
            
            logger.info(f"Live detection: {len(tasks)} tasks, {len(apps)} apps")
            
        except Exception as e:
            logger.error(f"Error handling live detection: {e}")


def main():
    """Main application entry point."""
    try:
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("AGE Agent")
        app.setApplicationVersion("1.0")
        
        # Create and show main window
        window = AGEAgentMainWindow()
        window.show()
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
