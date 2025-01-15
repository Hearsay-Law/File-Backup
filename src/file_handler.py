"""
File system event handler module for the File Copier application.
Handles file system events and copying operations.
"""

import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Set, Optional
import time
import os
from colorama import Fore, Style

class ProgressBar:
    """ASCII progress bar for file copying."""
    
    def __init__(self, total_size: int, width: int = 50):
        """
        Initialize progress bar.
        
        Args:
            total_size: Total size in bytes
            width: Width of the progress bar in characters
        """
        self.total_size = total_size
        self.width = width
        self.last_printed_len = 0
    
    def update(self, current_size: int) -> None:
        """
        Update the progress bar display.
        
        Args:
            current_size: Current size in bytes
        """
        percentage = min(100, int((current_size / self.total_size) * 100))
        filled_width = int(self.width * current_size / self.total_size)
        
        # Create the bar
        bar = ('=' * filled_width) + ('-' * (self.width - filled_width))
        
        # Calculate transfer speed
        speed = current_size / 1024  # KB/s
        speed_str = f"{speed:.1f} KB/s" if speed < 1024 else f"{speed/1024:.1f} MB/s"
        
        # Format progress line
        progress_line = f"\r[{bar}] {percentage}% ({speed_str})"
        
        # Clear previous line if it was longer
        if len(progress_line) < self.last_printed_len:
            print('\r' + ' ' * self.last_printed_len, end='')
            
        print(progress_line, end='')
        self.last_printed_len = len(progress_line)
        
        # Print newline if complete
        if percentage == 100:
            print()

def copy_with_progress(src: Path, dst: Path, chunk_size: int = 8192) -> None:
    """
    Copy a file with progress tracking.
    
    Args:
        src: Source file path
        dst: Destination file path
        chunk_size: Size of chunks to copy at once
    """
    total_size = os.path.getsize(src)
    progress = ProgressBar(total_size)
    copied_size = 0
    
    with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
        while True:
            chunk = fsrc.read(chunk_size)
            if not chunk:
                break
            fdst.write(chunk)
            copied_size += len(chunk)
            progress.update(copied_size)
    
    # Copy metadata (timestamps, permissions)
    shutil.copystat(src, dst)

from watchdog.events import FileSystemEventHandler

class FileHandler(FileSystemEventHandler):
    """
    Handler for file system events that copies files from source to destination.
    
    Attributes:
        source_dir (Path): Directory to monitor for new files
        destination_dir (Path): Directory where files should be copied
        processing_files (Set[Path]): Set of files currently being processed
    """
    
    def __init__(self, source_dir: Path, destination_dir: Path):
        """
        Initialize the file handler.
        
        Args:
            source_dir: Directory to monitor for new files
            destination_dir: Directory where files should be copied
        """
        self.source_dir = Path(source_dir)
        self.destination_dir = Path(destination_dir)
        self.processing_files: Set[Path] = set()

    def on_modified(self, event) -> None:
        """
        Handle file modification events.
        
        Args:
            event: File system event object
        """
        if not event.is_directory:
            self._handle_file_event(event.src_path, "modified")

    def _handle_file_event(self, source_path: str, event_type: str) -> None:
        """
        Process a file system event.
        
        Args:
            source_path: Path to the file that triggered the event
            event_type: Type of event ("created" or "modified")
        """
        source_path = Path(source_path)
        
        # Skip if file is already being processed
        if source_path in self.processing_files:
            return

        # Add file to processing set and handle it
        self.processing_files.add(source_path)
        try:
            self._copy_file(source_path)
        finally:
            self.processing_files.remove(source_path)

    def _copy_file(self, source_path: Path) -> None:
        """
        Copy a file from source to destination directory.
        
        Args:
            source_path: Path to the source file
        """
        file_name = source_path.name
        destination_path = self.destination_dir / file_name
        current_time = datetime.now().strftime("%I:%M:%S %p")

        try:
            # Wait briefly to ensure file is fully written
            time.sleep(1)

            # Create destination directory if it doesn't exist
            self.destination_dir.mkdir(parents=True, exist_ok=True)

            # Check if file is still being written to
            initial_size = source_path.stat().st_size
            time.sleep(0.5)
            if initial_size != source_path.stat().st_size:
                return  # File is still being written to, will catch it on next modification

            # Log start of copy
            print(f"{Fore.GREEN}[{current_time}] Copying {file_name}:{Style.RESET_ALL}")
            
            # Copy the file with progress bar
            copy_with_progress(source_path, destination_path)
            
            # Log success
            self._log_success(current_time, file_name, source_path, destination_path)
            logging.info(f"Successfully copied {file_name}")

        except Exception as e:
            self._log_error(current_time, file_name, str(e))
            logging.error(f"Error copying {file_name}: {str(e)}")

    def _log_success(self, time_str: str, file_name: str, source: Path, dest: Path) -> None:
        """
        Log a successful file copy operation.
        
        Args:
            time_str: Current timestamp string
            file_name: Name of the copied file
            source: Source path of the file
            dest: Destination path of the file
        """
        print(f"{Fore.GREEN}[{time_str}] File copied successfully:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}File: {Style.RESET_ALL}{file_name}")
        print(f"{Fore.CYAN}From: {Style.RESET_ALL}{source}")
        print(f"{Fore.CYAN}To:   {Style.RESET_ALL}{dest}\n")

    def _log_error(self, time_str: str, file_name: str, error: str) -> None:
        """
        Log a file copy error.
        
        Args:
            time_str: Current timestamp string
            file_name: Name of the file that failed to copy
            error: Error message
        """
        print(f"{Fore.RED}[{time_str}] Error copying {file_name}: {error}{Style.RESET_ALL}\n")