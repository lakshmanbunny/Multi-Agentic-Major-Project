"""
JSON Structured Logger for Auto-DataScientist

Industry-grade logging configuration with JSON formatting for
centralized log aggregation and monitoring.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Outputs logs in JSON format compatible with log aggregation tools
    like ELK Stack, CloudWatch, or Datadog.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from LoggerAdapter or extra kwargs
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        # Add any custom attributes
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info", "extra_fields"
            ]:
                log_data[key] = value
        
        return json.dumps(log_data)


def setup_logger(
    name: str = "auto-data-scientist",
    level: str = "INFO",
    json_format: bool = True
) -> logging.Logger:
    """
    Configure and return a logger instance.
    
    Args:
        name: Logger name (typically module or service name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: If True, use JSON formatting; otherwise use standard format
    
    Returns:
        Configured logger instance
    
    Example:
        >>> logger = setup_logger("orchestrator", level="DEBUG")
        >>> logger.info("Service started", extra={"port": 8000})
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    # Set formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


class ContextLogger:
    """
    Logger wrapper that adds contextual information to all log messages.
    
    Useful for adding service name, request ID, or user ID to all logs.
    
    Example:
        >>> base_logger = setup_logger("orchestrator")
        >>> ctx_logger = ContextLogger(base_logger, service="orchestrator", version="0.1.0")
        >>> ctx_logger.info("Processing request", request_id="123")
    """
    
    def __init__(self, logger: logging.Logger, **context: Any):
        """
        Initialize context logger.
        
        Args:
            logger: Base logger instance
            **context: Key-value pairs to add to all log messages
        """
        self.logger = logger
        self.context = context
    
    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        """Internal method to log with context"""
        extra_fields = {**self.context, **kwargs}
        extra = {"extra_fields": extra_fields}
        getattr(self.logger, level)(message, extra=extra)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with context"""
        self._log("debug", message, **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with context"""
        self._log("info", message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with context"""
        self._log("warning", message, **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with context"""
        self._log("error", message, **kwargs)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with context"""
        self._log("critical", message, **kwargs)


# Default logger instance for convenience
default_logger = setup_logger()
