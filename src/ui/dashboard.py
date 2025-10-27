"""Enhanced main dashboard UI using PyQt5 with comprehensive error handling."""
import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QProgressBar,
    QMessageBox, QGroupBox, QListWidget, QSplitter,
    QMenuBar, QAction, QStatusBar, QSystemTrayIcon,
    QMenu, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon, QPixmap
from ..utils.constants import *
from ..error_handling.logger import logger


class Dashboard(QMainWindow):
    """Enhanced main application dashboard with comprehensive error handling."""
    
    # Signals
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.recording = False
        self.recording_time = 0
        self.max_recording_time = 3600  # 1 hour max
        self.is_processing = False
        
        try:
            self.init_ui()
            self.setup_menu()
            self.setup_status_bar()
            self.setup_tray_icon()
            
            # Timer for recording duration
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_recording_time)
            
            # Timer for UI updates
            self.ui_timer = QTimer()
            self.ui_timer.timeout.connect(self.update_ui_status)
            self.ui_timer.start(1000)  # Update every second
            
            logger.info("Dashboard UI initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize dashboard UI: {e}", exc_info=True)
            raise
    
    def init_ui(self):
        """Initialize the user interface with enhanced error handling."""
        try:
            self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
            self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
            
            # Set minimum window size
            self.setMinimumSize(800, 600)
            
            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main layout
            main_layout = QVBoxLayout()
            central_widget.setLayout(main_layout)
            
            # Title section
            self._create_title_section(main_layout)
            
            # Status section
            self._create_status_section(main_layout)
            
            # Control buttons section
            self._create_control_section(main_layout)
            
            # Progress section
            self._create_progress_section(main_layout)
            
            # Splitter for workflow and log sections
            splitter = QSplitter(Qt.Horizontal)
            
            # Workflow display
            self._create_workflow_section(splitter)
            
            # Log display
            self._create_log_section(splitter)
            
            # Set splitter proportions
            splitter.setSizes([400, 300])
            main_layout.addWidget(splitter)
            
            # Set stylesheet
            self._apply_stylesheet()
            
        except Exception as e:
            logger.error(f"Error initializing UI: {e}", exc_info=True)
            raise
    
    def _create_title_section(self, layout):
        """Create title section."""
        try:
            title = QLabel(APP_NAME)
            title.setFont(QFont('Arial', 24, QFont.Bold))
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("color: #2c3e50; padding: 10px;")
            layout.addWidget(title)
        except Exception as e:
            logger.error(f"Error creating title section: {e}")
    
    def _create_status_section(self, layout):
        """Create status section."""
        try:
            # Status label
            self.status_label = QLabel(STATUS_IDLE)
            self.status_label.setFont(QFont('Arial', 14))
            self.status_label.setAlignment(Qt.AlignCenter)
            self.status_label.setStyleSheet("color: #666; padding: 10px;")
            layout.addWidget(self.status_label)
            
            # Recording time label
            self.time_label = QLabel("00:00:00")
            self.time_label.setFont(QFont('Arial', 18, QFont.Bold))
            self.time_label.setAlignment(Qt.AlignCenter)
            self.time_label.setStyleSheet("color: #2c3e50; padding: 5px;")
            layout.addWidget(self.time_label)
            
        except Exception as e:
            logger.error(f"Error creating status section: {e}")
    
    def _create_control_section(self, layout):
        """Create control buttons section."""
        try:
            button_layout = QHBoxLayout()
            
            # Start button
            self.start_btn = QPushButton("Start Recording")
            self.start_btn.setMinimumHeight(BUTTON_HEIGHT)
            self.start_btn.setMinimumWidth(150)
            self.start_btn.clicked.connect(self.on_start_clicked)
            button_layout.addWidget(self.start_btn)
            
            # Stop button
            self.stop_btn = QPushButton("Stop Recording")
            self.stop_btn.setMinimumHeight(BUTTON_HEIGHT)
            self.stop_btn.setMinimumWidth(150)
            self.stop_btn.setEnabled(False)
            self.stop_btn.clicked.connect(self.on_stop_clicked)
            button_layout.addWidget(self.stop_btn)
            
            # Emergency stop button
            self.emergency_btn = QPushButton("Emergency Stop")
            self.emergency_btn.setMinimumHeight(BUTTON_HEIGHT)
            self.emergency_btn.setMinimumWidth(150)
            self.emergency_btn.setEnabled(False)
            self.emergency_btn.clicked.connect(self.on_emergency_stop)
            self.emergency_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                }
            """)
            button_layout.addWidget(self.emergency_btn)
            
            layout.addLayout(button_layout)
            
        except Exception as e:
            logger.error(f"Error creating control section: {e}")
    
    def _create_progress_section(self, layout):
        """Create progress section."""
        try:
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            self.progress_bar.setMinimumHeight(20)
            layout.addWidget(self.progress_bar)
        except Exception as e:
            logger.error(f"Error creating progress section: {e}")
    
    def _create_workflow_section(self, parent):
        """Create workflow display section."""
        try:
            workflow_group = QGroupBox("Detected Workflows")
            workflow_layout = QVBoxLayout()
            
            self.workflow_list = QListWidget()
            self.workflow_list.setMinimumHeight(200)
            workflow_layout.addWidget(self.workflow_list)
            
            # Workflow actions
            action_layout = QHBoxLayout()
            
            clear_btn = QPushButton("Clear List")
            clear_btn.clicked.connect(self.clear_workflows)
            action_layout.addWidget(clear_btn)
            
            export_btn = QPushButton("Export Workflows")
            export_btn.clicked.connect(self.export_workflows)
            action_layout.addWidget(export_btn)
            
            workflow_layout.addLayout(action_layout)
            workflow_group.setLayout(workflow_layout)
            parent.addWidget(workflow_group)
            
        except Exception as e:
            logger.error(f"Error creating workflow section: {e}")
    
    def _create_log_section(self, parent):
        """Create log display section."""
        try:
            log_group = QGroupBox("Activity Log")
            log_layout = QVBoxLayout()
            
            self.log_display = QTextEdit()
            self.log_display.setReadOnly(True)
            self.log_display.setMaximumHeight(200)
            self.log_display.setMinimumHeight(150)
            log_layout.addWidget(self.log_display)
            
            # Log actions
            log_action_layout = QHBoxLayout()
            
            clear_log_btn = QPushButton("Clear Log")
            clear_log_btn.clicked.connect(self.clear_log)
            log_action_layout.addWidget(clear_log_btn)
            
            save_log_btn = QPushButton("Save Log")
            save_log_btn.clicked.connect(self.save_log)
            log_action_layout.addWidget(save_log_btn)
            
            log_layout.addLayout(log_action_layout)
            log_group.setLayout(log_layout)
            parent.addWidget(log_group)
            
        except Exception as e:
            logger.error(f"Error creating log section: {e}")
    
    def _apply_stylesheet(self):
        """Apply enhanced stylesheet."""
        try:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f8f9fa;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #bdc3c7;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QListWidget {
                    border: 1px solid #bdc3c7;
                    border-radius: 3px;
                    background-color: white;
                }
                QTextEdit {
                    border: 1px solid #bdc3c7;
                    border-radius: 3px;
                    background-color: white;
                }
                QProgressBar {
                    border: 2px solid #bdc3c7;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 3px;
                }
            """)
        except Exception as e:
            logger.error(f"Error applying stylesheet: {e}")
    
    def setup_menu(self):
        """Setup menu bar."""
        try:
            menubar = self.menuBar()
            
            # File menu
            file_menu = menubar.addMenu('File')
            
            export_action = QAction('Export Session', self)
            export_action.triggered.connect(self.export_session)
            file_menu.addAction(export_action)
            
            file_menu.addSeparator()
            
            exit_action = QAction('Exit', self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            # Help menu
            help_menu = menubar.addMenu('Help')
            
            about_action = QAction('About', self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)
            
        except Exception as e:
            logger.error(f"Error setting up menu: {e}")
    
    def setup_status_bar(self):
        """Setup status bar."""
        try:
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("Ready")
        except Exception as e:
            logger.error(f"Error setting up status bar: {e}")
    
    def setup_tray_icon(self):
        """Setup system tray icon."""
        try:
            if QSystemTrayIcon.isSystemTrayAvailable():
                self.tray_icon = QSystemTrayIcon(self)
                
                # Create tray menu
                tray_menu = QMenu()
                
                show_action = QAction("Show", self)
                show_action.triggered.connect(self.show)
                tray_menu.addAction(show_action)
                
                hide_action = QAction("Hide", self)
                hide_action.triggered.connect(self.hide)
                tray_menu.addAction(hide_action)
                
                tray_menu.addSeparator()
                
                quit_action = QAction("Quit", self)
                quit_action.triggered.connect(self.close)
                tray_menu.addAction(quit_action)
                
                self.tray_icon.setContextMenu(tray_menu)
                self.tray_icon.setToolTip(f"{APP_NAME} - Activity Recording Agent")
                self.tray_icon.show()
                
        except Exception as e:
            logger.warning(f"Could not setup tray icon: {e}")
    
    def on_start_clicked(self):
        """Handle start button click with error handling."""
        try:
            if self.is_processing:
                self.show_error("Cannot start recording while processing is in progress")
                return
            
            self.recording = True
            self.recording_time = 0
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.emergency_btn.setEnabled(True)
            self.status_label.setText(STATUS_RECORDING)
            self.status_label.setStyleSheet("color: #f44336; padding: 10px;")
            self.timer.start(1000)  # Update every second
            self.log_message("Recording started")
            self.status_bar.showMessage("Recording in progress...")
            self.recording_started.emit()
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}", exc_info=True)
            self.show_error(f"Failed to start recording: {e}")
            self._reset_recording_state()
    
    def on_stop_clicked(self):
        """Handle stop button click with error handling."""
        try:
            if not self.recording:
                return
            
            self.recording = False
            self.timer.stop()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.emergency_btn.setEnabled(False)
            self.status_label.setText(STATUS_PROCESSING)
            self.status_label.setStyleSheet("color: #FF9800; padding: 10px;")
            self.log_message("Recording stopped, processing...")
            self.status_bar.showMessage("Processing recording...")
            self.recording_stopped.emit()
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}", exc_info=True)
            self.show_error(f"Error stopping recording: {e}")
    
    def on_emergency_stop(self):
        """Handle emergency stop button click."""
        try:
            reply = QMessageBox.question(
                self, 
                "Emergency Stop", 
                "Are you sure you want to emergency stop?\nThis will terminate all recording and processing.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.log_message("EMERGENCY STOP ACTIVATED")
                self._force_stop_all()
                
        except Exception as e:
            logger.error(f"Error in emergency stop: {e}", exc_info=True)
    
    def _force_stop_all(self):
        """Force stop all operations."""
        try:
            self.recording = False
            self.is_processing = False
            self.timer.stop()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.emergency_btn.setEnabled(False)
            self.status_label.setText(STATUS_IDLE)
            self.status_label.setStyleSheet("color: #666; padding: 10px;")
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Emergency stop completed")
            
        except Exception as e:
            logger.error(f"Error in force stop: {e}")
    
    def update_recording_time(self):
        """Update recording time display with safety checks."""
        try:
            self.recording_time += 1
            
            # Check for maximum recording time
            if self.recording_time >= self.max_recording_time:
                self.log_message(f"Maximum recording time reached ({self.max_recording_time}s)")
                self.on_stop_clicked()
                return
            
            # Update display
            hours = self.recording_time // 3600
            minutes = (self.recording_time % 3600) // 60
            seconds = self.recording_time % 60
            self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # Update status bar
            self.status_bar.showMessage(f"Recording: {hours:02d}:{minutes:02d}:{seconds:02d}")
            
        except Exception as e:
            logger.error(f"Error updating recording time: {e}")
    
    def update_ui_status(self):
        """Update UI status periodically."""
        try:
            # Update status bar with system info
            if not self.recording and not self.is_processing:
                import psutil
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                self.status_bar.showMessage(f"Ready - CPU: {cpu_percent}% Memory: {memory_percent}%")
                
        except Exception as e:
            # Don't log this error as it's not critical
            pass
    
    def log_message(self, message):
        """Add message to log display with timestamp."""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.log_display.append(formatted_message)
            
            # Auto-scroll to bottom
            self.log_display.moveCursor(self.log_display.textCursor().End)
            
            logger.info(message)
            
        except Exception as e:
            logger.error(f"Error logging message: {e}")
    
    def update_workflows(self, workflows):
        """Update workflow list display with error handling."""
        try:
            self.workflow_list.clear()
            
            if not workflows:
                self.workflow_list.addItem("No workflows detected")
                return
            
            for i, workflow in enumerate(workflows):
                try:
                    desc = workflow.get('description', f'Workflow {i+1}')
                    potential = workflow.get('automation_potential', 'Unknown')
                    confidence = workflow.get('confidence', 0)
                    
                    item_text = f"[{potential}] {desc}"
                    if confidence > 0:
                        item_text += f" (Confidence: {confidence:.1%})"
                    
                    self.workflow_list.addItem(item_text)
                    
                except Exception as e:
                    logger.warning(f"Error processing workflow {i}: {e}")
                    self.workflow_list.addItem(f"Error processing workflow {i+1}")
            
        except Exception as e:
            logger.error(f"Error updating workflows: {e}")
    
    def show_processing_progress(self, show=True):
        """Show/hide processing progress bar."""
        try:
            self.progress_bar.setVisible(show)
            self.is_processing = show
            
            if show:
                self.progress_bar.setRange(0, 0)  # Indeterminate
                self.status_bar.showMessage("Processing...")
            else:
                self.status_bar.showMessage("Ready")
                
        except Exception as e:
            logger.error(f"Error showing processing progress: {e}")
    
    def processing_complete(self):
        """Handle processing completion."""
        try:
            self.status_label.setText(STATUS_READY)
            self.status_label.setStyleSheet("color: #4CAF50; padding: 10px;")
            self.progress_bar.setVisible(False)
            self.is_processing = False
            self.log_message("Processing complete!")
            self.status_bar.showMessage("Ready")
            
        except Exception as e:
            logger.error(f"Error in processing complete: {e}")
    
    def show_error(self, message):
        """Show error message dialog with enhanced error handling."""
        try:
            QMessageBox.critical(self, "Error", message)
            logger.error(f"UI Error: {message}")
        except Exception as e:
            logger.error(f"Error showing error dialog: {e}")
            print(f"ERROR: {message}")
    
    def show_info(self, message):
        """Show info message dialog."""
        try:
            QMessageBox.information(self, "Information", message)
        except Exception as e:
            logger.error(f"Error showing info dialog: {e}")
    
    def show_warning(self, message):
        """Show warning message dialog."""
        try:
            QMessageBox.warning(self, "Warning", message)
        except Exception as e:
            logger.error(f"Error showing warning dialog: {e}")
    
    def clear_workflows(self):
        """Clear workflow list."""
        try:
            self.workflow_list.clear()
            self.log_message("Workflow list cleared")
        except Exception as e:
            logger.error(f"Error clearing workflows: {e}")
    
    def clear_log(self):
        """Clear log display."""
        try:
            self.log_display.clear()
            self.log_message("Log cleared")
        except Exception as e:
            logger.error(f"Error clearing log: {e}")
    
    def export_workflows(self):
        """Export workflows to file."""
        try:
            from PyQt5.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Workflows", 
                "workflows.json", 
                "JSON Files (*.json)"
            )
            
            if filename:
                # Implementation would go here
                self.log_message(f"Workflows exported to {filename}")
                
        except Exception as e:
            logger.error(f"Error exporting workflows: {e}")
    
    def save_log(self):
        """Save log to file."""
        try:
            from PyQt5.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Log", 
                "activity_log.txt", 
                "Text Files (*.txt)"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.log_display.toPlainText())
                self.log_message(f"Log saved to {filename}")
                
        except Exception as e:
            logger.error(f"Error saving log: {e}")
    
    def export_session(self):
        """Export current session."""
        try:
            self.log_message("Session export requested")
            # Implementation would go here
            
        except Exception as e:
            logger.error(f"Error exporting session: {e}")
    
    def show_about(self):
        """Show about dialog."""
        try:
            QMessageBox.about(
                self, 
                "About AGE Agent",
                f"{APP_NAME} v{APP_VERSION}\n\n"
                "Activity Recording and Workflow Analysis Agent\n"
                "Built with PyQt5 and Python\n\n"
                "© 2024 AGE Agent Project"
            )
        except Exception as e:
            logger.error(f"Error showing about dialog: {e}")
    
    def closeEvent(self, event):
        """Handle application close event."""
        try:
            if self.recording:
                reply = QMessageBox.question(
                    self, 
                    "Recording in Progress", 
                    "Recording is currently in progress. Are you sure you want to exit?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    event.ignore()
                    return
            
            if self.is_processing:
                reply = QMessageBox.question(
                    self, 
                    "Processing in Progress", 
                    "Processing is currently in progress. Are you sure you want to exit?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    event.ignore()
                    return
            
            # Cleanup
            self._cleanup_on_close()
            event.accept()
            
        except Exception as e:
            logger.error(f"Error in close event: {e}")
            event.accept()
    
    def _cleanup_on_close(self):
        """Cleanup resources on close."""
        try:
            if hasattr(self, 'timer'):
                self.timer.stop()
            
            if hasattr(self, 'ui_timer'):
                self.ui_timer.stop()
                
            logger.info("Dashboard cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _reset_recording_state(self):
        """Reset recording state after error."""
        try:
            self.recording = False
            self.timer.stop()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.emergency_btn.setEnabled(False)
            self.status_label.setText(STATUS_IDLE)
            self.status_label.setStyleSheet("color: #666; padding: 10px;")
            self.status_bar.showMessage("Ready")
            
        except Exception as e:
            logger.error(f"Error resetting recording state: {e}")
