# """
# Auto-DataScientist Core Library

# Shared components for the Auto-DataScientist microservices system.
# Includes state models, logging utilities, and common helpers.
# """

# from .logger import ContextLogger, JSONFormatter, default_logger, setup_logger
# from .state import AgentState, ApprovalStatus, CodeContext, DatasetInfo

# __all__ = [
#     # State models
#     "AgentState",
#     "DatasetInfo",
#     "CodeContext",
#     "ApprovalStatus",
#     # Logger utilities
#     "setup_logger",
#     "JSONFormatter",
#     "ContextLogger",
#     "default_logger",
# ]

# __version__ = "0.1.0"

# libs/core/__init__.py

# Import from the specific files
from .logger import setup_logger
from .state import AgentState

# This makes them available when someone says "from core import setup_logger"
__all__ = ["setup_logger", "AgentState"]