"""
Dependency management module for the File Copier application.
Handles checking and installing required Python packages.
"""

import sys
import subprocess
import importlib.util
from typing import List, Set
from colorama import Fore, Style

class DependencyError(Exception):
    """Custom exception for dependency-related errors."""
    pass

# Define required packages and their minimum versions if needed
REQUIRED_PACKAGES = {
    'watchdog': None,  # None means any version is acceptable
    'colorama': None,
    'keyboard': None
}

def is_package_installed(package_name: str) -> bool:
    """
    Check if a Python package is installed.
    
    Args:
        package_name: Name of the package to check
        
    Returns:
        bool: True if package is installed, False otherwise
    """
    return importlib.util.find_spec(package_name) is not None

def get_missing_packages() -> Set[str]:
    """
    Get a set of required packages that are not installed.
    
    Returns:
        Set of package names that need to be installed
    """
    return {pkg for pkg, version in REQUIRED_PACKAGES.items() 
            if not is_package_installed(pkg)}

def install_package(package_name: str) -> bool:
    """
    Install a Python package using pip.
    
    Args:
        package_name: Name of the package to install
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    print(f"{Fore.YELLOW}Installing {package_name}...{Style.RESET_ALL}")
    
    # Construct the package specification
    package_spec = package_name
    if REQUIRED_PACKAGES[package_name]:
        package_spec += f"=={REQUIRED_PACKAGES[package_name]}"
    
    try:
        # Run pip install with the package specification
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            package_spec
        ])
        print(f"{Fore.GREEN}Successfully installed {package_name}{Style.RESET_ALL}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Failed to install {package_name}: {str(e)}{Style.RESET_ALL}")
        return False

def check_and_install_dependencies() -> bool:
    """
    Check if required packages are installed and install them if needed.
    
    Returns:
        bool: True if all dependencies are satisfied, False otherwise
        
    Raises:
        DependencyError: If dependencies cannot be satisfied
    """
    try:
        missing_packages = get_missing_packages()
        
        if not missing_packages:
            return True
            
        print(f"{Fore.YELLOW}Missing required packages: {', '.join(missing_packages)}{Style.RESET_ALL}")
        print("Installing missing packages...")
        
        failed_packages = []
        for package in missing_packages:
            if not install_package(package):
                failed_packages.append(package)
        
        if failed_packages:
            error_msg = (
                f"Failed to install the following packages: {', '.join(failed_packages)}\n"
                "Please install them manually using:\n"
            )
            for package in failed_packages:
                error_msg += f"pip install {package}\n"
            raise DependencyError(error_msg)
        
        print(f"\n{Fore.GREEN}All required packages have been installed.{Style.RESET_ALL}")
        
        # If we installed any packages, we should restart the application
        if missing_packages:
            print(f"\n{Fore.YELLOW}Restarting application to load new packages...{Style.RESET_ALL}")
            subprocess.call([sys.executable] + sys.argv)
            sys.exit(0)
            
        return True
        
    except Exception as e:
        raise DependencyError(f"Error checking/installing dependencies: {str(e)}")

def check_python_version(minimum_version: tuple = (3, 7)) -> None:
    """
    Check if the current Python version meets the minimum requirement.
    
    Args:
        minimum_version: Tuple of (major, minor) version numbers
        
    Raises:
        DependencyError: If Python version is too old
    """
    current_version = sys.version_info[:2]
    if current_version < minimum_version:
        raise DependencyError(
            f"Python {minimum_version[0]}.{minimum_version[1]} or higher is required. "
            f"You are using Python {current_version[0]}.{current_version[1]}"
        )

def verify_system_requirements() -> None:
    """
    Verify all system requirements are met.
    This includes Python version and required packages.
    
    Raises:
        DependencyError: If system requirements are not met
    """
    try:
        # Check Python version first
        check_python_version()
        
        # Then check and install package dependencies
        check_and_install_dependencies()
        
    except DependencyError as e:
        print(f"{Fore.RED}System requirements not met: {str(e)}{Style.RESET_ALL}")
        input("Press Enter to exit...")
        sys.exit(1)