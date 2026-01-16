"""
Test script for Data Engineering Agent

Tests the agent's ability to generate EDA code.
"""

import os
import sys

# Add project root
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from libs.core.state import AgentState, ApprovalStatus
from services.orchestrator.src.agents.data_engineer import data_engineering_node

# Create test state (simulating after research agent)
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
        "Perform EDA",
        "Train model",
        "Evaluate results"
    ],
    "code_context": {
        "eda_code": "",
        "model_code": "",
        "file_name": ""
    },
    "review_feedback": [],
    "human_approval": ApprovalStatus.PENDING,
    "next_step": "data_engineering_agent"
}

print("=" * 70)
print("🧪 Testing Data Engineering Agent")
print("=" * 70)
print(f"\n📊 User Goal: {test_state['user_goal']}")
print(f"📁 Dataset: {test_state['dataset_info']['url']}\n")

# Run the agent
result_state = data_engineering_node(test_state)

print("\n" + "=" * 70)
print("📊 RESULTS")
print("=" * 70)

eda_code = result_state['code_context']['eda_code']
file_name = result_state['code_context']['file_name']

print(f"\n✅ File Name: {file_name}")
print(f"📝 Generated Code Length: {len(eda_code)} characters")
print(f"📄 Lines of Code: {len(eda_code.split(chr(10)))}")
print(f"\n🔍 Code Preview (first 500 chars):")
print("-" * 70)
print(eda_code[:500])
print("-" * 70)

if result_state['messages']:
    print(f"\n💬 Agent Message:")
    print(result_state['messages'][-1]['content'][:300])

print(f"\n➡️  Next Step: {result_state['next_step']}")
print("\n" + "=" * 70)
print("✅ Test Complete!")
print("=" * 70)

# Optionally save the code to a file
save_code = input("\n💾 Save generated code to file? (y/n): ")
if save_code.lower() == 'y':
    with open("generated_eda.py", "w") as f:
        f.write(eda_code)
    print("✅ Saved to generated_eda.py")
