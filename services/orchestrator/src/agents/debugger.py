"""
Debugger Agent - Automated Code Fixing

This agent uses LLM to analyze error logs and automatically fix broken Python code.
"""

import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from libs.core.state import AgentState
from libs.core.logger import setup_logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = setup_logger("debugger_agent", level="INFO")


def debugger_node(state: AgentState) -> AgentState:
    """
    Debugger Agent that analyzes errors and fixes code.
    
    Args:
        state: Current workflow state with broken code and error logs
    
    Returns:
        Updated state with fixed code
    """
    combined_code = state.get("combined_code", "")
    execution_logs = state.get("execution_logs", "")
    
    logger.info("🔧 Debugger Agent started")
    
    # Validation: Check if we have the necessary inputs
    if not combined_code or len(combined_code.strip()) < 10:
        logger.warning("⚠️ No code to debug")
        return state
    
    if not execution_logs or len(execution_logs.strip()) < 10:
        logger.warning("⚠️ No error logs to analyze")
        return state
    
    logger.info(f"Analyzing error in {len(combined_code)} chars of code")
    logger.info(f"Error logs: {len(execution_logs)} chars")
    
    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Generate debugging prompt
        logger.info("Sending code to LLM for debugging...")
        
        debug_prompt = f"""You are an Expert Python Debugger. You must fix the broken code below.

**BROKEN CODE:**
```python
{combined_code}
```

**ERROR LOGS:**
```
{execution_logs}
```

**YOUR TASK:**
1. Analyze the traceback and identify the EXACT error
2. Common issues to check:
   - KeyError: Column doesn't exist in DataFrame
   - NameError: Variable not defined
   - SyntaxError: Invalid Python syntax
   - TypeError: Wrong data type
   - FileNotFoundError: Path doesn't exist
3. Rewrite the ENTIRE code with the fix applied
4. Ensure the fixed code is executable

**CRITICAL RULES:**
- Output ONLY the complete fixed Python code
- No markdown formatting (no ```python or ```)
- No explanations or comments about what you fixed
- The code must be ready to execute as-is
- Fix ALL errors you can identify

Generate the fixed code now:"""
        
        response = llm.invoke(debug_prompt)
        fixed_code = response.content.strip()
        
        # Clean up code (remove markdown if LLM added it)
        if fixed_code.startswith("```python"):
            fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()
        elif fixed_code.startswith("```"):
            fixed_code = fixed_code.replace("```", "").strip()
        
        logger.info(f"✅ Generated fixed code ({len(fixed_code)} chars)")
        
        # Update state with fixed code
        state["combined_code"] = fixed_code
        
        # Log the fix
        state["messages"].append({
            "role": "assistant",
            "content": f"""🔧 Debugger: Code automatically fixed

**Original Error:** {execution_logs[:200]}...
**Action:** LLM analyzed traceback and rewrote code
**New Code Length:** {len(fixed_code)} chars
"""
        })
        
        logger.info("✅ Debugger Agent completed successfully")
        
        return state
    
    except Exception as e:
        logger.error(f"❌ Debugger Agent failed: {str(e)}", exc_info=True)
        
        # If debugger fails, we can't fix the code
        state["messages"].append({
            "role": "assistant",
            "content": f"⚠️ Debugger failed: {str(e)}"
        })
        
        return state
