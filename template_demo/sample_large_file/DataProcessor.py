import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from .DataRecord import DataRecord

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