import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

class ConfigurationManager:
    """Manages application configuration settings."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_file = config_file
        self.config = {}
        self.defaults = {
            "debug": False,
            "log_level": "INFO",
            "max_connections": 10,
            "timeout": 30,
            "cache_size": 1000
        }
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        self.config = self.defaults.copy()
        
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
                logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        if not self.config_file:
            return False
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config file: {e}")
            return False