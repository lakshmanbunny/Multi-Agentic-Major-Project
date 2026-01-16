"""
Quick test script for the Research Agent

Run this to verify the Research Agent is working with real API calls.
"""

import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from libs.core.state import AgentState, ApprovalStatus
from services.orchestrator.src.agents.research import research_node

# Create a test state
test_state: AgentState = {
    "messages": [],
    "user_goal": "Build a customer churn prediction model for telecommunications",
    "dataset_info": {
        "url": "",
        "file_path": "",
        "is_public": True,
        "description": ""
    },
    "research_plan": [],
    "code_context": {
        "eda_code": "",
        "model_code": "",
        "file_name": ""
    },
    "review_feedback": [],
    "human_approval": ApprovalStatus.PENDING,
    "next_step": "research_agent"
}

print("=" * 60)
print("🧪 Testing Research Agent")
print("=" * 60)
print(f"\nUser Goal: {test_state['user_goal']}\n")

# Run the research agent
result_state = research_node(test_state)

print("\n" + "=" * 60)
print("📊 RESULTS")
print("=" * 60)

print(f"\n✅ Dataset URL: {result_state['dataset_info']['url']}")
print(f"\n📋 Research Plan ({len(result_state['research_plan'])} steps):")
for i, step in enumerate(result_state['research_plan'], 1):
    print(f"   {i}. {step}")

if result_state['messages']:
    print(f"\n💬 Agent Message:")
    print(result_state['messages'][-1]['content'])

print(f"\n➡️  Next Step: {result_state['next_step']}")
print("\n" + "=" * 60)
print("✅ Test Complete!")
print("=" * 60)
