"""
Base service class
Provides abstract interface for all services
"""
from abc import ABC
from typing import Any, Dict



class BaseService(ABC):
    """Abstract base service class"""
    
    def __init__(self, name: str = None):
        
        self.name = name or self.__class__.__name__
       
    
    
    
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute service (template method pattern)
        
        Args:
            data: Input data
            
        Returns:
            Result
        """
        self.log_info(f"Executing {self.name}")
        
        # Validate input
        if not self.validate_input(data):
            raise ValueError(f"Invalid input for {self.name}")
        
        # Process
        result = self.process(data)
        
        self.log_info(f"Completed {self.name}")
        return result
    
    def log_info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)
    
    def log_error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(message)
    
    def log_debug(self, message: str) -> None:
        """Log debug message"""
        self.logger.debug(message)
