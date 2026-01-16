import os

target_file = "services/browser_agent/src/main.py"
os.makedirs(os.path.dirname(target_file), exist_ok=True)

# We are overwriting main.py with the WINDOWS FIX included
new_content = '''
import sys
import os
import asyncio

# --- WINDOWS FIX: FORCE PROACTOR LOOP ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# ----------------------------------------

# --- PATH HACK: FORCE PYTHON TO FIND LOCAL FILES ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from automation import ColabBot
from libs.core.logger import setup_logger

logger = setup_logger("browser_agent")
app = FastAPI(title="Browser Agent", version="0.1.0")
bot = ColabBot()

class ExecuteRequest(BaseModel):
    code: str
    model_config = ConfigDict(protected_namespaces=())

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "browser_agent"}

@app.post("/execute")
async def execute_code(request: ExecuteRequest):
    logger.info(f"Executing code in Colab ({len(request.code)} chars)")
    try:
        result = await bot.execute_code(request.code)
        logger.info("Execution successful")
        return result
    except Exception as e:
        logger.error(f"Failed to execute code: {str(e)}")
        # If it's the "Browser Closed" error, we might need to login again
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # loop="asyncio" is safer for Windows + Playwright
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True, loop="asyncio")
'''

with open(target_file, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"✅ patched {target_file} with Windows Asyncio Fix")