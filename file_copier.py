import sys
import subprocess
import importlib.util
import json

def check_and_install_dependencies():
    """Check if required packages are installed and install them if needed."""
    required_packages = ['watchdog', 'colorama', 'keyboard']
    
    def is_package_installed(package_name):
        return importlib.util.find_spec(package_name) is not None
    
    def install_package(package_name):
        print(f"Installing {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"Successfully installed {package_name}")
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to install {package_name}")
            return False

    # Check and install missing packages
    missing_packages = [pkg for pkg in required_packages if not is_package_installed(pkg)]
    
    if missing_packages:
        print("Some required packages are missing. Installing them now...")
        for package in missing_packages:
            if not install_package(package):
                print(f"Error: Could not install {package}. Please install it manually using:")
                print(f"pip install {package}")
                input("Press Enter to exit...")
                sys.exit(1)
        
        print("\nAll required packages have been installed. Restarting application...\n")
        # Restart the script to ensure all imports work correctly
        subprocess.call([sys.executable] + sys.argv)
        sys.exit(0)

# Run dependency check before importing other modules
if __name__ == "__main__":
    check_and_install_dependencies()

# Now import the required packages
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import init, Fore, Style
from datetime import datetime
import shutil
import os
import time
import re
import logging
from pathlib import Path
import keyboard
import threading
# Initialize colorama
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_copier.log'),
        logging.StreamHandler()
    ]
)

def load_parameters():
    """Load parameters from the parameters.json file."""
    try:
        # Look for parameters.json in the same directory as the script
        params_path = Path(__file__).parent / 'parameters.json'
        
        if not params_path.exists():
            print(f"{Fore.RED}Error: parameters.json not found in {params_path.parent}{Style.RESET_ALL}")
            print("Creating default parameters.json file...")
            
            # Create default parameters file if it doesn't exist
            default_params = {
                "base_source_dir": "C:\\ComfyUI\\ComfyUI\\output",
                "destination_dir": "\\\\CAMSERVO\\home\\Photos\\AI Art - Others\\ComfyUI\\inbox"
            }
            
            with open(params_path, 'w') as f:
                json.dump(default_params, f, indent=4)
            
            return default_params
            
        with open(params_path, 'r') as f:
            params = json.load(f)
            
        # Validate required parameters
        required_params = ['base_source_dir', 'destination_dir']
        missing_params = [param for param in required_params if param not in params]
        
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
            
        return params
        
    except Exception as e:
        print(f"{Fore.RED}Error loading parameters: {str(e)}{Style.RESET_ALL}")
        input("Press Enter to exit...")
        sys.exit(1)

class FileHandler(FileSystemEventHandler):
    def __init__(self, source_dir, destination_dir):
        self.source_dir = Path(source_dir)
        self.destination_dir = Path(destination_dir)
        self.processing_files = set()

    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_event(event.src_path, "created")

    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_event(event.src_path, "modified")

    def _handle_file_event(self, source_path, event_type):
        source_path = Path(source_path)
        if source_path in self.processing_files:
            return

        self.processing_files.add(source_path)
        try:
            self._copy_file(source_path)
        finally:
            self.processing_files.remove(source_path)

    def _copy_file(self, source_path):
        file_name = source_path.name
        destination_path = self.destination_dir / file_name
        current_time = datetime.now().strftime("%I:%M:%S %p")

        # Wait briefly to ensure file is fully written
        time.sleep(1)

        try:
            # Create destination directory if it doesn't exist
            self.destination_dir.mkdir(parents=True, exist_ok=True)

            # Check if file is still being written to
            initial_size = source_path.stat().st_size
            time.sleep(0.5)
            if initial_size != source_path.stat().st_size:
                return  # File is still being written to, will catch it on next modification

            shutil.copy2(source_path, destination_path)
            self._log_success(current_time, file_name, source_path, destination_path)
            logging.info(f"Successfully copied {file_name}")

        except Exception as e:
            self._log_error(current_time, file_name, str(e))
            logging.error(f"Error copying {file_name}: {str(e)}")

    def _log_success(self, time_str, file_name, source, dest):
        print(f"{Fore.GREEN}[{time_str}] File copied successfully:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}File: {Style.RESET_ALL}{file_name}")
        print(f"{Fore.CYAN}From: {Style.RESET_ALL}{source}")
        print(f"{Fore.CYAN}To:   {Style.RESET_ALL}{dest}\n")

    def _log_error(self, time_str, file_name, error):
        print(f"{Fore.RED}[{time_str}] Error copying {file_name}: {error}{Style.RESET_ALL}\n")

def validate_folder_name(folder_name):
    """Validate the input folder name format."""
    pattern = r'^\d{2}-\d{2}$'
    if not re.match(pattern, folder_name):
        raise ValueError("Folder name must be in format XX-XX (e.g., 01-04)")

def get_valid_folder_name():
    """Get and validate folder name from user with retry logic."""
    while True:
        folder_name = input(f"{Fore.CYAN}Enter the folder name (e.g., 01-04): {Style.RESET_ALL}").strip()
        try:
            validate_folder_name(folder_name)
            return folder_name
        except ValueError as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

class FileMonitor:
    def __init__(self, base_source_dir, destination_dir):
        self.base_source_dir = Path(base_source_dir)
        self.destination_dir = Path(destination_dir)
        self.observer = None
        self.current_source_dir = None
        self.running = True
        self.menu_active = False

    def show_menu(self):
        if self.menu_active:
            return
        
        self.menu_active = True
        print("\n" + "=" * 50)
        print(f"{Fore.YELLOW}Select an option:{Style.RESET_ALL}")
        print(f"1. Change source folder")
        print(f"2. Quit")
        print("=" * 50)
        
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            self.change_source_folder()
        elif choice == "2":
            self.stop()
        
        self.menu_active = False

    def change_source_folder(self):
        # Stop current observer if running
        if self.observer:
            self.observer.stop()
            self.observer.join()

        # Get new folder name and update source directory
        folder_name = get_valid_folder_name()
        self.current_source_dir = self.base_source_dir / folder_name
        
        # Start monitoring new directory
        self.start_monitoring()

    def start_monitoring(self):
        if not self.current_source_dir.exists():
            print(f"{Fore.RED}Error: Source directory does not exist: {self.current_source_dir}{Style.RESET_ALL}")
            return

        # Create the event handler and observer
        event_handler = FileHandler(self.current_source_dir, self.destination_dir)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.current_source_dir), recursive=False)

        # Start monitoring
        self.observer.start()
        current_time = datetime.now().strftime("%I:%M:%S %p")
        print(f"{Fore.GREEN}[{current_time}] Monitoring started:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Source:      {Style.RESET_ALL}{self.current_source_dir}")
        print(f"{Fore.CYAN}Destination: {Style.RESET_ALL}{self.destination_dir}")
        print(f"{Fore.YELLOW}Press ESC to open menu{Style.RESET_ALL}\n")

    def stop(self):
        self.running = False
        if self.observer:
            self.observer.stop()
            current_time = datetime.now().strftime("%I:%M:%S %p")
            print(f"\n{Fore.YELLOW}[{current_time}] Monitoring stopped{Style.RESET_ALL}")
            self.observer.join()

    def run(self):
        # Set up keyboard listener
        keyboard.on_press_key("esc", lambda _: self.show_menu())
        
        try:
            # Get initial folder name and start monitoring
            folder_name = get_valid_folder_name()
            self.current_source_dir = self.base_source_dir / folder_name
            self.start_monitoring()
            
            # Keep the main thread running
            while self.running:
                time.sleep(0.1)
                
        except Exception as e:
            logging.error(f"Fatal error: {str(e)}")
            print(f"{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
        finally:
            self.stop()

if __name__ == "__main__":
    # Load parameters from file
    params = load_parameters()
    
    # Convert paths to Path objects
    BASE_SOURCE_DIR = Path(params['base_source_dir'])
    DESTINATION_DIR = Path(params['destination_dir'])

    try:
        monitor = FileMonitor(BASE_SOURCE_DIR, DESTINATION_DIR)
        monitor.run()
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        print(f"{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
    finally:
        input("Press Enter to exit...")