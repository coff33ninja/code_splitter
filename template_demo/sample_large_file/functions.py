import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

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

