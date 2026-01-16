import asyncio
import sys
import os
import uvicorn

# 1. FORCE THE WINDOWS PROACTOR LOOP (Must be done before ANY other imports)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 2. Add the path so Python finds the service
current_dir = os.path.dirname(os.path.abspath(__file__))
service_path = os.path.join(current_dir, "services", "browser_agent", "src")
if service_path not in sys.path:
    sys.path.append(service_path)
    # Also add libs
    sys.path.append(os.path.join(current_dir, "libs"))
    # Also add root
    sys.path.append(current_dir)

if __name__ == "__main__":
    print("🚀 Starting Browser Agent in ROBUST mode (Windows Fix Applied)...")
    # We turn OFF reload to prevent the loop conflict
    uvicorn.run("services.browser_agent.src.main:app", host="0.0.0.0", port=8001, reload=False)