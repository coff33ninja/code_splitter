import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from .DataProcessor import DataProcessor
from .CacheManager import CacheManager
from .EventLogger import EventLogger
from .ConfigurationManager import ConfigurationManager
from .DataRecord import DataRecord
from .APIClient import APIClient
from .DatabaseConnection import DatabaseConnection

class ApplicationManager:
    """Main application manager that coordinates all components."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize application manager."""
        self.config = ConfigurationManager(config_file)
        self.db = None
        self.api_client = None
        self.data_processor = DataProcessor()
        self.cache = CacheManager(self.config.get("cache_size", 1000))
        self.event_logger = EventLogger()
        self.is_running = False
        
    def initialize(self) -> bool:
        """Initialize all application components."""
        try:
            # Initialize database connection
            db_config = self.config.get("database", {})
            if db_config:
                self.db = DatabaseConnection(db_config.get("connection_string", ""))
                if not self.db.connect():
                    return False
            
            # Initialize API client
            api_config = self.config.get("api", {})
            if api_config:
                self.api_client = APIClient(
                    api_config.get("base_url", ""),
                    api_config.get("api_key")
                )
            
            self.event_logger.log_event("system", "Application initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            return False
    
    def start(self) -> None:
        """Start the application."""
        if not self.initialize():
            raise RuntimeError("Failed to initialize application")
        
        self.is_running = True
        self.event_logger.log_event("system", "Application started")
        logger.info("Application started successfully")
    
    def stop(self) -> None:
        """Stop the application."""
        self.is_running = False
        
        if self.db:
            self.db.disconnect()
        
        self.cache.clear()
        self.event_logger.log_event("system", "Application stopped")
        logger.info("Application stopped")
    
    def process_data(self, records: List[DataRecord]) -> Dict[str, int]:
        """Process a batch of data records."""
        if not self.is_running:
            raise RuntimeError("Application is not running")
        
        results = self.data_processor.process_batch(records)
        
        self.event_logger.log_event(
            "processing", 
            f"Processed batch of {len(records)} records",
            {"results": results}
        )
        
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "running": self.is_running,
            "database_connected": self.db.is_connected if self.db else False,
            "cache_stats": self.cache.get_stats(),
            "processing_stats": self.data_processor.get_statistics(),
            "recent_events": self.event_logger.get_events(limit=10)
        }