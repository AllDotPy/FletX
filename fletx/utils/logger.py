"""
Logging system for FletX
"""

import os
import logging
import sys
import threading
from typing import Optional


####
##      FLETX SHARED LOGGER CLASS
#####
class SharedLogger:
    """FletX Shared Logger."""
    
    _logger: Optional[logging.Logger] = None
    _lock = threading.Lock()
    debug_mode = os.getenv('FLETX_DEBUG','0') == '1'
    _env_log_level = os.getenv('FLETX_LOG_LEVEL', 'NOTSET').upper()
    
    @classmethod
    def get_logger(cls, name: str = "FletX") -> logging.Logger:
        """Gets the static logger (initialized only once)"""

        if cls._logger is None:
            with cls._lock:
                if cls._logger is None:
                    cls._initialize_logger(name)
        return cls._logger
    
    @property
    def logger(self) -> logging.Logger:
        return self.get_logger()
    
    @classmethod
    def _initialize_logger(cls, name: str,debug: bool = False):
        """One-time logger configuration"""

        logger = logging.getLogger(name)
        # Determine level: env overrides, else fallback to debug flag
        level_name = cls._env_log_level if cls._env_log_level in {
            'CRITICAL','ERROR','WARNING','INFO','DEBUG','NOTSET'
        } else 'NOTSET'
        level = getattr(logging, level_name, logging.NOTSET)
        if debug:
            level = logging.DEBUG
        logger.setLevel(level)
        
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            handler.setLevel(level)
            logger.addHandler(handler)
        
        cls._logger = logger
    
    def debug(self, message: str):
        """Log a debug message"""
        if self.debug_mode:
            self.logger.debug(message)
    
    def info(self, message: str):
        """Log an info level message"""
        if self.logger.isEnabledFor(logging.INFO):
            self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning level message"""
        if self.logger.isEnabledFor(logging.WARNING):
            self.logger.warning(message)
    
    def error(self, message: str,* args, **kwargs):
        """Log an error level message"""
        if self.logger.isEnabledFor(logging.ERROR):
            self.logger.error(message)
    
    def critical(self, message: str):
        """Log a critical level message"""
        if self.logger.isEnabledFor(logging.CRITICAL):
            self.logger.critical(message)
