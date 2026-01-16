import os
import sys

# Define base directory
base_dir = "libs/core"
os.makedirs(base_dir, exist_ok=True)

# 1. CREATE STATE.PY (The missing piece)
state_code = '''
from typing import TypedDict, List, Dict, Any, Optional
from enum import Enum

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DatasetInfo(TypedDict):
    url: str
    file_path: str
    is_public: bool
    description: str

class CodeContext(TypedDict):
    eda_code: str
    model_code: str
    file_name: str

class AgentState(TypedDict):
    messages: List[Dict[str, str]]
    user_goal: str
    dataset_info: DatasetInfo
    research_plan: List[str]
    code_context: CodeContext
    review_feedback: List[str]
    human_approval: ApprovalStatus
    next_step: str
'''

# 2. CREATE LOGGER.PY (The robust logger)
logger_code = '''
import logging
import sys
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        if hasattr(record, "workflow_id"):
            log_obj["workflow_id"] = record.workflow_id
        if hasattr(record, "user_goal"):
            log_obj["user_goal"] = record.user_goal
        return json.dumps(log_obj)

def setup_logger(name: str, level=logging.INFO):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger
'''

# 3. CREATE __INIT__.PY (Exporting both)
init_code = '''
from .logger import setup_logger
from .state import AgentState, ApprovalStatus, DatasetInfo, CodeContext

__all__ = ["setup_logger", "AgentState", "ApprovalStatus", "DatasetInfo", "CodeContext"]
'''

# --- WRITE FILES ---
print("🔧 repairing libs/core/state.py...")
with open(f"{base_dir}/state.py", "w", encoding="utf-8") as f:
    f.write(state_code)

print("🔧 repairing libs/core/logger.py...")
with open(f"{base_dir}/logger.py", "w", encoding="utf-8") as f:
    f.write(logger_code)

print("🔧 repairing libs/core/__init__.py...")
with open(f"{base_dir}/__init__.py", "w", encoding="utf-8") as f:
    f.write(init_code)

print("✅ All Core files repaired.")

# --- VERIFY ---
print("🔍 Verifying imports...")
try:
    # Add root to path for testing
    sys.path.append(os.getcwd())
    from libs.core.state import AgentState
    from libs.core.logger import setup_logger
    print("🎉 SUCCESS! imports are working.")
except Exception as e:
    print(f"❌ ERROR: {e}")