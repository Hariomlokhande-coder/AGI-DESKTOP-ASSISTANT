"""Setup script for building executable."""
import sys
from cx_Freeze import setup, Executable

# Dependencies
build_exe_options = {
    "packages": [
        "cv2",
        "numpy",
        "pyaudio",
        "PyQt5",
        "yaml",
        "mss",
        "google.generativeai"
    ],
    "include_files": [
        ("config", "config"),
    ],
    "excludes": ["tkinter"],
    "optimize": 2,
}

# Base for Windows (no console)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Setup
setup(
    name="AGE Agent",
    version="1.0.0",
    description="Desktop app for workflow automation analysis",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "src/main.py",
            base=base,
            target_name="AGEAgent.exe",
            icon=None
        )
    ]
)
