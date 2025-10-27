# AGE Agent - Complete Running Instructions

## 🚀 Quick Start (Just Run It!)

### Option 1: Double-Click to Run (Easiest)
Simply double-click: **`START.bat`**

### Option 2: Command Line
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run the application
python run_app.py
```

---

## ✅ What's Been Fixed

### Critical Bugs Fixed:
1. ✅ **Recursion Error** - Fixed infinite recursion in helper functions
2. ✅ **Permission Errors** - Fixed recursion in permission checking
3. ✅ **Environment Variables** - Handles missing/invalid .env file gracefully
4. ✅ **Unicode Errors** - Fixed encoding issues in config loading

### Enhanced Components:
1. ✅ **Video Processor** - Frame analysis, format validation, comprehensive error handling
2. ✅ **Audio Processor** - Transcription handling, audio format support, analysis
3. ✅ **Configuration Manager** - Validates settings, handles errors gracefully
4. ✅ **Local LLM** - No API keys required! Works completely offline

---

## 🎯 Key Features

### ✅ No API Keys Required
- Uses **local LLM** for workflow analysis
- Works completely **offline**
- No external API dependencies

### ✅ Comprehensive Error Handling
- All components handle edge cases
- Graceful fallbacks for all operations
- Detailed logging for debugging

### ✅ System Resource Monitoring
- Monitors CPU, memory, and disk usage
- Prevents system overload
- Automatic resource management

### ✅ Robust Pattern Detection
- Detects repetitive workflows
- Generates automation recommendations
- Analyzes complexity and time estimates

---

## 📋 How to Use

### 1. Starting the Application

**Easiest Way:**
```
Double-click START.bat
```

**Command Line:**
```bash
python run_app.py
```

### 2. Recording Your Workflow

1. Click **"Start Recording"** button
2. Perform your computer tasks normally
3. Click **"Stop Recording"** when done
4. Wait for analysis (progress bar will show status)

### 3. Viewing Results

**In the App:**
- View detected workflows in the main window
- See automation recommendations
- Check system resource usage

**Saved Files:**
- `user_data/processed/session_*.json` - Session data
- `user_data/processed/sessions.json` - All sessions
- `user_data/processed/user_patterns.json` - Detected patterns
- `logs/age_agent_*.log` - Detailed logs

---

## 🔧 Requirements

### Already Installed (in venv):
- Python 3.8+
- PyQt5 (GUI)
- OpenCV (Video processing)
- MSS (Screen capture)
- PyAudio (Audio recording)
- librosa (Audio analysis)
- psutil (System monitoring)
- PyYAML (Configuration)
- python-dotenv (Environment variables)

### No External APIs Needed! ✅

---

## 📁 Project Structure

```
age-agent-desktop/
├── src/
│   ├── main.py              # Application entry point
│   ├── app.py               # Main application controller
│   ├── ui/
│   │   └── dashboard.py     # GUI interface
│   ├── capture/
│   │   ├── screen_recorder.py
│   │   ├── audio_recorder.py
│   │   └── device_manager.py
│   ├── processing/
│   │   ├── video_processor.py
│   │   ├── audio_processor.py
│   │   └── json_generator.py
│   ├── llm/
│   │   ├── local_llm.py     # NEW: Local LLM (no API!)
│   │   └── workflow_analyzer.py
│   ├── storage/
│   │   ├── config.py        # Enhanced config manager
│   │   ├── local_storage.py
│   │   └── session_manager.py
│   ├── error_handling/
│   │   ├── exceptions.py
│   │   └── logger.py
│   └── utils/
│       ├── constants.py
│       ├── helpers.py        # Fixed recursion errors
│       └── validators.py     # Fixed recursion errors
├── config/
│   └── config.yaml          # Application settings
├── user_data/               # Created automatically
│   ├── recordings/
│   ├── processed/
│   └── logs/
└── START.bat               # Quick start script
```

---

## ⚙️ Configuration

### Basic Settings (config/config.yaml):

```yaml
recording:
  fps: 1                      # Screenshots per second
  max_duration_minutes: 60    # Max recording time
  audio_sample_rate: 16000    # Audio quality

storage:
  max_storage_gb: 5           # Max disk space

llm:
  provider: local             # Using local LLM (no API keys!)
  timeout_seconds: 30
```

### No Configuration Required!
Default settings work out of the box.

---

## 🐛 Troubleshooting

### "Permission denied" error
- **Windows**: Run as Administrator or grant permissions
- **macOS**: System Preferences > Security & Privacy > Screen Recording
- **Linux**: Check X11/Wayland permissions

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Application won't start
1. Check `logs/age_agent_*.log` for errors
2. Ensure Python 3.8+ is installed
3. Activate virtual environment: `.venv\Scripts\activate`

### No audio recording
- Check microphone permissions
- Verify microphone is not muted
- Application works without audio (video only mode)

---

## 📊 What Gets Analyzed

### Detected Patterns:
- File operations (create, read, write, delete)
- Text operations (typing, editing, formatting)
- Navigation (clicking, scrolling, switching)
- Browser operations (searching, loading pages)
- Development tasks (coding, debugging, testing)
- Communication (email, messaging)
- Multimedia (playback, recording, editing)
- Data analysis (processing, filtering, reporting)

### Generated Insights:
- Workflow description
- Complexity level (simple/moderate/complex)
- Automation potential score (0-100)
- Estimated time
- Recommended automation tools
- Step-by-step workflow breakdown

---

## 🎓 Example Usage

### Scenario: Automating a File Backup Workflow

1. **Start Recording**: Click "Start Recording"
2. **Perform Workflow**: 
   - Open file explorer
   - Navigate to source folder
   - Copy files
   - Navigate to backup folder
   - Paste files
3. **Stop Recording**: Click "Stop Recording"
4. **Review Analysis**:
   - AGE Agent detects: "File operations workflow"
   - Automation potential: "High (85%)"
   - Recommendations: "Python scripts", "Batch automation"
   - Suggested tools: "PowerShell", "Python file operations library"

---

## 📞 Support Files

- `HOW_TO_RUN.md` - Quick start guide
- `README.md` - Full documentation
- `TROUBLESHOOTING.md` - Common issues and solutions
- `ENHANCEMENT_SUMMARY.md` - Technical details

---

## ✨ Summary

✅ **No API Keys** - Uses local LLM  
✅ **Offline Analysis** - All processing locally  
✅ **Fixed All Errors** - Recursion, permissions, encoding  
✅ **Enhanced Components** - Video, audio, config  
✅ **Error Handling** - Comprehensive edge case coverage  
✅ **Easy to Run** - Just run `START.bat` or `python run_app.py`  

**You're ready to use AGE Agent!** 🚀

Just run `python run_app.py` and start recording your workflows!
