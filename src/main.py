"""Entry point for AGE Agent application."""
import sys
import os
import traceback
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import AGEAgentApp
    from error_handling.logger import logger
except ImportError as e:
    print(f"Failed to import required modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def check_system_requirements():
    """Check system requirements before starting."""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            raise RuntimeError(f"Python 3.8+ required, found {sys.version}")
        
        # Check if we're in the right directory
        if not os.path.exists("config/config.yaml"):
            raise RuntimeError("config/config.yaml not found. Please run from project root.")
        
        # Check disk space
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free / (1024**3)
        if free_gb < 1:
            raise RuntimeError(f"Insufficient disk space: {free_gb:.1f}GB available, need at least 1GB")
        
        logger.info(f"System requirements check passed. Free disk space: {free_gb:.1f}GB")
        return True
        
    except Exception as e:
        print(f"System requirements check failed: {e}")
        return False


def handle_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions globally."""
    if issubclass(exc_type, KeyboardInterrupt):
        logger.info("Application interrupted by user")
        sys.exit(0)
    
    logger.critical(
        f"Uncaught exception: {exc_type.__name__}: {exc_value}",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    # Try to show error to user if possible
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance()
        if app:
            QMessageBox.critical(
                None, 
                "Fatal Error", 
                f"An unexpected error occurred:\n{exc_value}\n\nCheck logs for details."
            )
    except:
        pass  # If we can't show GUI, just log it
    
    sys.exit(1)


def main():
    """Main entry point with comprehensive error handling."""
    # Set up global exception handler
    sys.excepthook = handle_uncaught_exceptions
    
    try:
        logger.info("=" * 50)
        logger.info("AGE Agent Starting...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info("=" * 50)
        
        # Check system requirements
        if not check_system_requirements():
            sys.exit(1)
        
        # Initialize and run application
        logger.info("Initializing AGE Agent application...")
        app = AGEAgentApp()
        
        logger.info("Starting application main loop...")
        app.run()
        
        logger.info("AGE Agent shutdown complete")
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user (Ctrl+C)")
        sys.exit(0)
    except ImportError as e:
        logger.critical(f"Import error - missing dependencies: {e}")
        print("\n" + "="*60)
        print("MISSING DEPENDENCIES")
        print("="*60)
        print("Please install required packages:")
        print("pip install -r requirements.txt")
        print("\nIf PyAudio fails to install:")
        print("Windows: pip install pipwin && pipwin install pyaudio")
        print("macOS: brew install portaudio && pip install pyaudio")
        print("Linux: sudo apt-get install portaudio19-dev && pip install pyaudio")
        print("="*60)
        sys.exit(1)
    except PermissionError as e:
        logger.critical(f"Permission error: {e}")
        print("\n" + "="*60)
        print("PERMISSION ERROR")
        print("="*60)
        print("Please run with appropriate permissions:")
        print("- Windows: Run as Administrator")
        print("- macOS: Grant screen recording permissions in System Preferences")
        print("- Linux: Check file permissions and audio device access")
        print("="*60)
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Fatal error during startup: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        print("Check logs for detailed information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
