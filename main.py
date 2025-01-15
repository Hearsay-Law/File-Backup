"""
Main entry point for the File Copier application.
Handles initialization, dependency checking, and starts the file monitoring process.
"""

import sys
from pathlib import Path
import keyboard
from colorama import init as colorama_init

# Add the src directory to the Python path
src_path = Path(__file__).parent / 'src'
sys.path.append(str(src_path))

# Import our modules
from src.dependencies import verify_system_requirements
from src.config import load_parameters
from src.file_monitor import FileMonitor
from src.utils import setup_logging
from src import __version__

def main():
    """
    Main entry point for the File Copier application.
    Initializes the application and starts the file monitoring process.
    """
    try:
        # Initialize colorama for cross-platform colored output
        colorama_init()
        
        # Set up logging
        setup_logging()
        
        # Print welcome message
        print(f"\nFile Copier v{__version__}")
        print("=" * 50)
        
        # Verify system requirements (Python version and dependencies)
        verify_system_requirements()
        
        # Load configuration
        params = load_parameters()
        
        # Convert paths to Path objects
        base_source_dir = Path(params['base_source_dir'])
        destination_dir = Path(params['destination_dir'])
        
        # Create and run the file monitor
        monitor = FileMonitor(base_source_dir, destination_dir)
        
        # Register keyboard shortcut for menu
        keyboard.on_press_key("esc", lambda _: monitor.show_menu())
        
        # Start monitoring
        monitor.run()
        
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        sys.exit(0)
        
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        input("Press Enter to exit...")
        sys.exit(1)
        
    finally:
        # Ensure proper cleanup
        keyboard.unhook_all()

if __name__ == "__main__":
    main()