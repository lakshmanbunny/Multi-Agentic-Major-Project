"""
Critic Agent - URL Validation & Quality Assurance

This agent validates dataset URLs using a 2-stage approach:
1. Quick HTTP check (fast fail)
2. Deep browser validation (actually loads dataset in Colab)
"""

import os
import sys
import httpx

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from libs.core.state import AgentState, ApprovalStatus
from libs.core.logger import setup_logger

# Initialize logger
logger = setup_logger("critic_agent", level="INFO")


def critic_node(state: AgentState) -> AgentState:
    """
    Critic Agent: 2-Stage Validation
    
    Stage 1: HTTP Status Check (fast fail for 404/403)
    Stage 2: Browser Validation (actually load dataset in Colab)
    Stage 3: Set waiting_human_approval for HITL
    """
    dataset_url = state.get("dataset_info", {}).get("url", "")
    
    logger.info(f"🔍 Critic Agent: Starting 2-stage validation...")
    
    # Clear previous feedback
    state["review_feedback"] = []
    
    # ===== STAGE 0: Check if URL exists =====
    if not dataset_url or len(dataset_url.strip()) < 5:
        logger.warning("⚠️ No valid dataset URL found")
        state["review_feedback"].append("critical_error: No URL found")
        return state
    
    logger.info(f"📋 URL to validate: {dataset_url}")
    
    # ===== STAGE 1: Quick HTTP Check =====
    logger.info("Stage 1/3: HTTP Status Check...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        with httpx.Client(timeout=10.0, follow_redirects=True, headers=headers) as client:
            try:
                response = client.head(dataset_url)
            except httpx.UnsupportedProtocol:
                response = client.get(dataset_url, timeout=10.0)

            if response.status_code not in [200, 301, 302, 307, 308]:
                logger.info(f"HEAD returned {response.status_code}, trying GET...")
                response = client.get(dataset_url, timeout=10.0)

            status_code = response.status_code
            logger.info(f"📡 HTTP Status: {status_code}")
            
            # Reject non-2xx codes immediately
            if not (200 <= status_code < 300):
                logger.error(f"❌ Stage 1 FAILED: HTTP {status_code}")
                state["review_feedback"].append(f"critical_error: HTTP {status_code}")
                state["dataset_info"]["url"] = ""
                
                state["messages"].append({
                    "role": "assistant",
                    "content": f"❌ Critic: URL failed HTTP check ({status_code})"
                })
                return state
            
            logger.info("✅ Stage 1 PASSED: HTTP check OK")
    
    except Exception as e:
        logger.error(f"❌ Stage 1 FAILED: Connection error - {str(e)}")
        state["review_feedback"].append(f"critical_error: Connection failed")
        state["dataset_info"]["url"] = ""
        
        state["messages"].append({
            "role": "assistant",
            "content": f"❌ Critic: Connection failed - {str(e)}"
        })
        return state
    
    # ===== STAGE 2: Browser Execution =====
    logger.info("Stage 2/3: Executing validation code in Browser...")
    
    # Check if this is a Kaggle URL
    is_kaggle = "kaggle.com/datasets" in dataset_url.lower()
    kaggle_handle = ""
    
    if is_kaggle:
        logger.info("🎯 Detected Kaggle URL - using kagglehub validation")
        
        # Extract Kaggle handle from URL
        try:
            parts = dataset_url.split("/datasets/")
            if len(parts) > 1:
                kaggle_handle = parts[1].strip("/").split("?")[0]
                logger.info(f"Extracted Kaggle handle: {kaggle_handle}")
        except:
            logger.error("Failed to extract Kaggle handle from URL")
            state["review_feedback"].append("critical_error: Invalid Kaggle URL format")
            state["dataset_info"]["url"] = ""
            return state
        
        # Generate Kaggle-specific validation code
        validation_code = f"""
import os
import sys

print("=" * 60)
print("🧪 CRITIC: KAGGLE DATASET VALIDATION")
print("=" * 60)

try:
    print("Install kagglehub...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "kagglehub"])
    
    import kagglehub
    import pandas as pd
    
    print(f"Downloading Kaggle dataset: {kaggle_handle}")
    path = kagglehub.dataset_download("{kaggle_handle}")
    print(f"✅ Dataset downloaded to: {{path}}")
    
    # Find CSV files in the downloaded folder
    csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
    
    if not csv_files:
        print("❌ No CSV files found in Kaggle dataset")
        sys.exit(0)
    
    print(f"Found {{len(csv_files)}} CSV file(s): {{csv_files}}")
    
    # Load the first CSV to verify it's readable
    csv_path = os.path.join(path, csv_files[0])
    df = pd.read_csv(csv_path, nrows=10)
    
    print("\\n" + "=" * 60)
    print("📊 DATASET PREVIEW")
    print("=" * 60)
    print(df.head())
    print("\\n" + "=" * 60)
    print(f"Shape: {{df.shape}} | Columns: {{len(df.columns)}}")
    print("=" * 60)
    
    # Print tagged preview for parsing
    print("\\nDATA_PREVIEW_START")
    print(df.head(5).to_string())
    print("DATA_PREVIEW_END")
    
except Exception as e:
    print(f"❌ Kaggle validation failed: {{e}}")
    sys.exit(1)
"""
    else:
        # Generate standard CSV validation code for direct URLs
        validation_code = f"""
import pandas as pd
import sys

print("=" * 60)
print("🧪 CRITIC: DATASET VALIDATION")
print("=" * 60)

try:
    print(f"Loading URL: {dataset_url}")
    df = pd.read_csv('{dataset_url}', on_bad_lines='skip', nrows=10)
    
    # Check for HTML content
    df_str = str(df.columns.tolist()) + str(df.values)
    
    if "<!DOCTYPE" in df_str or "<html" in df_str or "<body" in df_str:
        print("❌ DETECTED HTML CONTENT (Landing Page)")
        sys.exit(0)
    
    if df.empty or len(df) == 0:
        print("❌ Dataframe is empty")
        sys.exit(0)
    
    print("\\n" + "=" * 60)
    print("📊 DATASET PREVIEW")
    print("=" * 60)
    print(df.head())
    print("\\n" + "=" * 60)
    print(f"Shape: {{df.shape}} | Columns: {{len(df.columns)}}")
    print("=" * 60)
    
    # Print tagged preview for parsing
    print("\\nDATA_PREVIEW_START")
    print(df.head(5).to_string())
    print("DATA_PREVIEW_END")

except Exception as e:
    print(f"❌ Load Failed: {{e}}")
    sys.exit(1)
"""
    
    try:
        # Execute validation code in browser
        logger.info("Sending validation code to Browser Agent...")
        
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                "http://localhost:8001/execute",
                json={"code": validation_code}
            )
        
        if response.status_code != 200:
            logger.error(f"❌ Browser Agent failed: HTTP {response.status_code}")
            state["review_feedback"].append("critical_error: Browser execution failed")
            state["dataset_info"]["url"] = ""
            
            state["messages"].append({
                "role": "assistant",
                "content": "❌ Critic: Browser Agent execution failed"
            })
            return state
        
        logger.info("✅ Browser execution completed")
        
        # Extract data preview from logs
        result = response.json()
        logs = result.get("logs", "")
        
        data_preview = "No preview available"
        try:
            if "DATA_PREVIEW_START" in logs and "DATA_PREVIEW_END" in logs:
                start_idx = logs.index("DATA_PREVIEW_START") + len("DATA_PREVIEW_START")
                end_idx = logs.index("DATA_PREVIEW_END")
                data_preview = logs[start_idx:end_idx].strip()
                logger.info(f"✅ Extracted data preview ({len(data_preview)} chars)")
            else:
                logger.warning("⚠️ No DATA_PREVIEW tags found in logs")
        except Exception as e:
            logger.warning(f"Failed to extract data preview: {e}")
        
        # Save preview to state
        state["dataset_info"]["data_preview"] = data_preview
        logger.info("Saved data preview to state")
    
    except httpx.ConnectError:
        logger.warning("⚠️ Browser Agent not available")
        logger.info("Approving based on Stage 1 only (HTTP check)")
        
        state["review_feedback"].append("approved")
        state["messages"].append({
            "role": "assistant",
            "content": f"✅ Critic: URL validated (HTTP {status_code}, browser unavailable)"
        })
        return state
    
    except Exception as e:
        logger.error(f"❌ Browser error: {str(e)}")
        logger.info("Falling back to Stage 1 approval")
        
        state["review_feedback"].append("approved")
        state["messages"].append({
            "role": "assistant",
            "content": f"✅ Critic: URL validated (HTTP {status_code}, browser error)"
        })
        return state
    
    # ===== STAGE 3: SET WAITING STATUS FOR FRONTEND HITL =====
    logger.info("Stage 3/3: Setting status for Frontend HITL Verification...")
    
    # Log info for user
    logger.info("=" * 70)
    logger.info("🛑 HUMAN VERIFICATION REQUIRED")
    logger.info("=" * 70)
    logger.info(f"Dataset URL: {dataset_url}")
    if is_kaggle:
        logger.info(f"Kaggle Handle: {kaggle_handle}")
    logger.info("👉 Check the BROWSER WINDOW and approve via the UI popup.")
    logger.info("=" * 70)
    
    # Store metadata
    if is_kaggle:
        state["dataset_info"]["source_type"] = "kaggle"
        state["dataset_info"]["kaggle_handle"] = kaggle_handle
        logger.info(f"Stored Kaggle metadata: {kaggle_handle}")
    else:
        state["dataset_info"]["source_type"] = "direct"
    
    # Set status to waiting for frontend approval
    state["next_step"] = "waiting_human_approval"
    state["human_approval"] = ApprovalStatus.PENDING
    
    state["messages"].append({
        "role": "assistant",
        "content": f"🛑 Critic: Waiting for human verification via UI (HTTP {status_code})"
    })
    
    logger.info("Critic complete - waiting for frontend approval")
    return state