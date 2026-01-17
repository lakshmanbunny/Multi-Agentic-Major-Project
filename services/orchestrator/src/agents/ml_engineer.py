"""
ML Engineering Agent - Model Training Code Generation

This agent uses Gemini LLM to generate Python code for machine learning model
training, including preprocessing, training, evaluation, and visualization.
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
logger = setup_logger("ml_engineer_agent", level="INFO")


def ml_engineering_node(state: AgentState) -> AgentState:
    """
    ML Engineering Agent that generates model training code.
    
    Args:
        state: Current workflow state with dataset and research info
    
    Returns:
        Updated state with generated training code
    """
    user_goal = state.get("user_goal", "")
    dataset_url = state.get("dataset_info", {}).get("url", "")
    research_plan = state.get("research_plan", [])
    data_preview = state.get("dataset_info", {}).get("data_preview", "No preview available")
    schema = state.get("dataset_info", {}).get("schema", "")  # NEW: Get captured schema
    research_data = state.get("research_data", {})  # NEW: Get research findings
    
    logger.info(f"🤖 ML Engineering Agent started for: {user_goal}")
    logger.info(f"Research plan steps: {len(research_plan)}")
    logger.info(f"Data preview available: {len(data_preview)} chars")
    logger.info(f"Schema captured: {'YES' if schema else 'NO'} ({len(schema)} chars)")
    
    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Generate ML training code using LLM
        logger.info("Generating ML training code with LLM...")
        
        research_context = "\\n".join([f"- {step}" for step in research_plan])
        
        # NEW: Build schema section
        schema_section = ""
        if schema:
            schema_section = f"""
**📊 ACTUAL DATASET SCHEMA (from EDA execution):**
```
{schema}
```
✅ Use this REAL schema to write accurate code. These are the ACTUAL columns and types!
"""
        else:
            schema_section = "**⚠️ Schema not available - infer from preview**"
        
        # NEW: Build research papers section
        papers_context = ""
        if research_data.get("papers"):
            papers_summary = "\\n".join([f"- {p.get('title', 'N/A')}: {p.get('summary', '')[:100]}..." 
                                        for p in research_data["papers"][:3]])
            papers_context = f"""
**📚 Research Papers Context:**
{papers_summary}
"""
        
        ml_prompt = f"""You are an Expert ML Engineer. Write complete Python code for model training.

**User Goal:** {user_goal}
**Dataset URL:** {dataset_url}

**Research Plan:**
{research_context}

{schema_section}

{papers_context}

**DATASET PREVIEW (First 5 Rows):**
```
{data_preview}
```

**🚨 CRITICAL RULES - ZERO TOLERANCE:**

**RULE 1 (ABSOLUTE REQUIREMENT):** 
🚫 NEVER EVER create dummy data or hardcoded DataFrames like `data = {{'col1': [...], 'col2': [...]}}`.
✅ You MUST use the existing `df` variable that was already loaded by the Data Engineering Agent in the previous step.
✅ The DataFrame `df` is ALREADY IN MEMORY from the EDA code that ran before this.

**RULE 2 (Dynamic Inspection):**
If the DATASET PREVIEW above is empty, "No preview available", or truncated:
1. Start your code by printing: `print("\\nDataFrame Info:")`, `print(df.columns.tolist())`, `print(df.head())`
2. This will let you SEE the actual structure in the execution logs
3. Then proceed with the ML code

**RULE 3 (Target Detection):**
If you don't know the exact target column name from the preview:
- Write code to find it dynamically:
  ```python
  # Find target column dynamically
  target_col = None
  for col in df.columns:
      if any(keyword in col.lower() for keyword in ['target', 'outcome', 'class', 'diabetes', 'label', 'price', 'risk']):
          target_col = col
          break
  
  # Fallback: use last column
  if target_col is None:
      target_col = df.columns[-1]
  
  print(f"Target column detected: {{target_col}}")
  ```

**RULE 4 (Safety Checks):**
- Before dropping any column, check if it exists: `if 'column_name' in df.columns: df.drop(...)`
- NEVER assume column names - always verify first

**STANDARD REQUIREMENTS:**
1. **CORRECT IMPORTS (USE EXACTLY):**
   ```python
   from sklearn.impute import SimpleImputer  # NOT from sklearn.preprocessing!
   from sklearn.preprocessing import StandardScaler, LabelEncoder
   from sklearn.model_selection import train_test_split
   from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
   from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
   from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
   import matplotlib.pyplot as plt
   import seaborn as sns
   import numpy as np
   ```

2. **Preprocessing Pipeline:**
   - Separate numerical and categorical columns dynamically
   - Handle missing values (SimpleImputer)
   - Encode categorical variables (LabelEncoder for binary, OneHotEncoder for multiclass)
   - Scale numerical features (StandardScaler)

3. **Train/Test Split:** 80/20 ratio, random_state=42

4. **Model Selection:**
   - Classification: RandomForestClassifier(n_estimators=100, random_state=42)
   - Regression: RandomForestRegressor(n_estimators=100, random_state=42)

5. **Evaluation & Visualization:**
   - Print all metrics with clear labels
   - Create confusion matrix heatmap (classification) OR actual vs predicted plot (regression)
   - Create feature importance bar chart

**OUTPUT FORMAT:**
- Pure Python code ONLY
- No markdown ```python blocks
- No explanatory comments outside code
- Assume `df` is already loaded and ready to use

Generate the robust, dynamic ML training code now:"""
        
        response = llm.invoke(ml_prompt)
        ml_code = response.content.strip()
        
        # Clean up code (remove markdown if LLM added it)
        if ml_code.startswith("```python"):
            ml_code = ml_code.replace("```python", "").replace("```", "").strip()
        elif ml_code.startswith("```"):
            ml_code = ml_code.replace("```", "").strip()
        
        logger.info(f"✅ Generated {len(ml_code)} characters of ML training code")
        
        # Store code in state
        state["code_context"]["model_code"] = ml_code
        
        # Add message
        code_preview = ml_code[:200] + "..." if len(ml_code) > 200 else ml_code
        state["messages"].append({
            "role": "assistant",
            "content": f"""✅ ML Training Code Generated

**Lines of Code:** {len(ml_code.split(chr(10)))}
**Algorithm:** Intelligent selection based on goal

**Preview:**
```python
{code_preview}
```

Ready for model training!
"""
        })
        
        # Set next step
        state["next_step"] = "critic_agent"
        
        logger.info("✅ ML Engineering Agent completed successfully")
        
        return state
    
    except Exception as e:
        logger.error(f"❌ ML Engineering Agent failed: {str(e)}", exc_info=True)
        
        # Fallback: create basic ML code
        fallback_code = f"""
# ML Training Code (Fallback)
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

# Assume df is loaded from previous code
# Preprocessing
le = LabelEncoder()
for col in df.select_dtypes(include=['object']).columns:
    if col != 'target':  # Adjust 'target' to your actual target column
        df[col] = le.fit_transform(df[col].astype(str))

# Split features and target
X = df.drop('target', axis=1)  # Adjust 'target' column name
y = df['target']

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Metrics
accuracy = accuracy_score(y_test, y_pred)
print(f"\\nModel Accuracy: {{accuracy:.4f}}")
print("\\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\\nML Training Complete!")
"""
        
        state["code_context"]["model_code"] = fallback_code.strip()
        
        state["messages"].append({
            "role": "assistant",
            "content": f"⚠️ Generated fallback ML code due to error: {str(e)}"
        })
        
        state["next_step"] = "critic_agent"
        
        return state
