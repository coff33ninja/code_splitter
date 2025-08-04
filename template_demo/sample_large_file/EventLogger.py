import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

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