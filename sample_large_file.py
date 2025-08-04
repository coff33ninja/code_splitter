"""
Sample Large Python File for Code Splitter Demonstration

This is a template file that demonstrates various Python constructs
that the code splitter can handle effectively.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

# External library imports (simulated)
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("Requests not available")

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """Represents a user profile with personal information."""
    
    user_id: str
    username: str
    email: str
    created_at: datetime
    preferences: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    login_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user profile to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "preferences": self.preferences,
            "is_active": self.is_active,
            "login_count": self.login_count
        }
    
    def update_preferences(self, new_preferences: Dict[str, Any]) -> None:
        """Update user preferences."""
        self.preferences.update(new_preferences)
        logger.info(f"Updated preferences for user {self.username}")


@dataclass
class DataRecord:
    """Represents a data record with metadata."""
    
    record_id: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    tags: List[str] = field(default_factory=list)
    processed: bool = False
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the record."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def mark_processed(self) -> None:
        """Mark the record as processed."""
        self.processed = True
        logger.info(f"Record {self.record_id} marked as processed")


class DatabaseConnection:
    """Handles database connections and operations."""
    
    def __init__(self, connection_string: str):
        """Initialize database connection."""
        self.connection_string = connection_string
        self.is_connected = False
        self.connection = None
        
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            # Simulated connection logic
            logger.info("Connecting to database...")
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.is_connected:
            self.is_connected = False
            logger.info("Database connection closed")
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a database query."""
        if not self.is_connected:
            raise ConnectionError("Not connected to database")
        
        # Simulated query execution
        logger.info(f"Executing query: {query[:50]}...")
        return [{"result": "sample_data"}]
    
    def insert_record(self, table: str, data: Dict[str, Any]) -> bool:
        """Insert a record into the database."""
        if not self.is_connected:
            raise ConnectionError("Not connected to database")
        
        logger.info(f"Inserting record into {table}")
        return True


class APIClient:
    """Handles external API communications."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """Initialize API client."""
        self.base_url = base_url
        self.api_key = api_key
        self.session = None
        self.timeout = 30
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request to API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        if REQUESTS_AVAILABLE:
            # Simulated API call
            logger.info(f"GET request to {url}")
            return {"status": "success", "data": {}}
        else:
            raise ImportError("Requests library not available")
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request to API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        if REQUESTS_AVAILABLE:
            # Simulated API call
            logger.info(f"POST request to {url}")
            return {"status": "success", "id": "12345"}
        else:
            raise ImportError("Requests library not available")


class DataProcessor:
    """Processes and transforms data records."""
    
    def __init__(self):
        """Initialize data processor."""
        self.processed_count = 0
        self.error_count = 0
        self.processors = {}
        
    def register_processor(self, data_type: str, processor_func) -> None:
        """Register a processor function for a data type."""
        self.processors[data_type] = processor_func
        logger.info(f"Registered processor for {data_type}")
    
    def process_record(self, record: DataRecord) -> bool:
        """Process a single data record."""
        try:
            data_type = record.data.get("type", "unknown")
            
            if data_type in self.processors:
                processor = self.processors[data_type]
                result = processor(record.data)
                record.data.update(result)
                record.mark_processed()
                self.processed_count += 1
                return True
            else:
                logger.warning(f"No processor found for data type: {data_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing record {record.record_id}: {e}")
            self.error_count += 1
            return False
    
    def process_batch(self, records: List[DataRecord]) -> Dict[str, int]:
        """Process a batch of records."""
        results = {"processed": 0, "failed": 0}
        
        for record in records:
            if self.process_record(record):
                results["processed"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"Batch processing complete: {results}")
        return results
    
    def get_statistics(self) -> Dict[str, int]:
        """Get processing statistics."""
        return {
            "total_processed": self.processed_count,
            "total_errors": self.error_count,
            "success_rate": (
                self.processed_count / (self.processed_count + self.error_count)
                if (self.processed_count + self.error_count) > 0 else 0
            )
        }


class CacheManager:
    """Manages in-memory caching of frequently accessed data."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize cache manager."""
        self.max_size = max_size
        self.cache = {}
        self.access_times = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            self.access_times[key] = datetime.now()
            self.hit_count += 1
            return self.cache[key]
        else:
            self.miss_count += 1
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = value
        self.access_times[key] = datetime.now()
    
    def _evict_oldest(self) -> None:
        """Evict the oldest cache entry."""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), 
                        key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.access_times.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate
        }


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


class EventLogger:
    """Logs and manages application events."""
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize event logger."""
        self.log_file = log_file
        self.events = []
        self.max_events = 10000
        
    def log_event(self, event_type: str, message: str, 
                  metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log an application event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "message": message,
            "metadata": metadata or {}
        }
        
        self.events.append(event)
        
        # Keep only recent events
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # Write to file if specified
        if self.log_file:
            self._write_to_file(event)
    
    def _write_to_file(self, event: Dict[str, Any]) -> None:
        """Write event to log file."""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.error(f"Failed to write to log file: {e}")
    
    def get_events(self, event_type: Optional[str] = None, 
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get logged events."""
        events = self.events
        
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        
        if limit:
            events = events[-limit:]
        
        return events
    
    def clear_events(self) -> None:
        """Clear all logged events."""
        self.events.clear()
        logger.info("Event log cleared")


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


# Utility functions
def validate_email(email: str) -> bool:
    """Validate email address format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def generate_id() -> str:
    """Generate a unique identifier."""
    import uuid
    return str(uuid.uuid4())


def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display."""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def calculate_hash(data: str) -> str:
    """Calculate hash of data string."""
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest()


def retry_operation(func, max_retries: int = 3, delay: float = 1.0):
    """Retry an operation with exponential backoff."""
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))


# Main execution
if __name__ == "__main__":
    # Example usage
    app = ApplicationManager("config.json")
    
    try:
        app.start()
        
        # Create sample data
        records = [
            DataRecord(
                record_id=generate_id(),
                data={"type": "user_action", "action": "login"},
                timestamp=datetime.now(),
                source="web_app"
            ),
            DataRecord(
                record_id=generate_id(),
                data={"type": "system_event", "event": "backup_complete"},
                timestamp=datetime.now(),
                source="system"
            )
        ]
        
        # Process data
        results = app.process_data(records)
        print(f"Processing results: {results}")
        
        # Get system status
        status = app.get_system_status()
        print(f"System status: {status}")
        
    finally:
        app.stop()