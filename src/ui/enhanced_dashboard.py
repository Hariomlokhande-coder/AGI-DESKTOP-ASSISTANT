"""
Enhanced dashboard with detailed task analysis and OCR results display.
"""

import sys
import json
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTextEdit, QTabWidget, 
                             QTableWidget, QTableWidgetItem, QProgressBar,
                             QGroupBox, QScrollArea, QFrame, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QComboBox,
                             QListWidget, QListWidgetItem, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor

from ..error_handling.simple_logger import logger


class EnhancedDashboard(QMainWindow):
    """Enhanced dashboard with comprehensive task analysis display."""
    
    def __init__(self):
        super().__init__()
        self.analysis_data = {}
        self.screenshots = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the enhanced user interface."""
        self.setWindowTitle("AGE Agent - Enhanced Task Analysis Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #3c3c3c;
            }
            QTabBar::tab {
                background-color: #4a4a4a;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTableWidget {
                background-color: #3c3c3c;
                alternate-background-color: #4a4a4a;
                selection-background-color: #0078d4;
                gridline-color: #555555;
                border: 1px solid #555555;
            }
            QHeaderView::section {
                background-color: #555555;
                padding: 4px;
                border: 1px solid #666666;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QTextEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #3c3c3c;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Analysis Overview
        self.create_analysis_panel(splitter)
        
        # Right panel - Detailed Results
        self.create_details_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([400, 1000])
        
    def create_analysis_panel(self, parent):
        """Create the analysis overview panel."""
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        
        # Analysis Summary Group
        summary_group = QGroupBox("Analysis Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        # Workflow Type
        self.workflow_type_label = QLabel("Workflow Type: Not Analyzed")
        self.workflow_type_label.setFont(QFont("Arial", 12, QFont.Bold))
        summary_layout.addWidget(self.workflow_type_label)
        
        # Complexity
        self.complexity_label = QLabel("Complexity: Unknown")
        summary_layout.addWidget(self.complexity_label)
        
        # Automation Score
        self.automation_score_label = QLabel("Automation Score: 0/100")
        summary_layout.addWidget(self.automation_score_label)
        
        # Progress bar for automation score
        self.automation_progress = QProgressBar()
        self.automation_progress.setRange(0, 100)
        summary_layout.addWidget(self.automation_progress)
        
        # Duration
        self.duration_label = QLabel("Duration: Unknown")
        summary_layout.addWidget(self.duration_label)
        
        # Screenshot Count
        self.screenshot_count_label = QLabel("Screenshots: 0")
        summary_layout.addWidget(self.screenshot_count_label)
        
        analysis_layout.addWidget(summary_group)
        
        # Quick Actions Group
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.refresh_btn = QPushButton("Refresh Analysis")
        self.refresh_btn.clicked.connect(self.refresh_analysis)
        actions_layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self.export_results)
        actions_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("Clear Data")
        self.clear_btn.clicked.connect(self.clear_data)
        actions_layout.addWidget(self.clear_btn)
        
        analysis_layout.addWidget(actions_group)
        
        # Applications Used Group
        apps_group = QGroupBox("Applications Detected")
        apps_layout = QVBoxLayout(apps_group)
        
        self.apps_list = QListWidget()
        apps_layout.addWidget(self.apps_list)
        
        analysis_layout.addWidget(apps_group)
        
        # Add to parent
        parent.addWidget(analysis_widget)
        
    def create_details_panel(self, parent):
        """Create the detailed results panel."""
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        details_layout.addWidget(self.tab_widget)
        
        # Task Analysis Tab
        self.create_task_analysis_tab()
        
        # OCR Results Tab
        self.create_ocr_results_tab()
        
        # Workflow Steps Tab
        self.create_workflow_steps_tab()
        
        # Automation Recommendations Tab
        self.create_automation_tab()
        
        # Learning Insights Tab
        self.create_learning_tab()
        
        # Add to parent
        parent.addWidget(details_widget)
        
    def create_task_analysis_tab(self):
        """Create the task analysis tab."""
        task_widget = QWidget()
        task_layout = QVBoxLayout(task_widget)
        
        # Detected Tasks Table
        tasks_group = QGroupBox("Detected Tasks")
        tasks_layout = QVBoxLayout(tasks_group)
        
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(4)
        self.tasks_table.setHorizontalHeaderLabels(["Task Name", "Confidence", "Frequency", "Context"])
        tasks_layout.addWidget(self.tasks_table)
        
        task_layout.addWidget(tasks_group)
        
        # Task Breakdown
        breakdown_group = QGroupBox("Task Breakdown")
        breakdown_layout = QVBoxLayout(breakdown_group)
        
        self.task_breakdown_text = QTextEdit()
        self.task_breakdown_text.setMaximumHeight(200)
        breakdown_layout.addWidget(self.task_breakdown_text)
        
        task_layout.addWidget(breakdown_group)
        
        self.tab_widget.addTab(task_widget, "Task Analysis")
        
    def create_ocr_results_tab(self):
        """Create the OCR results tab."""
        ocr_widget = QWidget()
        ocr_layout = QVBoxLayout(ocr_widget)
        
        # OCR Confidence
        confidence_group = QGroupBox("OCR Analysis Quality")
        confidence_layout = QVBoxLayout(confidence_group)
        
        self.ocr_confidence_label = QLabel("OCR Confidence: 0%")
        confidence_layout.addWidget(self.ocr_confidence_label)
        
        self.ocr_confidence_progress = QProgressBar()
        self.ocr_confidence_progress.setRange(0, 100)
        confidence_layout.addWidget(self.ocr_confidence_progress)
        
        ocr_layout.addWidget(confidence_group)
        
        # Detected Text
        text_group = QGroupBox("Detected Text and UI Elements")
        text_layout = QVBoxLayout(text_group)
        
        self.detected_text = QTextEdit()
        self.detected_text.setMaximumHeight(300)
        text_layout.addWidget(self.detected_text)
        
        ocr_layout.addWidget(text_group)
        
        # UI Elements
        ui_group = QGroupBox("UI Elements Detected")
        ui_layout = QVBoxLayout(ui_group)
        
        self.ui_elements_tree = QTreeWidget()
        self.ui_elements_tree.setHeaderLabels(["Element Type", "Count", "Details"])
        ui_layout.addWidget(self.ui_elements_tree)
        
        ocr_layout.addWidget(ui_group)
        
        self.tab_widget.addTab(ocr_widget, "OCR Results")
        
    def create_workflow_steps_tab(self):
        """Create the workflow steps tab."""
        steps_widget = QWidget()
        steps_layout = QVBoxLayout(steps_widget)
        
        # Workflow Steps
        steps_group = QGroupBox("Workflow Steps")
        steps_layout_v = QVBoxLayout(steps_group)
        
        self.steps_list = QListWidget()
        steps_layout_v.addWidget(self.steps_list)
        
        steps_layout.addWidget(steps_group)
        
        # Repetitive Actions
        repetitive_group = QGroupBox("Repetitive Actions")
        repetitive_layout = QVBoxLayout(repetitive_group)
        
        self.repetitive_list = QListWidget()
        repetitive_layout.addWidget(self.repetitive_list)
        
        steps_layout.addWidget(repetitive_group)
        
        # Efficiency Metrics
        efficiency_group = QGroupBox("Efficiency Metrics")
        efficiency_layout = QVBoxLayout(efficiency_group)
        
        self.efficiency_text = QTextEdit()
        self.efficiency_text.setMaximumHeight(150)
        efficiency_layout.addWidget(self.efficiency_text)
        
        steps_layout.addWidget(efficiency_group)
        
        self.tab_widget.addTab(steps_widget, "Workflow Steps")
        
    def create_automation_tab(self):
        """Create the automation recommendations tab."""
        automation_widget = QWidget()
        automation_layout = QVBoxLayout(automation_widget)
        
        # Automation Opportunities
        opportunities_group = QGroupBox("Automation Opportunities")
        opportunities_layout = QVBoxLayout(opportunities_group)
        
        self.opportunities_list = QListWidget()
        opportunities_layout.addWidget(self.opportunities_list)
        
        automation_layout.addWidget(opportunities_group)
        
        # Recommended Tools
        tools_group = QGroupBox("Recommended Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        self.tools_list = QListWidget()
        tools_layout.addWidget(self.tools_list)
        
        automation_layout.addWidget(tools_group)
        
        # Implementation Details
        implementation_group = QGroupBox("Implementation Details")
        implementation_layout = QVBoxLayout(implementation_group)
        
        self.implementation_text = QTextEdit()
        self.implementation_text.setMaximumHeight(200)
        implementation_layout.addWidget(self.implementation_text)
        
        automation_layout.addWidget(implementation_group)
        
        self.tab_widget.addTab(automation_widget, "Automation")
        
    def create_learning_tab(self):
        """Create the learning insights tab."""
        learning_widget = QWidget()
        learning_layout = QVBoxLayout(learning_widget)
        
        # Skill Areas
        skills_group = QGroupBox("Identified Skill Areas")
        skills_layout = QVBoxLayout(skills_group)
        
        self.skills_list = QListWidget()
        skills_layout.addWidget(self.skills_list)
        
        learning_layout.addWidget(skills_group)
        
        # Improvement Opportunities
        improvement_group = QGroupBox("Improvement Opportunities")
        improvement_layout = QVBoxLayout(improvement_group)
        
        self.improvement_list = QListWidget()
        improvement_layout.addWidget(self.improvement_list)
        
        learning_layout.addWidget(improvement_group)
        
        # Pattern Analysis
        patterns_group = QGroupBox("Pattern Analysis")
        patterns_layout = QVBoxLayout(patterns_group)
        
        self.patterns_text = QTextEdit()
        self.patterns_text.setMaximumHeight(200)
        patterns_layout.addWidget(self.patterns_text)
        
        learning_layout.addWidget(patterns_group)
        
        self.tab_widget.addTab(learning_widget, "Learning Insights")
        
    def update_analysis_data(self, analysis_data):
        """Update the dashboard with new analysis data."""
        try:
            self.analysis_data = analysis_data
            self.update_summary_display()
            self.update_task_analysis()
            self.update_ocr_results()
            self.update_workflow_steps()
            self.update_automation_recommendations()
            self.update_learning_insights()
            logger.info("Dashboard updated with new analysis data")
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
    
    def update_summary_display(self):
        """Update the summary display with analysis data."""
        try:
            # Workflow type
            workflow_type = self.analysis_data.get('workflow_type', 'Unknown')
            self.workflow_type_label.setText(f"Workflow Type: {workflow_type.title()}")
            
            # Complexity
            complexity = self.analysis_data.get('complexity', 'Unknown')
            self.complexity_label.setText(f"Complexity: {complexity.title()}")
            
            # Automation score
            automation_score = self.analysis_data.get('automation_score', 0)
            self.automation_score_label.setText(f"Automation Score: {automation_score}/100")
            self.automation_progress.setValue(automation_score)
            
            # Duration
            session_info = self.analysis_data.get('session_info', {})
            duration = session_info.get('duration', 0)
            duration_text = f"{duration // 60} minutes {duration % 60} seconds" if duration > 60 else f"{duration} seconds"
            self.duration_label.setText(f"Duration: {duration_text}")
            
            # Screenshot count
            screenshot_count = session_info.get('screenshot_count', 0)
            self.screenshot_count_label.setText(f"Screenshots: {screenshot_count}")
            
            # Applications used
            self.apps_list.clear()
            applications = self.analysis_data.get('applications_used', [])
            for app in applications:
                app_name = app.get('name', 'Unknown')
                app_count = app.get('count', 0)
                item_text = f"{app_name} ({app_count} times)"
                self.apps_list.addItem(item_text)
                
        except Exception as e:
            logger.error(f"Error updating summary display: {e}")
    
    def update_task_analysis(self):
        """Update the task analysis display."""
        try:
            # Clear existing data
            self.tasks_table.setRowCount(0)
            
            # Get detected tasks
            tasks = self.analysis_data.get('detected_tasks', [])
            self.tasks_table.setRowCount(len(tasks))
            
            for row, task in enumerate(tasks):
                self.tasks_table.setItem(row, 0, QTableWidgetItem(task.get('name', 'Unknown')))
                confidence = task.get('average_confidence', 0)
                self.tasks_table.setItem(row, 1, QTableWidgetItem(f"{confidence:.2f}"))
                self.tasks_table.setItem(row, 2, QTableWidgetItem(str(task.get('frequency', 0))))
                contexts = task.get('contexts', [])
                context_text = ', '.join(contexts[:3])  # Show first 3 contexts
                self.tasks_table.setItem(row, 3, QTableWidgetItem(context_text))
            
            # Update task breakdown
            task_breakdown = self.analysis_data.get('task_breakdown', {})
            breakdown_text = f"""
Total Tasks Detected: {task_breakdown.get('total_tasks_detected', 0)}
Total Applications Used: {task_breakdown.get('total_applications_used', 0)}

Task Categories:
"""
            for task_name, data in task_breakdown.get('task_categories', {}).items():
                breakdown_text += f"• {task_name}: {data.get('count', 0)} times (confidence: {data.get('average_confidence', 0):.2f})\n"
            
            self.task_breakdown_text.setPlainText(breakdown_text)
            
        except Exception as e:
            logger.error(f"Error updating task analysis: {e}")
    
    def update_ocr_results(self):
        """Update the OCR results display."""
        try:
            # Update OCR confidence
            detailed_analysis = self.analysis_data.get('detailed_analysis', {})
            ocr_confidence = detailed_analysis.get('ocr_confidence', 0)
            self.ocr_confidence_label.setText(f"OCR Confidence: {ocr_confidence:.1%}")
            self.ocr_confidence_progress.setValue(int(ocr_confidence * 100))
            
            # Update detected text
            ocr_analysis = self.analysis_data.get('ocr_analysis', {})
            text_quality = ocr_analysis.get('text_detection_quality', 'Unknown')
            ui_detection = ocr_analysis.get('ui_element_detection', 'Unknown')
            task_accuracy = ocr_analysis.get('task_accuracy', 'Unknown')
            
            ocr_text = f"""
Text Detection Quality: {text_quality}
UI Element Detection: {ui_detection}
Task Accuracy: {task_accuracy}

OCR Analysis completed successfully.
Text and UI elements have been extracted from screenshots for analysis.
"""
            self.detected_text.setPlainText(ocr_text)
            
            # Update UI elements tree
            self.ui_elements_tree.clear()
            # This would be populated with actual UI element data from OCR analysis
            
        except Exception as e:
            logger.error(f"Error updating OCR results: {e}")
    
    def update_workflow_steps(self):
        """Update the workflow steps display."""
        try:
            # Update steps list
            self.steps_list.clear()
            steps = self.analysis_data.get('steps', [])
            for i, step in enumerate(steps, 1):
                self.steps_list.addItem(f"{i}. {step}")
            
            # Update repetitive actions
            self.repetitive_list.clear()
            repetitive_actions = self.analysis_data.get('repetitive_actions', [])
            for action in repetitive_actions:
                self.repetitive_list.addItem(action)
            
            # Update efficiency metrics
            task_breakdown = self.analysis_data.get('task_breakdown', {})
            efficiency_metrics = task_breakdown.get('efficiency_metrics', {})
            
            efficiency_text = f"""
Task Density: {efficiency_metrics.get('task_density', 0)}
Application Switching: {efficiency_metrics.get('application_switching', 0)}
Task Variety: {efficiency_metrics.get('task_variety', 0)}
"""
            self.efficiency_text.setPlainText(efficiency_text)
            
        except Exception as e:
            logger.error(f"Error updating workflow steps: {e}")
    
    def update_automation_recommendations(self):
        """Update the automation recommendations display."""
        try:
            # Update automation opportunities
            self.opportunities_list.clear()
            opportunities = self.analysis_data.get('automation_opportunities', [])
            for opportunity in opportunities:
                self.opportunities_list.addItem(opportunity)
            
            # Update recommended tools
            self.tools_list.clear()
            tools = self.analysis_data.get('recommended_tools', [])
            for tool in tools:
                self.tools_list.addItem(tool)
            
            # Update implementation details
            implementation_difficulty = self.analysis_data.get('implementation_difficulty', 'Unknown')
            time_savings = self.analysis_data.get('time_savings', 'Unknown')
            
            implementation_text = f"""
Implementation Difficulty: {implementation_difficulty.title()}
Estimated Time Savings: {time_savings}

Automation Potential: {self.analysis_data.get('automation_potential', 'Unknown').title()}
Automation Score: {self.analysis_data.get('automation_score', 0)}/100
"""
            self.implementation_text.setPlainText(implementation_text)
            
        except Exception as e:
            logger.error(f"Error updating automation recommendations: {e}")
    
    def update_learning_insights(self):
        """Update the learning insights display."""
        try:
            # Update skill areas
            self.skills_list.clear()
            learning_insights = self.analysis_data.get('learning_insights', {})
            skill_areas = learning_insights.get('skill_areas', [])
            for skill in skill_areas:
                self.skills_list.addItem(skill)
            
            # Update improvement opportunities
            self.improvement_list.clear()
            improvement_opportunities = learning_insights.get('improvement_opportunities', [])
            for opportunity in improvement_opportunities:
                self.improvement_list.addItem(opportunity)
            
            # Update pattern analysis
            pattern_analysis = self.analysis_data.get('pattern_analysis', {})
            patterns_text = f"""
Task Sequences: {', '.join(pattern_analysis.get('task_sequences', []))}
Application Workflows: {', '.join(pattern_analysis.get('application_workflows', []))}

Efficiency Patterns:
"""
            for pattern in pattern_analysis.get('efficiency_patterns', []):
                patterns_text += f"• {pattern}\n"
            
            self.patterns_text.setPlainText(patterns_text)
            
        except Exception as e:
            logger.error(f"Error updating learning insights: {e}")
    
    def refresh_analysis(self):
        """Refresh the analysis data."""
        logger.info("Refreshing analysis data...")
        # This would trigger a re-analysis of the current data
        # For now, just log the action
        pass
    
    def export_results(self):
        """Export the analysis results."""
        try:
            # Create export data
            export_data = {
                'analysis_summary': {
                    'workflow_type': self.analysis_data.get('workflow_type', 'Unknown'),
                    'complexity': self.analysis_data.get('complexity', 'Unknown'),
                    'automation_score': self.analysis_data.get('automation_score', 0),
                    'duration': self.analysis_data.get('session_info', {}).get('duration', 0),
                    'screenshot_count': self.analysis_data.get('session_info', {}).get('screenshot_count', 0)
                },
                'detected_tasks': self.analysis_data.get('detected_tasks', []),
                'applications_used': self.analysis_data.get('applications_used', []),
                'automation_recommendations': {
                    'opportunities': self.analysis_data.get('automation_opportunities', []),
                    'tools': self.analysis_data.get('recommended_tools', []),
                    'difficulty': self.analysis_data.get('implementation_difficulty', 'Unknown')
                },
                'learning_insights': self.analysis_data.get('learning_insights', {}),
                'export_timestamp': self.analysis_data.get('session_info', {}).get('timestamp', '')
            }
            
            # Save to file
            with open('analysis_export.json', 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info("Analysis results exported to analysis_export.json")
            
        except Exception as e:
            logger.error(f"Error exporting results: {e}")
    
    def clear_data(self):
        """Clear all analysis data."""
        self.analysis_data = {}
        self.update_summary_display()
        self.update_task_analysis()
        self.update_ocr_results()
        self.update_workflow_steps()
        self.update_automation_recommendations()
        self.update_learning_insights()
        logger.info("Analysis data cleared")
