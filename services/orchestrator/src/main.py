"""
Orchestrator Service - The Brain 🧠

FastAPI service that coordinates the Auto-DataScientist workflow.
Manages agents and routes code execution to the Browser Agent.
"""
import sys
import os

# --- PATH FIX: FORCE PYTHON TO FIND 'libs' ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ---------------------------------------------

import uuid
import httpx  # Required for calling the Browser Agent
import time   # For rate limiting between retries
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict

# Import our shared core library
from libs.core.state import AgentState, ApprovalStatus
from libs.core.logger import setup_logger

# Import agents
from agents.research import research_node
from agents.data_engineer import data_engineering_node
from agents.ml_engineer import ml_engineering_node
from agents.critic import critic_node
from agents.debugger import debugger_node

# Initialize logger
logger = setup_logger("orchestrator", level="INFO")

# Initialize FastAPI app
app = FastAPI(
    title="Auto-DataScientist Orchestrator",
    description="Central coordination service for the Auto-DataScientist AI system",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- IN-MEMORY STATE STORE ---
workflows: Dict[str, AgentState] = {}

# --- MODELS ---
class WorkflowRequest(BaseModel):
    user_goal: str
    dataset_url: Optional[str] = ""
    model_config = ConfigDict(protected_namespaces=())

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    message: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class FeedbackRequest(BaseModel):
    satisfied: bool
    feedback: str = ""

# --- BACKGROUND TASK (Real Workflow Execution) ---
async def run_workflow_simulation(workflow_id: str):
    """
    Executes the full agent workflow: Research -> Data Eng -> ML Eng -> Browser Agent
    """
    logger.info(f"Workflow processing started", extra={"workflow_id": workflow_id})
    
    # CRITICAL FIX: Define state FIRST to avoid UnboundLocalError
    state = workflows[workflow_id]

    # 1. Research + Critic Loop (with retry for broken URLs)
    logger.info("Starting Research Phase with Critic validation...", extra={"workflow_id": workflow_id})
    
    max_retries = 3
    approved = False
    
    for attempt in range(1, max_retries + 1):
        logger.info(f"Research attempt {attempt}/{max_retries}", extra={"workflow_id": workflow_id})
        
        # Run Research Agent
        try:
            state["next_step"] = "research_agent"
            workflows[workflow_id] = state
            state = research_node(state)
            workflows[workflow_id] = state
            logger.info("Research Agent completed", extra={"workflow_id": workflow_id})
        except Exception as e:
            logger.error(f"Research Agent failed: {e}", extra={"workflow_id": workflow_id})
            if attempt == max_retries:
                logger.error("Max retries reached, aborting workflow", extra={"workflow_id": workflow_id})
                return
            continue
        
        # Run Critic Agent to validate URL
        try:
            state["next_step"] = "critic_agent"
            workflows[workflow_id] = state
            state = critic_node(state)
            workflows[workflow_id] = state
            logger.info("Critic Agent completed", extra={"workflow_id": workflow_id})
            
            # Check feedback
            feedback = state.get("review_feedback", [])
            next_step = state.get("next_step", "")
            
            # Check if waiting for frontend HITL approval
            if next_step == "waiting_human_approval":
                logger.info("⏳ Waiting for frontend HITL approval...", extra={"workflow_id": workflow_id})
                logger.info("Workflow paused - will continue when user approves via UI", extra={"workflow_id": workflow_id})
                workflows[workflow_id] = state
                return  # Exit cleanly - workflow will be resumed by approve endpoint
            
            if "approved" in feedback:
                logger.info("✅ Critic approved - Dataset URL validated!", extra={"workflow_id": workflow_id})
                approved = True
                break
            
            elif any("critical_error" in fb for fb in feedback):
                logger.warning(f"❌ Critic rejected URL (attempt {attempt}/{max_retries})", extra={"workflow_id": workflow_id})
                logger.info("Retrying research to find a valid dataset...", extra={"workflow_id": workflow_id})
                # Loop continues to retry research
            
            else:
                logger.warning(f"⚠️ Critic gave warning but proceeding (attempt {attempt}/{max_retries})", extra={"workflow_id": workflow_id})
                approved = True
                break
                
        except Exception as e:
            logger.error(f"Critic Agent failed: {e}", extra={"workflow_id": workflow_id})
            if attempt == max_retries:
                logger.error("Max retries reached, aborting workflow", extra={"workflow_id": workflow_id})
                return
    
    # Check if we got approval
    if not approved:
        logger.error("❌ Failed to find valid dataset after all retries. Aborting workflow.", extra={"workflow_id": workflow_id})
        state["messages"].append({
            "role": "assistant",
            "content": "❌ Workflow aborted: Could not find a valid dataset URL after multiple attempts."
        })
        workflows[workflow_id] = state
        return
    
    # 2. Execute Data Engineering Agent
    logger.info("Data Engineering Agent: Generating EDA code...", extra={"workflow_id": workflow_id})
    state["next_step"] = "data_engineering_agent"
    workflows[workflow_id] = state
    try:
        state = data_engineering_node(state)
        workflows[workflow_id] = state
        code_length = len(state["code_context"]["eda_code"])
        logger.info(f"Data Engineering Agent completed - Generated {code_length} chars of code", extra={"workflow_id": workflow_id})
    except Exception as e:
        logger.error(f"Data Engineering Agent failed: {e}", extra={"workflow_id": workflow_id})
        return
    
    # 3. Execute ML Engineering Agent
    logger.info("ML Engineering Agent: Generating training code...", extra={"workflow_id": workflow_id})
    state["next_step"] = "ml_engineering_agent"
    workflows[workflow_id] = state
    try:
        state = ml_engineering_node(state)
        workflows[workflow_id] = state
        ml_code_length = len(state["code_context"]["model_code"])
        logger.info(f"ML Engineering Agent completed - Generated {ml_code_length} chars of code", extra={"workflow_id": workflow_id})
    except Exception as e:
        logger.error(f"ML Engineering Agent failed: {e}", extra={"workflow_id": workflow_id})
        return
    
    # 4. Combine Code for Execution
    logger.info("Combining EDA and ML code...", extra={"workflow_id": workflow_id})
    eda_code = state["code_context"].get("eda_code", "")
    ml_code = state["code_context"].get("model_code", "")
    
    full_code = f"""
# ==========================================
# AUTO-GENERATED BY AUTO-DATA-SCIENTIST
# ==========================================

# --- PART 1: EXPLORATORY DATA ANALYSIS ---
{eda_code}

# --- PART 2: MACHINE LEARNING TRAINING ---
{ml_code}
"""
    state["combined_code"] = full_code
    workflows[workflow_id] = state
    logger.info(f"Combined code ready ({len(full_code)} chars)", extra={"workflow_id": workflow_id})
    
    # 5. Execute in Browser with Self-Healing
    state["next_step"] = "browser_execution"
    workflows[workflow_id] = state
    
    max_debug_attempts = 3
    execution_success = False
    
    for debug_attempt in range(1, max_debug_attempts + 1):
        logger.info(f"Browser Execution: Attempt {debug_attempt}/{max_debug_attempts}...", extra={"workflow_id": workflow_id})
        
        try:
            with httpx.Client(timeout=180.0) as client:
                response = client.post(
                    "http://localhost:8001/execute",
                    json={"code": state["combined_code"]}
                )
            
            if response.status_code == 200:
                result = response.json()
                logs = result.get("logs", "")
                state["execution_logs"] = logs
                workflows[workflow_id] = state
                
                error_keywords = ["Traceback", "Error:", "Exception:", "KeyError", "SyntaxError"]
                has_error = any(kw in logs for kw in error_keywords)
                
                if has_error and debug_attempt < max_debug_attempts:
                    logger.warning(f"⚠️ Execution error detected, invoking debugger...", extra={"workflow_id": workflow_id})
                    time.sleep(5)
                    state = debugger_node(state)
                    workflows[workflow_id] = state
                    continue
                elif not has_error:
                    logger.info("✅ Code executed successfully!", extra={"workflow_id": workflow_id})
                    execution_success = True
                    break
                else:
                    logger.error("❌ Max debug attempts reached", extra={"workflow_id": workflow_id})
                    break
            else:
                logger.error(f"Browser Agent error: HTTP {response.status_code}", extra={"workflow_id": workflow_id})
                break
        except httpx.ConnectError:
            logger.error("❌ Browser Agent not reachable", extra={"workflow_id": workflow_id})
            break
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}", extra={"workflow_id": workflow_id})
            break
    
    # Final status - Wait for user satisfaction check
    if execution_success:
        logger.info("✅ Execution successful - waiting for user final satisfaction check...", extra={"workflow_id": workflow_id})
        state["next_step"] = "waiting_final_approval"
        # DO NOT set to completed yet - user needs to approve
    else:
        logger.error("💀 Workflow execution failed", extra={"workflow_id": workflow_id})
        state["next_step"] = "failed"
    
    workflows[workflow_id] = state


# --- CONTINUE WORKFLOW AFTER HITL APPROVAL ---
def continue_workflow_after_approval(workflow_id: str):
    """Continue workflow execution from Data Engineering after frontend approval"""
    logger.info("🔄 Resuming workflow after HITL approval...", extra={"workflow_id": workflow_id})
    
    if workflow_id not in workflows:
        logger.error("Workflow not found for continuation", extra={"workflow_id": workflow_id})
        return
    
    state = workflows[workflow_id]
    
    # 2. Execute Data Engineering Agent
    logger.info("Data Engineering Agent: Generating EDA code...", extra={"workflow_id": workflow_id})
    state["next_step"] = "data_engineering_agent"
    workflows[workflow_id] = state
    
    try:
        state = data_engineering_node(state)
        workflows[workflow_id] = state
        code_length = len(state["code_context"]["eda_code"])
        logger.info(f"Data Engineering Agent completed - Generated {code_length} chars of code", extra={"workflow_id": workflow_id})
    except Exception as e:
        logger.error(f"Data Engineering Agent failed: {e}", extra={"workflow_id": workflow_id})
        state["next_step"] = "failed"
        workflows[workflow_id] = state
        return
    
    # 3. Execute ML Engineering Agent
    logger.info("ML Engineering Agent: Generating training code...", extra={"workflow_id": workflow_id})
    state["next_step"] = "ml_engineering_agent"
    workflows[workflow_id] = state
    
    try:
        state = ml_engineering_node(state)
        workflows[workflow_id] = state
        ml_code_length = len(state["code_context"]["model_code"])
        logger.info(f"ML Engineering Agent completed - Generated {ml_code_length} chars of code", extra={"workflow_id": workflow_id})
    except Exception as e:
        logger.error(f"ML Engineering Agent failed: {e}", extra={"workflow_id": workflow_id})
        state["next_step"] = "failed"
        workflows[workflow_id] = state
        return
    
    # 4. Combine Code for Execution
    logger.info("Combining EDA and ML code...", extra={"workflow_id": workflow_id})
    eda_code = state["code_context"].get("eda_code", "")
    ml_code = state["code_context"].get("model_code", "")
    
    full_code = f"""
# ==========================================
# AUTO-GENERATED BY AUTO-DATA-SCIENTIST
# ==========================================

# --- PART 1: EXPLORATORY DATA ANALYSIS ---
{eda_code}

# --- PART 2: MACHINE LEARNING TRAINING ---
{ml_code}
"""
    state["combined_code"] = full_code
    workflows[workflow_id] = state
    logger.info(f"Combined code ready ({len(full_code)} chars)", extra={"workflow_id": workflow_id})
    
    # 5. Execute in Browser with Self-Healing
    state["next_step"] = "browser_execution"
    workflows[workflow_id] = state
    
    max_debug_attempts = 3
    execution_success = False
    
    for debug_attempt in range(1, max_debug_attempts + 1):
        logger.info(f"Browser Execution: Attempt {debug_attempt}/{max_debug_attempts}...", extra={"workflow_id": workflow_id})
        
        try:
            with httpx.Client(timeout=180.0) as client:
                response = client.post(
                    "http://localhost:8001/execute",
                    json={"code": state["combined_code"]}
                )
            
            if response.status_code == 200:
                result = response.json()
                logs = result.get("logs", "")
                state["execution_logs"] = logs
                workflows[workflow_id] = state
                
                error_keywords = ["Traceback", "Error:", "Exception:", "KeyError", "SyntaxError"]
                has_error = any(kw in logs for kw in error_keywords)
                
                if has_error and debug_attempt < max_debug_attempts:
                    logger.warning(f"⚠️ Execution error detected, invoking debugger...", extra={"workflow_id": workflow_id})
                    time.sleep(5)
                    state = debugger_node(state)
                    workflows[workflow_id] = state
                    continue
                elif not has_error:
                    logger.info("✅ Code executed successfully!", extra={"workflow_id": workflow_id})
                    execution_success = True
                    break
                else:
                    logger.error("❌ Max debug attempts reached", extra={"workflow_id": workflow_id})
                    break
            else:
                logger.error(f"Browser Agent error: HTTP {response.status_code}", extra={"workflow_id": workflow_id})
                break
        except httpx.ConnectError:
            logger.error("❌ Browser Agent not reachable", extra={"workflow_id": workflow_id})
            break
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}", extra={"workflow_id": workflow_id})
            break
    
    # Final status - Wait for user satisfaction check
    if execution_success:
        logger.info("✅ Execution successful - waiting for user final satisfaction check...", extra={"workflow_id": workflow_id})
        state["next_step"] = "waiting_final_approval"
        # DO NOT set to completed yet - user needs to approve
    else:
        logger.error("💀 Workflow execution failed", extra={"workflow_id": workflow_id})
        state["next_step"] = "failed"
    
    workflows[workflow_id] = state


# --- RETRY RESEARCH AFTER HITL REJECTION ---
def retry_research_after_rejection(workflow_id: str):
    """Retry research when user rejects the dataset via HITL"""
    logger.info("🔄 Retrying research after HITL rejection...", extra={"workflow_id": workflow_id})
    
    if workflow_id not in workflows:
        logger.error("Workflow not found for retry", extra={"workflow_id": workflow_id})
        return
    
    state = workflows[workflow_id]
    
    # Clear old dataset info and feedback
    state["dataset_info"]["url"] = ""
    state["dataset_info"]["data_preview"] = ""
    state["review_feedback"] = []  # Clear old feedback
    state["human_approval"] = ApprovalStatus.PENDING
    
    # Run NEW research
    logger.info("Research Agent: Searching for new dataset...", extra={"workflow_id": workflow_id})
    state["next_step"] = "research_agent"
    workflows[workflow_id] = state
    
    try:
        state = research_node(state)
        workflows[workflow_id] = state
        logger.info("New Research completed", extra={"workflow_id": workflow_id})
    except Exception as e:
        logger.error(f"Research retry failed: {e}", extra={"workflow_id": workflow_id})
        state["next_step"] = "failed"
        workflows[workflow_id] = state
        return
    
    # Run Critic validation again
    logger.info("Critic Agent: Validating new dataset...", extra={"workflow_id": workflow_id})
    state["next_step"] = "critic_agent"
    workflows[workflow_id] = state
    
    try:
        state = critic_node(state)
        workflows[workflow_id] = state
        logger.info("Critic Agent completed", extra={"workflow_id": workflow_id})
        
        # Check if waiting for frontend HITL again
        if state.get("next_step") == "waiting_human_approval":
            logger.info("⏳ Waiting for frontend HITL approval (retry)...", extra={"workflow_id": workflow_id})
            return  # Wait for next user decision
        
        # If directly approved by critic (rare), continue
        if "approved" in state.get("review_feedback", []):
            logger.info("✅ New dataset approved by Critic", extra={"workflow_id": workflow_id})
            continue_workflow_after_approval(workflow_id)
            
    except Exception as e:
        logger.error(f"Critic retry failed: {e}", extra={"workflow_id": workflow_id})
        state["next_step"] = "failed"
        workflows[workflow_id] = state
        return


# --- API ENDPOINTS ---

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(status="healthy", service="orchestrator", version="0.1.0")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    logger.info("Health check requested")
    return HealthResponse(status="healthy", service="orchestrator", version="0.1.0")

@app.post("/workflow/start", response_model=WorkflowResponse)
async def start_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    logger.info("Starting new workflow", extra={"user_goal": request.user_goal})
    
    try:
        workflow_id = str(uuid.uuid4())
        
        # Initialize State
        initial_state: AgentState = {
            "messages": [],
            "user_goal": request.user_goal,
            "dataset_info": {"url": request.dataset_url or "", "file_path": "", "is_public": True, "description": ""},
            "research_plan": [],
            "code_context": {"eda_code": "", "model_code": "", "file_name": ""},
            "review_feedback": [],
            "human_approval": ApprovalStatus.PENDING,
            "next_step": "research_agent",
            "rejected_urls": []  # Track rejected dataset URLs
        }
        
        # Save to memory
        workflows[workflow_id] = initial_state
        
        # Run the workflow in background
        background_tasks.add_task(run_workflow_simulation, workflow_id)
        
        logger.info("Workflow started successfully", extra={"workflow_id": workflow_id})
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            status="started",
            message="Workflow initialized and running"
        )
    except Exception as e:
        logger.error(f"Failed to start workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    logger.info("Status check requested", extra={"workflow_id": workflow_id})
    
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    state = workflows[workflow_id]
    
    # Determine status based on next_step and approval state
    next_step = state.get("next_step", "")
    approval = state.get("human_approval", ApprovalStatus.PENDING)
    
    if next_step == "waiting_human_approval":
        status = "waiting_approval"
    elif next_step == "waiting_final_approval":
        status = "waiting_final_approval"
    elif next_step == "completed":
        status = "completed"
    elif next_step == "failed":
        status = "failed"
    elif approval == ApprovalStatus.REJECTED:
        status = "failed"
    else:
        status = "running"
    
    return {
        "workflow_id": workflow_id,
        "status": status,
        "current_step": next_step,
        "user_goal": state.get("user_goal", "")
    }


@app.post("/workflow/{workflow_id}/approve")
async def approve_workflow(workflow_id: str, background_tasks: BackgroundTasks):
    """Frontend HITL: User approves the dataset"""
    logger.info("Approval received from frontend", extra={"workflow_id": workflow_id})
    
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    state = workflows[workflow_id]
    state["human_approval"] = ApprovalStatus.APPROVED
    state["review_feedback"].append("approved")
    state["next_step"] = "data_engineering_agent"
    workflows[workflow_id] = state
    
    logger.info("✅ Workflow approved by user - resuming execution...", extra={"workflow_id": workflow_id})
    
    # Resume workflow in background
    background_tasks.add_task(continue_workflow_after_approval, workflow_id)
    
    return {"status": "approved", "message": "Workflow approved, continuing to Data Engineering"}


@app.post("/workflow/{workflow_id}/feedback")
async def submit_final_feedback(workflow_id: str, feedback: FeedbackRequest, background_tasks: BackgroundTasks):
    """Final Satisfaction Check: User provides feedback after execution"""
    logger.info(f"Final feedback received: satisfied={feedback.satisfied}", extra={"workflow_id": workflow_id})
    
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    state = workflows[workflow_id]
    
    if feedback.satisfied:
        # User is satisfied - mark workflow as completed
        logger.info("✅ User satisfied with results - marking workflow as completed", extra={"workflow_id": workflow_id})
        state["next_step"] = "completed"
        state["human_approval"] = ApprovalStatus.APPROVED
        workflows[workflow_id] = state
        
        return {"status": "completed", "message": "Workflow marked as completed"}
    else:
        # User is unsatisfied - retry from Data Engineering
        logger.warning(f"❌ User unsatisfied: {feedback.feedback}", extra={"workflow_id": workflow_id})
        
        # Add user feedback to messages
        state["messages"].append({
            "role": "user",
            "content": f"Feedback: {feedback.feedback if feedback.feedback else 'Results not satisfactory'}"
        })
        
        state["next_step"] = "data_engineering_agent"
        workflows[workflow_id] = state
        
        logger.info("Retrying workflow from Data Engineering phase...", extra={"workflow_id": workflow_id})
        
        # Restart workflow from Data Engineering in background
        background_tasks.add_task(continue_workflow_after_approval, workflow_id)
        
        return {"status": "retrying", "message": "Retrying workflow from Data Engineering phase"}


@app.post("/workflow/{workflow_id}/reject")
async def reject_workflow(workflow_id: str, background_tasks: BackgroundTasks):
    """Frontend HITL: User rejects the dataset - triggers new research"""
    logger.info("Rejection received from frontend", extra={"workflow_id": workflow_id})
    
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    state = workflows[workflow_id]
    
    # Track rejected URL to avoid retrying it
    rejected_url = state["dataset_info"].get("url", "")
    if rejected_url and rejected_url not in state.get("rejected_urls", []):
        if "rejected_urls" not in state:
            state["rejected_urls"] = []
        state["rejected_urls"].append(rejected_url)
        logger.info(f"Added to rejected list: {rejected_url}")
    
    state["human_approval"] = ApprovalStatus.REJECTED
    state["next_step"] = "research_agent"
    workflows[workflow_id] = state
    
    logger.warning(f"❌ Workflow rejected - will exclude {len(state.get('rejected_urls', []))} URL(s)", extra={"workflow_id": workflow_id})
    
    # Restart research in background
    background_tasks.add_task(retry_research_after_rejection, workflow_id)
    
    return {"status": "rejected", "message": "Workflow rejected, searching for new dataset..."}

@app.post("/workflow/clear")
async def clear_all_workflows():
    """Clear all workflow state - for UI reset"""
    logger.info("Clearing all workflow state")
    workflows.clear()
    return {"status": "cleared", "message": "All workflows cleared"}

@app.delete("/workflow/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a specific workflow"""
    if workflow_id in workflows:
        del workflows[workflow_id]
        logger.info("Workflow deleted", extra={"workflow_id": workflow_id})
        return {"status": "deleted", "workflow_id": workflow_id}
    else:
        raise HTTPException(status_code=404, detail="Workflow not found")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Orchestrator service")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Project root: {project_root}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")