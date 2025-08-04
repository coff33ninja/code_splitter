import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

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