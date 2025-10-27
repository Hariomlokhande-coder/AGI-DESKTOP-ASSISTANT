"""AGE Agent Application Launcher"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import from src
from src.app import AGEAgentApp
from src.error_handling.logger import logger


def main():
    """Launch the AGE Agent application."""
    try:
        print("Starting AGE Agent...")
        logger.info("AGE Agent launched")
        
        app = AGEAgentApp()
        app.run()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        logger.critical(f"Fatal error: {e}", exc_info=True)
        
        print("Troubleshooting:")
        print("1. Check if .env file exists with GEMINI_API_KEY")
        print("2. Ensure venv is activated: venv\\Scripts\\activate")
        print("3. Check logs/age_agent_*.log for details\n")
        
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
