import os

# Define the path
target_file = "services/browser_agent/src/main.py"
os.makedirs(os.path.dirname(target_file), exist_ok=True)

# The ROBUST content for main.py
new_content = '''
import sys
import os

# --- PATH HACK: FORCE PYTHON TO FIND LOCAL FILES ---
# 1. Add current directory (to find automation.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 2. Add Project Root (to find libs.core)
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)
# ---------------------------------------------------

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from automation import ColabBot  # Now this works!
from libs.core.logger import setup_logger

# Setup Logger
logger = setup_logger("browser_agent")

app = FastAPI(title="Browser Agent", version="0.1.0")

# Initialize the Bot
bot = ColabBot()

class ExecuteRequest(BaseModel):
    code: str
    model_config = ConfigDict(protected_namespaces=())

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "browser_agent"}

@app.post("/execute")
async def execute_code(request: ExecuteRequest):
    """
    Receives code, runs it in Colab (headless or visible), returns screenshot.
    """
    logger.info(f"Executing code in Colab ({len(request.code)} chars)")
    
    try:
        # Run the automation
        result = await bot.execute_code(request.code)
        
        logger.info("Execution successful")
        return result
        
    except Exception as e:
        logger.error(f"Failed to execute code: {str(e)}")
        # Print full stack trace to console for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
'''

with open(target_file, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"✅ Successfully repaired {target_file}")
print("You can now restart the browser agent!")