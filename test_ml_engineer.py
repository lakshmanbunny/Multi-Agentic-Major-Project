"""
Test script for ML Engineering Agent

Tests the agent's ability to generate ML training code.
"""

import os
import sys

# Add project root
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from libs.core.state import AgentState, ApprovalStatus
from services.orchestrator.src.agents.ml_engineer import ml_engineering_node

# Create test state (simulating after research + data engineering)
test_state: AgentState = {
    "messages": [],
    "user_goal": "Build a customer churn prediction model",
    "dataset_info": {
        "url": "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv",
        "file_path": "",
        "is_public": True,
        "description": "Telco customer churn dataset"
    },
    "research_plan": [
        "Download and validate dataset",
        "Perform exploratory data analysis",
        "Select RandomForest or XGBoost classifier",
        "Train model and evaluate with confusion matrix"
    ],
    "code_context": {
        "eda_code": "# EDA code would be here...\nimport pandas as pd\ndf = pd.read_csv('...')",
        "model_code": "",
        "file_name": ""
    },
    "review_feedback": [],
    "human_approval": ApprovalStatus.PENDING,
    "next_step": "ml_engineering_agent"
}

print("=" * 70)
print("🧪 Testing ML Engineering Agent")
print("=" * 70)
print(f"\n🎯 User Goal: {test_state['user_goal']}")
print(f"📁 Dataset: {test_state['dataset_info']['url']}")
print(f"📋 Research Plan: {len(test_state['research_plan'])} steps\n")

# Run the agent
result_state = ml_engineering_node(test_state)

print("\n" + "=" * 70)
print("📊 RESULTS")
print("=" * 70)

ml_code = result_state['code_context']['model_code']

print(f"\n✅ Generated ML Training Code")
print(f"📝 Code Length: {len(ml_code)} characters")
print(f"📄 Lines of Code: {len(ml_code.split(chr(10)))}")

# Check what's included
has_preprocessing = any(word in ml_code.lower() for word in ['scaler', 'encoder', 'preprocessing'])
has_train_test = 'train_test_split' in ml_code
has_model = any(word in ml_code for word in ['RandomForest', 'XGBoost', 'fit(', 'predict('])
has_metrics = any(word in ml_code.lower() for word in ['accuracy', 'classification_report', 'confusion_matrix'])

print(f"\n🔍 Code includes:")
print(f"   {'✅' if has_preprocessing else '❌'} Preprocessing (scaling/encoding)")
print(f"   {'✅' if has_train_test else '❌'} Train/Test split")
print(f"   {'✅' if has_model else '❌'} Model training")
print(f"   {'✅' if has_metrics else '❌'} Evaluation metrics")

print(f"\n🔍 Code Preview (first 600 chars):")
print("-" * 70)
print(ml_code[:600])
print("-" * 70)

if result_state['messages']:
    print(f"\n💬 Agent Message:")
    print(result_state['messages'][-1]['content'][:300])

print(f"\n➡️  Next Step: {result_state['next_step']}")
print("\n" + "=" * 70)
print("✅ Test Complete!")
print("=" * 70)

# Optionally save the code
save_code = input("\n💾 Save generated code to file? (y/n): ")
if save_code.lower() == 'y':
    with open("generated_ml_training.py", "w") as f:
        f.write(ml_code)
    print("✅ Saved to generated_ml_training.py")
