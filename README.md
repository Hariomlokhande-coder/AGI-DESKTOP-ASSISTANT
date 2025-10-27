# Workflow Monitor

A comprehensive real-time monitoring system that tracks active application windows and key actions, providing detailed workflow analysis with OCR capabilities.

## Features

### 🔍 **Real-time Monitoring**
- **Window Tracking**: Monitors active application switches (Excel, Chrome, Notepad, etc.)
- **Keyboard Monitoring**: Captures key actions and shortcuts in real-time
- **Screenshot Capture**: Automatic screenshots for OCR analysis
- **Action Classification**: Categorizes actions into meaningful workflow patterns

### 📊 **Action Labels & Logging**
- `[App Opened]` - New application launched
- `[App Switched]` - Window focus changed
- `[Typed]` - Text input detected
- `[Saved File]` - File save operations
- `[Browsed URL]` - Web navigation
- `[Search]` - Search operations
- `[Calculation]` - Excel formulas and calculations
- `[Email]` - Email operations
- `[Copy/Paste]` - Clipboard operations

### 🧠 **OCR Analysis**
- Extracts text from screenshots
- Detects UI elements and application context
- Identifies specific tasks (data entry, formulas, browsing)
- Provides workflow insights

### 📈 **Workflow Analytics**
- Session tracking and analysis
- Application usage statistics
- Action pattern recognition
- Real-time terminal display with color coding

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (for window monitoring)
- Tesseract OCR (for text recognition)

### Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Tesseract OCR (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract

# Or use winget:
winget install UB-Mannheim.TesseractOCR
```

### Quick Start

```bash
# Run the workflow monitor
python run_workflow_monitor.py
```

## Usage

### Basic Monitoring

The system automatically starts monitoring when you run the launcher. You'll see real-time output like:

```
[App Opened] Microsoft Excel - Budget_2024.xlsx (14:30:15)
[Typed] Entering data in cell A1 (14:30:18)
[Calculation] Formula: =SUM(A1:A10) (14:30:22)
[Saved File] Ctrl+S - Budget_2024.xlsx (14:30:25)
[App Switched] Google Chrome - Gmail (14:30:30)
[Browsed URL] https://mail.google.com (14:30:31)
```

### Configuration

You can customize the monitoring behavior by modifying the `WorkflowMonitor` initialization:

```python
monitor = WorkflowMonitor(
    enable_ocr=True,           # Enable OCR analysis
    enable_screenshots=True,   # Enable screenshot capture
    screenshot_interval=5.0,   # Screenshot interval (seconds)
    log_to_file=True          # Save logs to file
)
```

### Programmatic Usage

```python
from src.monitoring.workflow_monitor import WorkflowMonitor

# Create monitor
monitor = WorkflowMonitor()

# Start monitoring
monitor.start_monitoring()

# Get statistics
stats = monitor.get_statistics()
print(f"Total events: {stats['total_events']}")

# Get recent actions
actions = monitor.get_recent_actions(limit=10)

# Stop monitoring
monitor.stop_monitoring()
```

## Architecture

### Core Components

1. **WindowMonitor** - Tracks active windows and application switches
2. **KeyboardMonitor** - Captures keyboard input and shortcuts
3. **ScreenshotCapture** - Takes screenshots for OCR analysis
4. **OCRAnalyzer** - Extracts text and UI elements from screenshots
5. **ActionClassifier** - Categorizes actions into workflow patterns
6. **RealTimeLogger** - Displays real-time logs with action labels
7. **WorkflowMonitor** - Coordinates all components

### Data Flow

```
Window Events → WindowMonitor → ActionClassifier → RealTimeLogger
Keyboard Events → KeyboardMonitor → ActionClassifier → RealTimeLogger
Screenshots → ScreenshotCapture → OCRAnalyzer → WorkflowAnalyzer → RealTimeLogger
```

## Output Files

- `workflow_log.txt` - Detailed log file with all events
- `screenshots/` - Directory containing captured screenshots
- `workflow_export_YYYYMMDD_HHMMSS.txt` - Exported logs for analysis

## Supported Applications

### Office Applications
- Microsoft Excel (formulas, data entry, charts)
- Microsoft Word (document editing, formatting)
- Microsoft Outlook (email, calendar)
- Microsoft Teams (meetings, chat)

### Web Browsers
- Google Chrome (browsing, searching, form filling)
- Mozilla Firefox (web navigation)
- Microsoft Edge (web activities)

### Development Tools
- Visual Studio Code (code editing, debugging)
- Notepad++ (text editing)
- Command Prompt/PowerShell (system commands)

### System Applications
- File Explorer (file management)
- Calculator (calculations)
- Paint (image editing)

## Action Categories

### App Switching
- `app_opened` - New application launched
- `app_switched` - Window focus changed

### Typing
- `data_entry` - Data input in spreadsheets
- `text_editing` - Document editing
- `formula_input` - Excel formula creation
- `search_input` - Search queries

### File Operations
- `file_save` - Save operations
- `file_open` - Open operations
- `file_close` - Close operations

### Navigation
- `web_browsing` - Website navigation
- `web_search` - Search engine queries
- `url_navigation` - Direct URL access

### Editing
- `copy_operation` - Copy actions
- `paste_operation` - Paste actions
- `format_operation` - Text formatting

### Calculation
- `formula_calculation` - Excel formulas
- `sum_calculation` - Sum operations
- `average_calculation` - Average operations

## Troubleshooting

### Common Issues

1. **Permission Errors**
   - Run as Administrator for full system access
   - Grant necessary permissions for window monitoring

2. **OCR Not Working**
   - Ensure Tesseract is installed and in PATH
   - Check if pytesseract can find tesseract executable

3. **Keyboard Monitoring Issues**
   - Some applications may block low-level keyboard hooks
   - Try running with elevated privileges

4. **Performance Issues**
   - Increase screenshot interval for better performance
   - Disable OCR if not needed
   - Clear old screenshots regularly

### Debug Mode

Enable debug logging by modifying the logger configuration:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Privacy & Security

- All data is processed locally
- No data is sent to external servers
- Screenshots are stored locally and can be deleted
- Logs contain only action metadata, not sensitive content

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `workflow_log.txt`
3. Create an issue with detailed information

---

**Note**: This tool is designed for productivity monitoring and workflow analysis. Please ensure compliance with your organization's policies regarding system monitoring and data collection.