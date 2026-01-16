"""
Data Engineering Agent - EDA Code Generation

This agent uses Gemini LLM to generate Python code for exploratory data analysis,
including data loading, cleaning, and visualizations.
"""

import os
import sys
from typing import Dict

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
logger = setup_logger("data_engineer_agent", level="INFO")


def data_engineering_node(state: AgentState) -> AgentState:
    """
    Data Engineering Agent that generates EDA code.
    
    Args:
        state: Current workflow state with dataset info
    
    Returns:
        Updated state with generated EDA code
    """
    user_goal = state.get("user_goal", "")
    dataset_url = state.get("dataset_info", {}).get("url", "")
    source_type = state.get("dataset_info", {}).get("source_type", "direct")
    kaggle_handle = state.get("dataset_info", {}).get("kaggle_handle", "")
    data_preview = state.get("dataset_info", {}).get("data_preview", "No preview available")
    
    logger.info(f"🔧 Data Engineering Agent started for: {user_goal}")
    logger.info(f"Dataset source: {source_type}")
    if source_type == "kaggle":
        logger.info(f"Kaggle handle: {kaggle_handle}")
    else:
        logger.info(f"Dataset URL: {dataset_url}")
    logger.info(f"Data preview available: {len(data_preview)} chars")
    
    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Generate loading instructions based on source type
        if source_type == "kaggle":
            loading_instructions = f"""
**Dataset Source:** Kaggle ({kaggle_handle})

**Loading Instructions:**
1. Install kagglehub: !pip install -q kagglehub
2. Import: import kagglehub, os
3. Download: path = kagglehub.dataset_download("{kaggle_handle}")
4. Find CSV: csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
5. Load first CSV: df = pd.read_csv(os.path.join(path, csv_files[0]))
"""
        else:
            loading_instructions = f"""
**Dataset Source:** Direct URL
**Dataset URL:** {dataset_url}

**Loading Instructions:**
1. Load directly: df = pd.read_csv('{dataset_url}')
2. Use try-except for error handling
"""
        
        # Generate EDA code using LLM
        logger.info("Generating EDA code with LLM...")
        
        eda_prompt = f"""You are an Expert Data Engineer. Write a complete Python script to perform Exploratory Data Analysis.

**User Goal:** {user_goal}
{loading_instructions}

**ACTUAL DATASET PREVIEW (First 5 Rows):**
```
{data_preview}
```

**CRITICAL REQUIREMENTS:**
1. Import necessary libraries (pandas, matplotlib, seaborn, numpy)
2. Load the dataset using the EXACT loading instructions above
3. Use ONLY the column names that appear in the dataset preview above
4. DO NOT invent or assume column names like 'id', 'name', etc. that are not in the preview
5. Handle missing values (impute numeric with mean, categorical with mode)
6. Print dataset info, shape, and summary statistics
7. Create exactly 2 visualizations:
   - Histogram of numerical features
   - Correlation matrix heatmap
8. Save plots as PNG files

**OUTPUT RULES:**
- Output ONLY valid Python code
- No markdown formatting (no ```python or ```)
- No explanatory text or comments
- Follow the loading instructions EXACTLY
- Use the exact column names from the preview

Generate the code now:"""
        
        response = llm.invoke(eda_prompt)
        eda_code = response.content.strip()
        
        # Clean up code (remove markdown if LLM added it anyway)
        if eda_code.startswith("```python"):
            eda_code = eda_code.replace("```python", "").replace("```", "").strip()
        elif eda_code.startswith("```"):
            eda_code = eda_code.replace("```", "").strip()
        
        logger.info(f"✅ Generated {len(eda_code)} characters of EDA code")
        
        # Store code in state
        state["code_context"]["eda_code"] = eda_code
        state["code_context"]["file_name"] = "eda_analysis.py"
        
        # Add message
        code_preview = eda_code[:200] + "..." if len(eda_code) > 200 else eda_code
        state["messages"].append({
            "role": "assistant",
            "content": f"""✅ EDA Code Generated

**Lines of Code:** {len(eda_code.split(chr(10)))}
**File:** eda_analysis.py

**Preview:**
```python
{code_preview}
```

Ready to execute in Google Colab!
"""
        })
        
        # Set next step
        state["next_step"] = "browser_agent"
        
        logger.info("✅ Data Engineering Agent completed successfully")
        
        return state
    
    except Exception as e:
        logger.error(f"❌ Data Engineering Agent failed: {str(e)}", exc_info=True)
        
        # Fallback: create basic EDA code
        fallback_code = f"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
try:
    df = pd.read_csv('{dataset_url}')
except:
    print("Failed to load dataset from URL")
    df = pd.DataFrame()

# Basic info
print("Dataset Shape:", df.shape)
print("\\nDataset Info:")
print(df.info())
print("\\nSummary Statistics:")
print(df.describe())

# Handle missing values
for col in df.select_dtypes(include=['float64', 'int64']).columns:
    df[col].fillna(df[col].mean(), inplace=True)

# Visualizations
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
df.hist(ax=axes[0])
axes[0].set_title('Feature Distributions')
sns.heatmap(df.corr(), annot=True, ax=axes[1])
axes[1].set_title('Correlation Matrix')
plt.savefig('eda_output.png')
print("\\nEDA complete!")
"""
        
        state["code_context"]["eda_code"] = fallback_code.strip()
        state["code_context"]["file_name"] = "eda_analysis.py"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"⚠️ Generated fallback EDA code due to error: {str(e)}"
        })
        
        state["next_step"] = "browser_agent"
        
        return state
