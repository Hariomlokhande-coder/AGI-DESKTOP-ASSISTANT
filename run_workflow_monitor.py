#!/usr/bin/env python3
"""
Workflow Monitor Launcher
A comprehensive system to monitor active application windows and key actions in real-time.
"""

import sys
import os
import time
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from monitoring.workflow_monitor import WorkflowMonitor
    print("[OK] Workflow Monitor imported successfully")
except ImportError as e:
    print(f"[ERROR] Error importing Workflow Monitor: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install psutil win32gui pynput mss pillow pytesseract opencv-python")
    sys.exit(1)


def check_dependencies():
    """Check if required dependencies are available."""
    dependencies = {
        'psutil': 'psutil',
        'win32gui': 'pywin32',
        'pynput': 'pynput',
        'mss': 'mss',
        'PIL': 'Pillow',
        'cv2': 'opencv-python',
        'pytesseract': 'pytesseract'
    }
    
    # Also check if tesseract executable is available
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
    except Exception:
        print("[WARNING] Tesseract OCR executable not found. OCR features will be limited.")
    
    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[MISSING] {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    return True


def main():
    """Main function to run the workflow monitor."""
    print("=" * 60)
    print("WORKFLOW MONITOR")
    print("Real-time Application and Action Monitoring System")
    print("=" * 60)
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        print("\nPlease install missing dependencies and try again.")
        return
    
    print("\n[OK] All dependencies available")
    
    # Configuration
    print("\nConfiguration:")
    print("- OCR Analysis: Enabled")
    print("- Screenshot Capture: Enabled (every 5 seconds)")
    print("- File Logging: Enabled")
    print("- Real-time Display: Enabled")
    
    print("\nStarting Workflow Monitor...")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 60)
    
    try:
        # Create and start monitor
        monitor = WorkflowMonitor(
            enable_ocr=True,
            enable_screenshots=True,
            screenshot_interval=5.0,
            log_to_file=True
        )
        
        monitor.start_monitoring()
        
        # Keep running until interrupted
        last_stats_time = 0
        while monitor.is_running():
            time.sleep(1)
            
            # Print statistics every 30 seconds
            current_time = time.time()
            if current_time - last_stats_time >= 30:
                stats = monitor.get_statistics()
                runtime = stats.get('runtime_seconds', 0)
                hours, remainder = divmod(runtime, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                print(f"\n[STATS] Runtime: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d} | "
                      f"Events: {stats['total_events']} | "
                      f"Windows: {stats['window_changes']} | "
                      f"Keyboard: {stats['keyboard_events']} | "
                      f"Screenshots: {stats['screenshots_taken']} | "
                      f"OCR: {stats['ocr_analyses']}")
                
                last_stats_time = current_time
    
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'monitor' in locals():
            monitor.stop_monitoring()
        
        print("\n" + "=" * 60)
        print("Workflow monitoring stopped.")
        print("Logs saved to: workflow_log.txt")
        print("Screenshots saved to: screenshots/")
        print("=" * 60)


if __name__ == "__main__":
    main()
