"""
Utility functions module for the File Copier application.
Contains logging setup, folder name validation, and other utility functions.
"""

import re
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
from colorama import Fore, Style

class ValidationError(Exception):
    """Custom exception for validation-related errors."""
    pass

def setup_logging(log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_file: Optional path to the log file. If None, uses 'file_copier.log'
    """
    if log_file is None:
        log_file = 'file_copier.log'
        
    # Create logs directory if it doesn't exist
    log_path = Path('logs')
    log_path.mkdir(exist_ok=True)
    
    # Configure logging with both file and console handlers
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path / log_file),
            logging.StreamHandler()
        ]
    )
    
    # Log application start
    logging.info('File Copier application started')

def validate_folder_name(folder_name: str) -> bool:
    """
    Validate the input folder name format (XX-XX).
    
    Args:
        folder_name: Folder name to validate
        
    Returns:
        bool: True if valid, raises ValidationError if invalid
        
    Raises:
        ValidationError: If folder name format is invalid
    """
    pattern = r'^\d{2}-\d{2}$'
    if not re.match(pattern, folder_name):
        raise ValidationError("Folder name must be in format XX-XX (e.g., 01-04)")
    return True

def get_valid_folder_name() -> str:
    """
    Get and validate folder name from user with retry logic.
    
    Returns:
        str: Valid folder name
    """
    while True:
        folder_name = input(f"{Fore.CYAN}Enter the folder name (e.g., 01-04): {Style.RESET_ALL}").strip()
        try:
            validate_folder_name(folder_name)
            return folder_name
        except ValidationError as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    Format a timestamp for display.
    
    Args:
        timestamp: Optional datetime object. If None, uses current time
        
    Returns:
        str: Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%I:%M:%S %p")

def format_file_size(size_in_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_in_bytes: File size in bytes
        
    Returns:
        str: Formatted file size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} TB"

def is_path_accessible(path: Path) -> bool:
    """
    Check if a path is accessible for reading/writing.
    
    Args:
        path: Path to check
        
    Returns:
        bool: True if path is accessible, False otherwise
    """
    try:
        if path.exists():
            # Check read access
            if not path.is_dir():  # File
                return path.is_file() and os.access(path, os.R_OK | os.W_OK)
            else:  # Directory
                # Try to create a temporary file to verify write access
                test_file = path / '.test_access'
                test_file.touch()
                test_file.unlink()
                return True
        else:
            # Try to create the directory
            path.mkdir(parents=True, exist_ok=True)
            return True
    except Exception as e:
        logging.error(f"Error checking path accessibility: {str(e)}")
        return False

def create_backup_filename(original_path: Path) -> Path:
    """
    Create a backup filename for a given path.
    Appends a timestamp to the filename.
    
    Args:
        original_path: Original file path
        
    Returns:
        Path: Backup file path
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return original_path.parent / f"{original_path.stem}_{timestamp}{original_path.suffix}"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing periods and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = 'unnamed_file'
        
    return sanitized