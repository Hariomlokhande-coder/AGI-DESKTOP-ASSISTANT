# Quick Start Guide - AGE Agent

## 🚀 Get Started in 5 Minutes

### Step 1: Setup Environment (2 minutes)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Key (1 minute)

```bash
# Copy environment template
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux

# Edit .env and add your Gemini API key:
GEMINI_API_KEY=your_actual_api_key_here
```

**Get Gemini API Key**: https://makersuite.google.com/app/apikey

### Step 3: Run Application (30 seconds)

```bash
python src/main.py
```

### Step 4: Use the App (1 minute)

1. Click **"Start Recording"**
2. Do some work on your computer (open apps, files, etc.)
3. Wait at least 30 seconds
4. Click **"Stop Recording"**
5. Wait for processing (10-30 seconds)
6. View detected workflows in the list!

## 📦 Building Executable

```bash
# Install cx_Freeze
pip install cx-Freeze

# Build
python setup.py build

# Or use batch file (Windows)
build_exe.bat

# Find executable in: build/exe.win-amd64-3.x/AGEAgent.exe
```

## 🎥 Demo Video Recording Tips

1. **Show the UI**: Start with the main dashboard
2. **Click Start**: Begin recording while explaining
3. **Demo Activity**: Open Excel, type some data, save file
4. **Click Stop**: Stop and wait for processing
5. **Show Results**: Display detected workflows
6. **Explain**: Mention the automation potential

## ⚙️ Common Issues

### Issue: PyAudio installation fails
```bash
# Windows: Download precompiled wheel
# Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install PyAudio‑0.2.13‑cp39‑cp39‑win_amd64.whl
```

### Issue: No audio devices found
- This is OK! App will work without audio
- Just shows warning in logs
- Screen capture still works

### Issue: Screen capture fails
- Run as administrator (Windows)
- Check permissions (Mac: System Preferences > Security > Screen Recording)

### Issue: Gemini API errors
- Verify API key is correct in .env
- Check internet connection
- API is free tier - rate limits may apply

## 📁 What Gets Created

```
age-agent-desktop/
├── user_data/
│   ├── temp/              # Temporary screenshots
│   ├── recordings/        # Audio files
│   ├── processed/         # JSON summaries
│   └── sessions.json      # Session history
└── logs/
    └── age_agent_*.log    # Daily logs
```

## 🎯 For Hackathon Submission

### Required Files:
1. **AGEAgent.exe** (from build/ folder)
2. **demo_video.mp4** (record with OBS/Camtasia)
3. **README.md** (already included)

### Submission Checklist:
- [ ] Executable runs without Python installed
- [ ] Demo video shows full workflow (Start → Record → Stop → Results)
- [ ] Video explains what's happening (voiceover or text)
- [ ] Video is under 5 minutes
- [ ] Tested on clean Windows machine

### Demo Video Script:
```
0:00-0:30: Introduction & showing the UI
0:30-1:00: Starting recording + explaining what it does
1:00-2:30: Doing example tasks (Excel, files, etc.)
2:30-3:00: Stopping recording + showing processing
3:00-4:00: Showing results (workflows detected)
4:00-4:30: Explaining automation potential
4:30-5:00: Conclusion
```

## 🏆 Success!

You're ready to:
✅ Run the application locally
✅ Build the executable
✅ Create a demo video
✅ Submit to the hackathon

Good luck! 🚀
