"""UI widgets and components."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QTextEdit, QListWidget,
    QGroupBox, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class StatusWidget(QWidget):
    """Widget for displaying application status."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        
        self.time_label = QLabel("00:00:00")
        self.time_label.setFont(QFont('Arial', 16, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.time_label)
        self.setLayout(layout)


class ControlWidget(QWidget):
    """Widget for recording controls."""
    
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Recording")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.start_btn.clicked.connect(self.start_clicked.emit)
        
        self.stop_btn = QPushButton("Stop Recording")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        self.setLayout(layout)
    
    def set_recording_state(self, recording):
        """Update button states based on recording status."""
        self.start_btn.setEnabled(not recording)
        self.stop_btn.setEnabled(recording)


class WorkflowWidget(QWidget):
    """Widget for displaying detected workflows."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Detected Workflows")
        title.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(title)
        
        # Workflow list
        self.workflow_list = QListWidget()
        self.workflow_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)
        layout.addWidget(self.workflow_list)
        
        self.setLayout(layout)
    
    def update_workflows(self, workflows):
        """Update the workflow list."""
        self.workflow_list.clear()
        for workflow in workflows:
            desc = workflow.get('description', 'Unknown workflow')
            potential = workflow.get('automation_potential', 'Medium')
            
            # Color code by automation potential
            if potential == 'High':
                color = "#4CAF50"
            elif potential == 'Medium':
                color = "#FF9800"
            else:
                color = "#f44336"
            
            item_text = f"[{potential}] {desc}"
            self.workflow_list.addItem(item_text)


class LogWidget(QWidget):
    """Widget for displaying activity logs."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Activity Log")
        title.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(title)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(150)
        self.log_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                background-color: #f9f9f9;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.log_display)
        
        self.setLayout(layout)
    
    def add_message(self, message):
        """Add a message to the log."""
        self.log_display.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class ProgressWidget(QWidget):
    """Widget for displaying processing progress."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
    
    def show_progress(self, show=True):
        """Show or hide progress bar."""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)  # Indeterminate
    
    def set_progress(self, value, maximum=100):
        """Set progress value."""
        self.progress_bar.setRange(0, maximum)
        self.progress_bar.setValue(value)
