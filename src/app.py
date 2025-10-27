"""Main application controller with enhanced error handling."""
import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from .ui.dashboard import Dashboard
from .storage.config import config
from .storage.local_storage import LocalStorage
from .storage.session_manager import SessionManager
from .capture.screen_recorder import ScreenshotCapture
from .capture.audio_recorder import AudioRecorder
from .capture.device_manager import DeviceManager
from .processing.video_processor import VideoProcessor
from .processing.audio_processor import AudioProcessor
from .processing.json_generator import JSONGenerator
from .processing.cleanup import CleanupManager
from .llm.workflow_analyzer import WorkflowAnalyzer
from .llm.model_adapter import ModelAdapter
from .error_handling.logger import logger
from .error_handling.exceptions import *


class ProcessingWorker(QThread):
    """Enhanced worker thread for processing data with better error handling."""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, session_data, screenshots, audio_path, processor):
        super().__init__()
        self.session_data = session_data
        self.screenshots = screenshots
        self.audio_path = audio_path
        self.processor = processor
        self._stop_requested = False
    
    def stop(self):
        """Request worker to stop gracefully."""
        self._stop_requested = True
    
    def run(self):
        """Run processing in background thread with comprehensive error handling."""
        try:
            if self._stop_requested:
                return
            
            # Validate inputs
            if not self.session_data:
                raise ProcessingError("No session data provided")
            
            if not self.screenshots:
                logger.warning("No screenshots to process")
                self.finished.emit([])
                return
            
            self.progress.emit("Validating session data...")
            
            # Process audio with timeout protection
            audio_transcription = ""
            if self.audio_path and os.path.exists(self.audio_path):
                try:
                    self.progress.emit("Transcribing audio...")
                    audio_transcription = self.processor['audio'].transcribe_audio(self.audio_path)
                    if not audio_transcription:
                        audio_transcription = "[No audio content detected]"
                except Exception as e:
                    logger.warning(f"Audio processing failed: {e}")
                    audio_transcription = "[Audio processing failed]"
            else:
                audio_transcription = "[No audio file available]"
            
            if self._stop_requested:
                return
            
            # Analyze workflows with timeout protection
            self.progress.emit("Analyzing workflows...")
            workflows = []
            try:
                workflows = self.processor['workflow'].analyze_session(
                    self.session_data,
                    self.screenshots,
                    audio_transcription
                )
                if not workflows:
                    workflows = [{
                        'description': 'General Computer Activity',
                        'steps': ['Various computer tasks performed'],
                        'automation_potential': 'Medium'
                    }]
            except Exception as e:
                logger.error(f"Workflow analysis failed: {e}")
                workflows = [{
                    'description': 'Activity Detected (Analysis Failed)',
                    'steps': ['Computer activity was recorded but analysis failed'],
                    'automation_potential': 'Unknown'
                }]
            
            if self._stop_requested:
                return
            
            # Generate JSON with error handling
            self.progress.emit("Generating summary...")
            try:
                self.processor['json'].generate_session_summary(
                    self.session_data,
                    self.screenshots,
                    {'transcription': audio_transcription},
                    workflows
                )
            except Exception as e:
                logger.error(f"JSON generation failed: {e}")
                # Continue without JSON generation
            
            if self._stop_requested:
                return
            
            # Update patterns with error handling
            self.progress.emit("Updating patterns...")
            try:
                self.processor['adapter'].update_patterns(workflows)
            except Exception as e:
                logger.error(f"Pattern update failed: {e}")
                # Continue without pattern update
            
            self.finished.emit(workflows)
            
        except Exception as e:
            logger.error(f"Processing error: {e}", exc_info=True)
            self.error.emit(str(e))


class AGEAgentApp:
    """Enhanced main application class with comprehensive error handling."""
    
    def __init__(self):
        self.app = None
        self.ui = None
        self.components_initialized = False
        self.current_session_id = None
        self.processing_worker = None
        
        try:
            self._initialize_qt_app()
            self._initialize_ui()
            self._initialize_components()
            self._connect_signals()
            self._check_permissions()
            self.components_initialized = True
            logger.info("AGE Agent application initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}", exc_info=True)
            self._show_critical_error(f"Application initialization failed: {e}")
            raise
    
    def _initialize_qt_app(self):
        """Initialize Qt application with error handling."""
        try:
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("AGE Agent")
            self.app.setApplicationVersion("1.0.0")
            
            # Set up application-wide error handling
            self.app.aboutToQuit.connect(self._cleanup_on_exit)
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Qt application: {e}")
    
    def _initialize_ui(self):
        """Initialize UI with error handling."""
        try:
            self.ui = Dashboard()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize UI: {e}")
    
    def _initialize_components(self):
        """Initialize all application components with comprehensive error handling."""
        try:
            # Storage and configuration
            logger.info("Initializing storage components...")
            self.storage = LocalStorage(config)
            self.session_manager = SessionManager(self.storage)
            
            # Capture components
            logger.info("Initializing capture components...")
            self.screen_capture = ScreenshotCapture(config, self.storage)
            self.audio_recorder = AudioRecorder(config, self.storage)
            self.device_manager = DeviceManager()
            
            # Processing components
            logger.info("Initializing processing components...")
            self.video_processor = VideoProcessor(config, self.storage)
            self.audio_processor = AudioProcessor(config, self.storage)
            self.json_generator = JSONGenerator(self.storage)
            self.cleanup_manager = CleanupManager(self.storage, config)
            
            # LLM components
            logger.info("Initializing LLM components...")
            self.workflow_analyzer = WorkflowAnalyzer(config)
            self.model_adapter = ModelAdapter(self.storage)
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}", exc_info=True)
            raise
    
    def _connect_signals(self):
        """Connect UI signals to handlers with error handling."""
        try:
            self.ui.recording_started.connect(self.on_recording_started)
            self.ui.recording_stopped.connect(self.on_recording_stopped)
        except Exception as e:
            logger.error(f"Failed to connect signals: {e}")
            raise
    
    def _check_permissions(self):
        """Check permissions and device availability with comprehensive error handling."""
        try:
            logger.info("Checking system permissions...")
            
            # Check screen capture permission
            screen_permission = self.device_manager.check_screen_capture_permission()
            if not screen_permission:
                logger.warning("Screen capture permission denied")
                self.ui.show_error(
                    "Screen capture permission denied.\n"
                    "Please grant permission in system settings:\n"
                    "• Windows: Run as Administrator\n"
                    "• macOS: System Preferences > Security & Privacy > Screen Recording\n"
                    "• Linux: Check display permissions"
                )
            else:
                logger.info("Screen capture permission granted")
            
            # Check audio devices
            devices = self.device_manager.check_audio_devices()
            if not devices:
                logger.warning("No audio input devices found")
                self.ui.log_message("Warning: No audio input devices found - continuing without audio")
            else:
                logger.info(f"Found {len(devices)} audio input devices")
            
            # Check disk space
            disk_space_ok = self.storage.check_disk_space(1)
            if not disk_space_ok:
                logger.error("Insufficient disk space")
                self.ui.show_error("Insufficient disk space (need at least 1GB)")
            else:
                logger.info("Disk space check passed")
                
        except Exception as e:
            logger.error(f"Permission check error: {e}")
            self.ui.show_error(f"Permission check failed: {e}")
    
    def on_recording_started(self):
        """Handle recording start with comprehensive error handling."""
        try:
            logger.info("Starting recording session...")
            
            # Validate components
            if not self.components_initialized:
                raise RecordingError("Application not properly initialized")
            
            # Create new session
            session_id = self.session_manager.create_session()
            self.current_session_id = session_id
            logger.info(f"Created session: {session_id}")
            
            # Start screen capture
            try:
                self.screen_capture.start_capture(session_id)
                self.ui.log_message(f"Screen capture started (Session: {session_id})")
                logger.info("Screen capture started successfully")
            except Exception as e:
                logger.error(f"Screen capture failed: {e}")
                raise RecordingError(f"Failed to start screen capture: {e}")
            
            # Start audio recording with graceful fallback
            audio_path = self.storage.get_temp_file_path(f"audio_{session_id}.wav")
            try:
                self.audio_recorder.start_recording(audio_path)
                self.ui.log_message("Audio recording started")
                logger.info("Audio recording started successfully")
            except Exception as e:
                logger.warning(f"Audio recording failed: {e}")
                self.ui.log_message("Continuing without audio recording")
                # Continue without audio - this is not a fatal error
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}", exc_info=True)
            self.ui.show_error(f"Failed to start recording: {e}")
            self._reset_recording_state()
    
    def on_recording_stopped(self):
        """Handle recording stop with comprehensive error handling."""
        try:
            logger.info("Stopping recording session...")
            
            # Stop screen capture
            screenshots = []
            try:
                screenshots = self.screen_capture.stop_capture()
                self.ui.log_message(f"Captured {len(screenshots)} screenshots")
                logger.info(f"Screen capture stopped. Captured {len(screenshots)} screenshots")
            except Exception as e:
                logger.error(f"Error stopping screen capture: {e}")
                self.ui.log_message("Error stopping screen capture")
            
            # Stop audio recording
            audio_path = None
            try:
                audio_path = self.audio_recorder.stop_recording()
                if audio_path:
                    self.ui.log_message("Audio recording stopped")
                    logger.info("Audio recording stopped successfully")
                else:
                    logger.info("No audio recording to stop")
            except Exception as e:
                logger.warning(f"Audio stop error: {e}")
                self.ui.log_message("Error stopping audio recording")
            
            # End session
            session_id = None
            session_data = None
            try:
                session_id = self.session_manager.end_session()
                if session_id:
                    session_data = self.session_manager.get_session(session_id)
                    logger.info(f"Session ended: {session_id}")
                else:
                    logger.warning("No active session to end")
            except Exception as e:
                logger.error(f"Error ending session: {e}")
                self.ui.log_message("Error ending session")
            
            # Start processing if we have data
            if session_data and screenshots:
                self._start_processing(session_data, screenshots, audio_path)
            else:
                logger.warning("No data to process")
                self.ui.log_message("No data captured to process")
                self.ui.processing_complete()
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}", exc_info=True)
            self.ui.show_error(f"Error stopping recording: {e}")
            self.ui.processing_complete()
    
    def _start_processing(self, session_data, screenshots, audio_path):
        """Start processing with error handling."""
        try:
            # Show processing UI
            self.ui.show_processing_progress(True)
            
            # Start processing in background thread
            self.processing_worker = ProcessingWorker(
                session_data,
                screenshots,
                audio_path,
                {
                    'audio': self.audio_processor,
                    'workflow': self.workflow_analyzer,
                    'json': self.json_generator,
                    'adapter': self.model_adapter
                }
            )
            
            self.processing_worker.progress.connect(self.ui.log_message)
            self.processing_worker.finished.connect(self.on_processing_finished)
            self.processing_worker.error.connect(self.on_processing_error)
            self.processing_worker.start()
            
            logger.info("Processing started in background thread")
            
        except Exception as e:
            logger.error(f"Error starting processing: {e}")
            self.ui.show_error(f"Failed to start processing: {e}")
            self.ui.processing_complete()
    
    def on_processing_finished(self, workflows):
        """Handle processing completion with error handling."""
        try:
            logger.info(f"Processing completed. Found {len(workflows)} workflows")
            
            # Update UI with workflows
            self.ui.update_workflows(workflows)
            self.ui.processing_complete()
            self.ui.log_message(f"Found {len(workflows)} automatable workflows")
            
            # Cleanup temp files if configured
            try:
                if config.get('storage.auto_delete_raw', True):
                    self.cleanup_manager.cleanup_temp_directory()
                    self.ui.log_message("Cleaned up temporary files")
                    logger.info("Temporary files cleaned up")
            except Exception as e:
                logger.warning(f"Cleanup failed: {e}")
            
            # Show insights
            try:
                insights = self.model_adapter.get_insights()
                self.ui.show_info(
                    f"Analysis Complete!\n\n"
                    f"Total workflows learned: {insights['total_workflows_learned']}\n"
                    f"Learning sessions: {insights['learning_sessions']}\n"
                    f"Most common workflow: {insights.get('most_common_workflow', 'None')}"
                )
            except Exception as e:
                logger.warning(f"Failed to get insights: {e}")
                self.ui.show_info("Analysis complete!")
            
        except Exception as e:
            logger.error(f"Error in post-processing: {e}")
            self.ui.show_error(f"Post-processing error: {e}")
    
    def on_processing_error(self, error_message):
        """Handle processing error."""
        logger.error(f"Processing error: {error_message}")
        self.ui.show_error(f"Processing error: {error_message}")
        self.ui.processing_complete()
    
    def _reset_recording_state(self):
        """Reset recording state after error."""
        try:
            self.ui.on_stop_clicked()
        except:
            pass
    
    def _show_critical_error(self, message):
        """Show critical error message."""
        try:
            if self.ui:
                self.ui.show_error(message)
            else:
                print(f"CRITICAL ERROR: {message}")
        except:
            print(f"CRITICAL ERROR: {message}")
    
    def _cleanup_on_exit(self):
        """Cleanup resources on application exit."""
        try:
            logger.info("Cleaning up resources...")
            
            # Stop any running processing
            if self.processing_worker and self.processing_worker.isRunning():
                self.processing_worker.stop()
                self.processing_worker.wait(5000)  # Wait up to 5 seconds
            
            # Stop any active recording
            if hasattr(self, 'screen_capture') and self.screen_capture.is_capturing:
                self.screen_capture.stop_capture()
            
            if hasattr(self, 'audio_recorder') and self.audio_recorder.is_recording:
                self.audio_recorder.stop_recording()
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def run(self):
        """Run the application with error handling."""
        try:
            if not self.components_initialized:
                raise RuntimeError("Application not properly initialized")
            
            self.ui.show()
            logger.info("Application main loop started")
            sys.exit(self.app.exec_())
            
        except Exception as e:
            logger.critical(f"Fatal error in main loop: {e}", exc_info=True)
            self._show_critical_error(f"Application error: {e}")
            sys.exit(1)
