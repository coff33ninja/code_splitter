"""
Interface module for sample_large_file.

This file provides a clean interface to all classes and functions
that were split into separate modules. Import from this file
to maintain compatibility with existing code.
"""

from .sample_large_file.UserProfile import UserProfile
from .sample_large_file.DataRecord import DataRecord
from .sample_large_file.DatabaseConnection import DatabaseConnection
from .sample_large_file.APIClient import APIClient
from .sample_large_file.DataProcessor import DataProcessor
from .sample_large_file.CacheManager import CacheManager
from .sample_large_file.ConfigurationManager import ConfigurationManager
from .sample_large_file.EventLogger import EventLogger
from .sample_large_file.ApplicationManager import ApplicationManager
from .sample_large_file.functions import validate_email, generate_id, format_timestamp, calculate_hash, retry_operation

__all__ = [
    "UserProfile",
    "DataRecord",
    "DatabaseConnection",
    "APIClient",
    "DataProcessor",
    "CacheManager",
    "ConfigurationManager",
    "EventLogger",
    "ApplicationManager",
    "validate_email",
    "generate_id",
    "format_timestamp",
    "calculate_hash",
    "retry_operation",
]
