# AGE Agent Desktop - Workflow Monitor

A comprehensive real-time workflow monitoring system that tracks your computer activities with detailed, live action labels.

## 🎯 Features

### Real-Time Action Tracking
- **Detailed App Labels**: See exactly which applications you open and switch to (e.g., "Opened Microsoft Excel")
- **Live Action Monitoring**: Track typing, keyboard shortcuts, file operations, and more in real-time
- **Window Title Tracking**: Know which specific files/windows you're working with
- **Keyboard Shortcut Detection**: Automatically detect and label common shortcuts (Ctrl+S, Ctrl+C, etc.)
- **Smart Action Classification**: Categorizes activities into logical groups (typing, file operations, editing, etc.)

### Advanced Monitoring
- **OCR Analysis**: Screenshot analysis to detect workflow patterns
- **Screenshot Capture**: Automatic screenshots every 5 seconds
- **Workflow Pattern Detection**: Identifies repeating patterns in your work
- **Statistics Tracking**: View runtime statistics, event counts, and app usage

### Professional Output
- **Color-Coded Labels**: Different colors for different action types
- **Bold Action Labels**: Easy-to-spot action indicators
- **Timestamp Information**: Every action includes timestamp
- **Clean Console Display**: Professional, readable output

## 📋 Prerequisites

- Windows 10/11
- Python 3.11 or higher
- Administrator permissions for window monitoring and keyboard tracking

## 🚀 Installation

### 1. Clone or Download
```bash
cd D:\exported-assets\age-agent-desktop
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
.\venv\Scripts\activate.bat
```

### 4. Install Dependencies
```bash
pip install pywin32 pynput psutil mss Pillow pytesseract opencv-python
```

### 5. Post-Install Setup (for pywin32)
After installing pywin32, run:
```bash
python .\venv\Scripts\pywin32_postinstall.py -install
```

## 🎮 Usage

### Basic Usage
Simply run the workflow monitor:
```bash
python run_workflow_monitor.py
```

### What You'll See
The monitor will display detailed action labels in real-time:

```
======================================================================
WORKFLOW MONITOR - Real-time Application and Action Tracking
======================================================================

Starting monitoring... Press Ctrl+C to stop

You will see detailed action labels as you work:
  [APP OPENED] Opened Microsoft Excel - Workbook1.xlsx
  [TYPING] Typing in Microsoft Excel: data entry...
  [FILE ACTION] Saved file - Ctrl+S

======================================================================

[APP OPENED] Opened Microsoft Excel - Budget.xlsx (10:30:15)
[TYPING] Typed 25 chars: Q1 Revenue: $125,000 (10:30:22)
[FILE ACTION] Saved file - Ctrl+S (10:30:45)
[APP SWITCHED] Switched to Google Chrome - Search Results (10:31:10)
[TYPING] Typed 35 chars: python workflow automation (10:31:25)
```

### Action Label Types

#### Application Actions
- `[APP OPENED]` - When you open a new application
- `[APP SWITCHED]` - When you switch between applications

#### Keyboard Actions
- `[TYPING]` - Shows typing activity with character count and preview
- `[FILE ACTION]` - File operations (Save, Open, Close)
- `[EDIT ACTION]` - Editing operations (Copy, Paste, Cut, Undo, Redo)

#### System Actions
- `[OCR ANALYSIS]` - Screenshot OCR analysis results
- `[WORKFLOW ANALYSIS]` - Detected workflow patterns

## ⚙️ Configuration

### Modify Settings
Edit `src/monitoring/workflow_monitor.py` to customize:

```python
monitor = WorkflowMonitor(
    enable_ocr=True,              # Enable/disable OCR analysis
    enable_screenshots=True,      # Enable/disable screenshot capture
    screenshot_interval=5.0,      # Seconds between screenshots
    log_to_file=True             # Enable/disable file logging
)
```

### Adjust Action Detection
Modify keyboard patterns in `src/monitoring/keyboard_monitor.py`:

```python
self.action_patterns = {
    'save': ['ctrl+s', 'ctrl+shift+s'],
    'open': ['ctrl+o'],
    'copy': ['ctrl+c'],
    # Add more patterns...
}
```

### App Name Mappings
Customize app display names in `src/monitoring/window_monitor.py`:

```python
self.app_mappings = {
    'excel.exe': 'Microsoft Excel',
    'winword.exe': 'Microsoft Word',
    'chrome.exe': 'Google Chrome',
    # Add more mappings...
}
```

## 📊 Statistics

Every 30 seconds, you'll see a statistics summary:

```
[STATS] Runtime: 00:25:01 | Events: 317 | Windows: 23 | Keyboard: 79 | Screenshots: 215 | OCR: 215
```

- **Runtime**: How long the monitor has been running
- **Events**: Total number of tracked events
- **Windows**: Window/app switches detected
- **Keyboard**: Keyboard events captured
- **Screenshots**: Screenshots taken
- **OCR**: OCR analyses performed

## 📁 Output Files

### Logs
- `workflow_log.txt` - Detailed log file with all actions
- `logs/` - Application logs directory

### Screenshots
- `screenshots/` - All captured screenshots
- Files named: `screenshot_{number}_{timestamp}_{window_title}.png`

### Processed Data
- `user_data/processed/` - Processed JSON data
- Contains workflow analysis results

## 🎨 Action Label Colors

Different action types are color-coded for easy identification:

- **Blue** - App switching
- **Green** - Typing
- **Yellow** - File operations
- **Cyan** - Navigation
- **Magenta** - Editing
- **Red** - Calculations
- **White** - Communication
- **Gray** - System actions

## 🔧 Troubleshooting

### Issue: Import Error
**Error**: `No module named 'win32gui'`
**Solution**: Install pywin32 and run the post-install script:
```bash
pip install pywin32
python .\venv\Scripts\pywin32_postinstall.py -install
```

### Issue: Keyboard Monitoring Not Working
**Error**: Keyboard events not being captured
**Solution**: 
1. Ensure `pynput` is installed: `pip install pynput`
2. Check if another program is capturing keyboard input
3. Run with administrator privileges if needed

### Issue: Screenshots Not Saving
**Error**: Screenshots directory not found
**Solution**: The monitor automatically creates the `screenshots/` directory

### Issue: OCR Not Working
**Error**: OCR analysis failing
**Solution**: 
1. OCR features work without Tesseract but are limited
2. For full OCR, install Tesseract OCR separately
3. The system will continue working without OCR

### Issue: Unicode Errors
**Error**: Character encoding errors
**Solution**: Use the latest version of the code which handles Unicode properly

## 🛑 Stopping the Monitor

Press `Ctrl+C` to gracefully stop the monitor. It will:
- Stop all monitoring threads
- Save all pending logs
- Display final statistics

## 📝 Examples

### Example 1: Excel Workflow
```
[APP OPENED] Opened Microsoft Excel - Budget2024.xlsx (09:15:23)
[TYPING] Typed 42 chars: January Sales: $45,000 (09:15:45)
[TYPING] Typed 38 chars: February Sales: $52,000 (09:16:12)
[EDIT ACTION] Copied - Ctrl+C (09:16:30)
[EDIT ACTION] Pasted - Ctrl+V (09:16:32)
[FILE ACTION] Saved file - Ctrl+S (09:17:01)
```

### Example 2: Browser Research
```
[APP OPENED] Opened Google Chrome - Python Documentation (14:23:10)
[TYPING] Typed 28 chars: python lambda functions (14:23:45)
[APP SWITCHED] Switched to Visual Studio Code - example.py (14:24:12)
[TYPING] Typed 65 chars: data = list(map(lambda x: x*2, range(10))) (14:24:30)
```

## 🔐 Privacy & Security

- All data is stored locally on your computer
- No data is sent to external servers
- Screenshots are stored in the local `screenshots/` directory
- Logs contain only action descriptions, not the full content of what you type

## 📚 File Structure

```
age-agent-desktop/
├── src/
│   ├── monitoring/
│   │   ├── workflow_monitor.py       # Main monitoring system
│   │   ├── window_monitor.py         # Window/app tracking
│   │   ├── keyboard_monitor.py       # Keyboard input tracking
│   │   ├── real_time_logger.py       # Real-time console logger
│   │   ├── screenshot_capture.py     # Screenshot system
│   │   └── action_classifier.py      # Action categorization
│   ├── processing/
│   │   └── ocr_analyzer.py         # OCR analysis
│   └── error_handling/
│       └── simple_logger.py        # Logging system
├── run_workflow_monitor.py           # Main entry point
├── screenshots/                      # Screenshot storage
├── logs/                             # Application logs
└── README.md                         # This file
```

## 🤝 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the logs in `logs/` directory
3. Ensure all dependencies are properly installed

## 📄 License

This project is part of the AGE Agent Desktop suite.

## 🎉 Quick Start Summary

1. **Install**: `pip install pywin32 pynput psutil mss Pillow pytesseract opencv-python`
2. **Setup**: Run `python .\venv\Scripts\pywin32_postinstall.py -install`
3. **Run**: `python run_workflow_monitor.py`
4. **Watch**: See your detailed workflow actions in real-time!

---

**Happy Workflow Tracking! 🚀**

