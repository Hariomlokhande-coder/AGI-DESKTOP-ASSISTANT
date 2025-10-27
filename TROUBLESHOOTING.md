# Troubleshooting Guide

## Installation Issues

### PyAudio Installation Failed

**Windows**:
```bash
# Option 1: Use pipwin
pip install pipwin
pipwin install pyaudio

# Option 2: Download wheel file
# Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Download appropriate .whl file
pip install PyAudio‑0.2.13‑cp39‑cp39‑win_amd64.whl
```

**macOS**:
```bash
brew install portaudio
pip install pyaudio
```

**Linux**:
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### OpenCV Import Error

```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

### Qt Platform Plugin Error

```bash
pip install --upgrade PyQt5
```

## Runtime Issues

### No Audio Devices Found

**Symptom**: Warning message about no audio devices

**Solution**: This is OK! The app continues without audio. To fix:
- Check if microphone is connected
- Check system audio settings
- Grant microphone permissions
- Try running as administrator

### Screen Capture Permission Denied

**Windows**:
- Run application as Administrator
- Check Windows Privacy Settings > Screen Recording

**macOS**:
- System Preferences > Security & Privacy > Privacy
- Select "Screen Recording"
- Add Python or your app to allowed list

### API Key Not Working

**Check**:
1. Is GEMINI_API_KEY set in .env file?
2. Is .env file in the project root?
3. Is API key valid? Test at: https://makersuite.google.com
4. Internet connection working?

### Executable Not Building

```bash
# Clear build cache
rm -rf build dist

# Reinstall cx_Freeze
pip uninstall cx-Freeze
pip install cx-Freeze

# Try building again
python setup.py build
```

### Application Crashes on Start

**Check logs**:
```bash
# Look in logs/ directory
cat logs/age_agent_*.log
```

**Common fixes**:
1. Delete user_data/ folder and restart
2. Check config/config.yaml is valid
3. Ensure all dependencies installed
4. Try running from command line to see errors

### Processing Takes Too Long

**Solutions**:
1. Reduce screenshot interval in config.yaml
2. Shorten recording duration
3. Check disk space
4. Close other applications

### Workflows Not Detected

**Possible reasons**:
1. Recording too short (try 1+ minutes)
2. API key not configured
3. No internet connection
4. Increase activity during recording

## Configuration Issues

### Config File Not Loading

```bash
# Verify config file exists
ls config/config.yaml

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
```

### Storage Path Errors

**Fix**:
- Ensure paths in config.yaml are valid
- Use forward slashes or double backslashes
- Check write permissions
- Try relative paths: `./user_data`

## Performance Issues

### High CPU Usage

**Solutions**:
- Reduce FPS in config.yaml (try fps: 0.5)
- Increase screenshot interval
- Close unnecessary applications

### High Disk Usage

**Solutions**:
- Enable auto_delete_raw in config.yaml
- Reduce max_storage_gb limit
- Manually delete old files in user_data/

### Memory Leaks

**Solutions**:
- Restart application periodically
- Reduce recording duration
- Update dependencies:
  ```bash
  pip install --upgrade -r requirements.txt
  ```

## Building Executable Issues

### Executable Too Large

**Reduce size**:
```python
# In setup.py, add to build_exe_options:
"excludes": ["tkinter", "matplotlib", "scipy"],
"include_msvcr": False,
```

### Missing Dependencies in Executable

**Add to setup.py**:
```python
"packages": ["missing_package_name"],
"include_files": [("path/to/file", "destination")],
```

### DLL Errors on Other Machines

**Solution**:
- Include Visual C++ Redistributable
- Build on clean VM
- Use PyInstaller as alternative:
  ```bash
  pip install pyinstaller
  pyinstaller --onefile --windowed src/main.py
  ```

## Testing Issues

### Tests Not Running

```bash
# Install pytest
pip install pytest

# Run tests
pytest tests/ -v
```

### Import Errors in Tests

```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%\src         # Windows
```

## Getting Help

### Check Logs

```bash
# View latest log
tail -f logs/age_agent_*.log  # Linux/Mac
type logs\age_agent_*.log    # Windows
```

### Enable Debug Mode

In `src/error_handling/logger.py`, change:
```python
console_handler.setLevel(logging.DEBUG)
```

### Report Issues

Include:
1. Full error message
2. Log file contents
3. Operating system
4. Python version: `python --version`
5. Steps to reproduce

## Still Having Issues?

1. **Check logs**: `logs/age_agent_*.log`
2. **Try fresh install**: Delete venv/ and reinstall
3. **Check permissions**: Run as admin/sudo
4. **Update Python**: Ensure Python 3.8+
5. **Check dependencies**: `pip list`

## Quick Fixes

```bash
# Nuclear option - fresh start
rm -rf venv build dist user_data logs
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```
