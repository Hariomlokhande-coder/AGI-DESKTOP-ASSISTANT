# How to Run AGE Agent

## Quick Start (No API Keys Required!)

Good news! AGE Agent now uses a **local LLM** for workflow analysis, so you don't need any API keys to run it!

### Step 1: Activate Virtual Environment

```bash
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Run the Application

```bash
python run_app.py
```

That's it! The application will start with the GUI.

## What You'll See

1. **Main Dashboard**: The main window will open with:
   - Start/Stop recording buttons
   - Status indicators
   - Activity log
   - System tray icon (minimize to tray)

2. **First Run**: On first run, the application will:
   - Create necessary directories (`user_data`, `logs`, etc.)
   - Check system permissions
   - Detect available audio/video devices

## Using the Application

### Recording Workflows

1. Click **"Start Recording"**
2. Perform your computer tasks
3. Click **"Stop Recording"** when done
4. The application will automatically:
   - Analyze your workflow using local LLM
   - Detect repetitive patterns
   - Generate automation recommendations
   - Save results to `user_data/processed/`

### Viewing Results

- **Workflows**: See detected workflows in the main window
- **Logs**: Check `logs/age_agent_*.log` for detailed information
- **Session Data**: Results saved in `user_data/processed/session_*.json`

## Requirements

- Python 3.8 or higher
- All dependencies installed (see below)

## Installing Dependencies (First Time)

If you haven't installed dependencies yet:

```bash
pip install -r requirements.txt
```

## Troubleshooting

### Permission Errors

**Windows:**
- Run the application as Administrator if you see permission errors

**macOS:**
- Grant screen recording permission in System Preferences > Security & Privacy
- Grant microphone permission if using audio recording

**Linux:**
- Ensure proper audio and display permissions

### No Audio Devices Found

- Check if your microphone is connected and not muted
- On Windows: Check Privacy Settings > Microphone
- The application will work without audio - it will continue with video only

### Application Crashes on Startup

1. Check the logs: `logs/age_agent_*.log`
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Try running with verbose logging:
   ```bash
   python run_app.py --verbose
   ```

## Features

✅ **No API Keys Required** - Uses local LLM for analysis
✅ **Offline Analysis** - All processing happens locally
✅ **Pattern Detection** - Automatically detects repetitive workflows
✅ **Automation Recommendations** - Suggests tools and approaches
✅ **Multiple Data Sources** - Screenshots, audio, and user activity
✅ **Comprehensive Logging** - Detailed logs for debugging
✅ **Error Handling** - Graceful handling of all edge cases

## Configuration

Edit `config/config.yaml` to customize:
- Recording FPS
- Audio sample rate
- Storage limits
- Processing timeouts
- UI settings

## Need Help?

- Check `TROUBLESHOOTING.md` for common issues
- Review logs in `logs/age_agent_*.log`
- See `README.md` for detailed documentation

Enjoy using AGE Agent! 🚀
