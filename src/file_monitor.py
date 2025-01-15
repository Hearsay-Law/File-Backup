"""
File monitoring module for the File Copier application.
Provides the main file system monitoring functionality.
"""

import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from colorama import Fore, Style
from datetime import datetime
from typing import Optional

from .file_handler import FileHandler
from .utils import get_valid_folder_name, format_timestamp

class FileMonitor:
    """
    Main class for monitoring file system changes and managing the application state.
    
    Attributes:
        base_source_dir (Path): Base directory containing monitored folders
        destination_dir (Path): Directory where files should be copied
        observer (Observer): Watchdog observer instance
        current_source_dir (Path): Currently monitored source directory
        running (bool): Flag indicating if monitoring is active
        menu_active (bool): Flag indicating if menu is currently shown
    """
    
    def __init__(self, base_source_dir: Path, destination_dir: Path):
        """
        Initialize the file monitor.
        
        Args:
            base_source_dir: Base directory containing monitored folders
            destination_dir: Directory where files should be copied
        """
        self.base_source_dir = Path(base_source_dir)
        self.destination_dir = Path(destination_dir)
        self.observer: Optional[Observer] = None
        self.current_source_dir: Optional[Path] = None
        self.running = True
        self.menu_active = False

    def show_menu(self) -> None:
        """Display the application menu and handle user input."""
        if self.menu_active:
            return
        
        self.menu_active = True
        try:
            print("\n" + "=" * 50)
            print(f"{Fore.YELLOW}Select an option:{Style.RESET_ALL}")
            print("1. Change source folder")
            print("2. Quit")
            print("=" * 50)
            
            choice = input("Enter your choice (1 or 2): ").strip()
            
            if choice == "1":
                self.change_source_folder()
            elif choice == "2":
                self.stop()
            
        finally:
            self.menu_active = False

    def change_source_folder(self) -> None:
        """Change the monitored source folder."""
        # Stop current observer if running
        if self.observer:
            self.observer.stop()
            self.observer.join()

        # Get new folder name and update source directory
        folder_name = get_valid_folder_name()
        self.current_source_dir = self.base_source_dir / folder_name
        
        # Start monitoring new directory
        self.start_monitoring()

    def start_monitoring(self) -> None:
        """Start monitoring the current source directory."""
        if not self.current_source_dir or not self.current_source_dir.exists():
            print(f"{Fore.RED}Error: Source directory does not exist: {self.current_source_dir}{Style.RESET_ALL}")
            return

        try:
            # Create the event handler and observer
            event_handler = FileHandler(self.current_source_dir, self.destination_dir)
            self.observer = Observer()
            self.observer.schedule(event_handler, str(self.current_source_dir), recursive=False)

            # Start the observer
            self.observer.start()
            
            # Log monitoring start
            current_time = format_timestamp()
            print(f"{Fore.GREEN}[{current_time}] Monitoring started:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Source:      {Style.RESET_ALL}{self.current_source_dir}")
            print(f"{Fore.CYAN}Destination: {Style.RESET_ALL}{self.destination_dir}")
            print(f"{Fore.YELLOW}Press ESC to open menu{Style.RESET_ALL}\n")
            
            logging.info(f"Started monitoring directory: {self.current_source_dir}")
            
        except Exception as e:
            logging.error(f"Error starting monitoring: {str(e)}")
            print(f"{Fore.RED}Error starting monitoring: {str(e)}{Style.RESET_ALL}")

    def stop(self) -> None:
        """Stop monitoring and clean up resources."""
        self.running = False
        if self.observer:
            self.observer.stop()
            current_time = format_timestamp()
            print(f"\n{Fore.YELLOW}[{current_time}] Monitoring stopped{Style.RESET_ALL}")
            self.observer.join()
            logging.info("Monitoring stopped")

    def run(self) -> None:
        """Main run loop for the file monitor."""
        try:
            # Get initial folder name and start monitoring
            folder_name = get_valid_folder_name()
            self.current_source_dir = self.base_source_dir / folder_name
            self.start_monitoring()
            
            # Keep the main thread running
            while self.running:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logging.info("Application terminated by user")
            print(f"\n{Fore.YELLOW}Application terminated by user{Style.RESET_ALL}")
            
        except Exception as e:
            logging.error(f"Fatal error: {str(e)}")
            print(f"{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
            
        finally:
            self.stop()