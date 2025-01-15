"""
File Copier module for monitoring and copying files between directories.
Provides automated file system monitoring and copying functionality with a user interface.
"""

from .file_monitor import FileMonitor
from .file_handler import FileHandler
from .config import load_parameters
from .dependencies import check_and_install_dependencies
from .utils import validate_folder_name, get_valid_folder_name

__version__ = "1.0.0"
__author__ = "Hearsay"

# Define what should be available when using "from file_copier import *"
__all__ = [
    'FileMonitor',
    'FileHandler',
    'load_parameters',
    'check_and_install_dependencies',
    'validate_folder_name',
    'get_valid_folder_name'
]