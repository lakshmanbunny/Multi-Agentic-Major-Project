"""
Test script for Critic Agent

Tests URL validation functionality.
"""

import os
import sys

# Add project root
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from libs.core.state import AgentState, ApprovalStatus
from services.orchestrator.src.agents.critic import critic_node

print("=" * 70)
print("🧪 Testing Critic Agent - URL Validation")
print("=" * 70)

# Test 1: Valid URL
print("\n📋 TEST 1: Valid URL")
print("-" * 70)

test_state_valid: AgentState = {
    "messages": [],
    "user_goal": "Test workflow",
    "dataset_info": {
        "url": "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv",
        "file_path": "",
        "is_public": True,
        "description": ""
    },
    "research_plan": [],
    "code_context": {"eda_code": "", "model_code": "", "file_name": ""},
    "review_feedback": [],
    "human_approval": ApprovalStatus.PENDING,
    "next_step": "critic"
}

result = critic_node(test_state_valid)
print(f"URL: {test_state_valid['dataset_info']['url'][:60]}...")
print(f"Feedback: {result['review_feedback']}")
print(f"Result: {'✅ PASS' if 'approved' in result['review_feedback'] else '❌ FAIL'}")

# Test 2: Broken URL (404)
print("\n📋 TEST 2: Broken URL (404)")
print("-" * 70)

test_state_broken: AgentState = {
    "messages": [],
    "user_goal": "Test workflow",
    "dataset_info": {
        "url": "https://raw.githubusercontent.com/nonexistent/repo/file.csv",
        "file_path": "",
        "is_public": True,
        "description": ""
    },
    "research_plan": [],
    "code_context": {"eda_code": "", "model_code": "", "file_name": ""},
    "review_feedback": [],
    "human_approval": ApprovalStatus.PENDING,
    "next_step": "critic"
}

result = critic_node(test_state_broken)
print(f"URL: {test_state_broken['dataset_info']['url']}")
print(f"Feedback: {result['review_feedback']}")
print(f"URL cleared: {result['dataset_info']['url'] == ''}")
print(f"Result: {'✅ PASS' if any('critical_error' in fb for fb in result['review_feedback']) else '❌ FAIL'}")

# Test 3: No URL
print("\n📋 TEST 3: Empty URL")
print("-" * 70)

test_state_empty: AgentState = {
    "messages": [],
    "user_goal": "Test workflow",
    "dataset_info": {
        "url": "",
        "file_path": "",
        "is_public": True,
        "description": ""
    },
    "research_plan": [],
    "code_context": {"eda_code": "", "model_code": "", "file_name": ""},
    "review_feedback": [],
    "human_approval": ApprovalStatus.PENDING,
    "next_step": "critic"
}

result = critic_node(test_state_empty)
print(f"URL: (empty)")
print(f"Feedback: {result['review_feedback']}")
print(f"Result: {'✅ PASS' if any('critical_error' in fb for fb in result['review_feedback']) else '❌ FAIL'}")

print("\n" + "=" * 70)
print("✅ All Tests Complete!")
print("=" * 70)
