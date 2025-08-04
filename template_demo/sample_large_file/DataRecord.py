import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

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