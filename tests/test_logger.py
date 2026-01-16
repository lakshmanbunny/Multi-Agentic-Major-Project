"""
Tests for core library logger utilities
"""

import json
import logging
from io import StringIO
import sys
from pathlib import Path

# Add libs/core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "libs" / "core"))

import pytest

from core import setup_logger, ContextLogger, JSONFormatter


def test_setup_logger_basic():
    """Test basic logger setup"""
    logger = setup_logger("test-logger", level="INFO")
    
    assert logger.name == "test-logger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1


def test_setup_logger_levels():
    """Test different logging levels"""
    debug_logger = setup_logger("debug-logger", level="DEBUG")
    assert debug_logger.level == logging.DEBUG
    
    warning_logger = setup_logger("warning-logger", level="WARNING")
    assert warning_logger.level == logging.WARNING
    
    error_logger = setup_logger("error-logger", level="ERROR")
    assert error_logger.level == logging.ERROR


def test_json_formatter_output():
    """Test that JSONFormatter produces valid JSON"""
    # Create logger with JSON formatter
    logger = logging.getLogger("test-json")
    logger.setLevel(logging.INFO)
    
    # Capture output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    # Log a message
    logger.info("Test message")
    
    # Parse the JSON output
    output = stream.getvalue().strip()
    log_data = json.loads(output)
    
    # Validate structure
    assert "timestamp" in log_data
    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Test message"
    assert "module" in log_data
    assert "function" in log_data
    assert "line" in log_data


def test_json_formatter_with_exception():
    """Test JSONFormatter with exception info"""
    logger = logging.getLogger("test-exception")
    logger.setLevel(logging.ERROR)
    
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    try:
        raise ValueError("Test error")
    except ValueError:
        logger.error("Error occurred", exc_info=True)
    
    output = stream.getvalue().strip()
    log_data = json.loads(output)
    
    assert log_data["level"] == "ERROR"
    assert log_data["message"] == "Error occurred"
    assert "exception" in log_data
    assert "ValueError: Test error" in log_data["exception"]


def test_context_logger_basic():
    """Test ContextLogger basic functionality"""
    base_logger = logging.getLogger("test-context")
    base_logger.setLevel(logging.INFO)
    
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())
    base_logger.addHandler(handler)
    
    # Create context logger
    ctx_logger = ContextLogger(
        base_logger,
        service="test-service",
        version="1.0.0"
    )
    
    # Log a message
    ctx_logger.info("Test message", request_id="abc-123")
    
    output = stream.getvalue().strip()
    log_data = json.loads(output)
    
    # Validate context is included
    assert log_data["message"] == "Test message"
    assert log_data["service"] == "test-service"
    assert log_data["version"] == "1.0.0"
    assert log_data["request_id"] == "abc-123"


def test_context_logger_all_levels():
    """Test ContextLogger with all log levels"""
    base_logger = logging.getLogger("test-levels")
    base_logger.setLevel(logging.DEBUG)
    
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())
    base_logger.addHandler(handler)
    
    ctx_logger = ContextLogger(base_logger, component="test")
    
    # Test each level
    ctx_logger.debug("Debug message")
    ctx_logger.info("Info message")
    ctx_logger.warning("Warning message")
    ctx_logger.error("Error message")
    ctx_logger.critical("Critical message")
    
    output = stream.getvalue().strip()
    lines = output.split('\n')
    
    assert len(lines) == 5
    
    levels = [json.loads(line)["level"] for line in lines]
    assert levels == ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def test_logger_no_propagation():
    """Test that logger doesn't propagate to root"""
    logger = setup_logger("no-propagate")
    assert logger.propagate is False


def test_standard_format_output():
    """Test non-JSON format output"""
    logger = setup_logger("standard-format", json_format=False)
    
    # Get the handler
    handler = logger.handlers[0]
    formatter = handler.formatter
    
    # Check it's not JSONFormatter
    assert not isinstance(formatter, JSONFormatter)
    assert "%(asctime)s" in formatter._fmt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
