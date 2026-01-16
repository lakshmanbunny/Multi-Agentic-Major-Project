import os

# Define the file paths
base_dir = "libs/core"
os.makedirs(base_dir, exist_ok=True)

# 1. CONTENT FOR LOGGER.PY
logger_code = '''
import logging
import sys
import json
from datetime import datetime
from typing import Any

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)

def setup_logger(name: str = "auto-data-scientist", level: str = "INFO", json_format: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))
        if json_format:
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
    logger.propagate = False
    return logger
'''

# 2. CONTENT FOR __INIT__.PY
init_code = '''
from .logger import setup_logger
# We will add State later if needed, but for now let's fix the logger first.
__all__ = ["setup_logger"]
'''

# Write the files
with open(f"{base_dir}/logger.py", "w", encoding="utf-8") as f:
    f.write(logger_code)
    print(f"✅ Re-wrote {base_dir}/logger.py")

with open(f"{base_dir}/__init__.py", "w", encoding="utf-8") as f:
    f.write(init_code)
    print(f"✅ Re-wrote {base_dir}/__init__.py")

print("Files repaired. Attempting to verify import...")
try:
    import sys
    # Add local directory to path to simulate the real run
    sys.path.append(os.path.join(os.getcwd(), "libs"))
    from core import setup_logger
    print("🎉 SUCCESS! 'from core import setup_logger' is working now.")
except ImportError as e:
    print(f"❌ STILL FAILING: {e}")
except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")