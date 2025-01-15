"""
Configuration management module for the File Copier application.
Handles loading and validation of application parameters from JSON configuration file.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
from colorama import Fore, Style

# Default configuration values
DEFAULT_CONFIG = {
    "base_source_dir": "C:\\Path\\To\\Your\\Source\\Directory",
    "destination_dir": "C:\\Path\\To\\Your\\Destination\\Directory"
}

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass

def get_config_path() -> Path:
    """
    Determine the path to the configuration file.
    Returns the path relative to the main script location.
    """
    script_dir = Path(__file__).parent.parent  # Navigate up from src directory
    return script_dir / 'parameters.json'

def create_default_config(config_path: Path) -> Dict[str, Any]:
    """
    Create a default configuration file if none exists.
    
    Args:
        config_path: Path where the configuration file should be created
        
    Returns:
        Dict containing the default configuration
    """
    try:
        print(f"{Fore.YELLOW}No configuration file found. Creating default parameters.json...{Style.RESET_ALL}")
        config_path.write_text(json.dumps(DEFAULT_CONFIG, indent=4))
        print(f"{Fore.GREEN}Default configuration file created at: {config_path}{Style.RESET_ALL}")
        return DEFAULT_CONFIG
    except Exception as e:
        raise ConfigurationError(f"Failed to create default configuration file: {str(e)}")

def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the configuration dictionary.
    
    Args:
        config: Dictionary containing configuration parameters
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    required_params = ['base_source_dir', 'destination_dir']
    missing_params = [param for param in required_params if param not in config]
    
    if missing_params:
        raise ConfigurationError(f"Missing required parameters: {', '.join(missing_params)}")
        
    # Validate that paths are strings
    for param in ['base_source_dir', 'destination_dir']:
        if not isinstance(config[param], str):
            raise ConfigurationError(f"Parameter '{param}' must be a string")

def load_parameters() -> Dict[str, Any]:
    """
    Load parameters from the configuration file.
    Creates default configuration if none exists.
    
    Returns:
        Dict containing the configuration parameters
        
    Raises:
        ConfigurationError: If configuration cannot be loaded or is invalid
    """
    try:
        config_path = get_config_path()
        
        # Create default config if file doesn't exist
        if not config_path.exists():
            return create_default_config(config_path)
        
        # Load existing configuration
        try:
            config = json.loads(config_path.read_text())
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {str(e)}")
        
        # Validate configuration
        validate_config(config)
        
        return config
        
    except Exception as e:
        print(f"{Fore.RED}Error loading configuration: {str(e)}{Style.RESET_ALL}")
        input("Press Enter to exit...")
        sys.exit(1)

def update_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update the configuration file with new values.
    
    Args:
        updates: Dictionary containing parameters to update
        
    Returns:
        Dict containing the updated configuration
        
    Raises:
        ConfigurationError: If update fails
    """
    try:
        # Load current config
        config = load_parameters()
        
        # Update with new values
        config.update(updates)
        
        # Validate new configuration
        validate_config(config)
        
        # Save updated configuration
        config_path = get_config_path()
        config_path.write_text(json.dumps(config, indent=4))
        
        return config
        
    except Exception as e:
        raise ConfigurationError(f"Failed to update configuration: {str(e)}")

def get_config_template() -> str:
    """
    Get the configuration template as a formatted string.
    Useful for generating the parameters.template.json file.
    
    Returns:
        String containing the JSON template with comments
    """
    template = {
        "_comment": "File Copier Configuration Template",
        "base_source_dir": {
            "value": DEFAULT_CONFIG["base_source_dir"],
            "description": "Base directory containing ComfyUI output folders"
        },
        "destination_dir": {
            "value": DEFAULT_CONFIG["destination_dir"],
            "description": "Directory where files should be copied to"
        }
    }
    
    return json.dumps(template, indent=4)