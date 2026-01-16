"""
Workflow State Management

Handles persistence and retrieval of workflow states.
In production, this would integrate with a database or state store.
"""

import uuid
from datetime import datetime
from typing import Dict, Optional

from core import AgentState, ApprovalStatus, CodeContext, DatasetInfo, setup_logger

logger = setup_logger("state_manager", level="INFO")


class WorkflowStateManager:
    """
    Manages workflow state persistence and retrieval
    
    In production, this would use Redis, PostgreSQL, or a similar
    state store. For now, uses in-memory storage.
    """
    
    def __init__(self):
        self._states: Dict[str, AgentState] = {}
        self._metadata: Dict[str, dict] = {}
    
    def create_workflow(self, user_goal: str, dataset_url: str = "") -> str:
        """
        Create a new workflow with initial state
        
        Args:
            user_goal: The user's objective
            dataset_url: Optional dataset URL
        
        Returns:
            workflow_id: Unique identifier for the workflow
        """
        workflow_id = f"wf-{uuid.uuid4().hex[:12]}"
        
        # Initialize state
        initial_state: AgentState = {
            "messages": [],
            "user_goal": user_goal,
            "dataset_info": DatasetInfo(
                url=dataset_url,
                file_path="",
                is_public=True,
                description=""
            ),
            "research_plan": [],
            "code_context": CodeContext(),
            "review_feedback": [],
            "human_approval": ApprovalStatus.PENDING,
            "next_step": "research_agent"
        }
        
        self._states[workflow_id] = initial_state
        self._metadata[workflow_id] = {
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "initialized"
        }
        
        logger.info("Created new workflow", workflow_id=workflow_id, user_goal=user_goal)
        
        return workflow_id
    
    def get_state(self, workflow_id: str) -> Optional[AgentState]:
        """
        Retrieve workflow state
        
        Args:
            workflow_id: Workflow identifier
        
        Returns:
            AgentState if found, None otherwise
        """
        state = self._states.get(workflow_id)
        
        if state:
            logger.info("Retrieved workflow state", workflow_id=workflow_id)
        else:
            logger.warning("Workflow not found", workflow_id=workflow_id)
        
        return state
    
    def update_state(self, workflow_id: str, state: AgentState) -> bool:
        """
        Update workflow state
        
        Args:
            workflow_id: Workflow identifier
            state: Updated state
        
        Returns:
            True if successful, False otherwise
        """
        if workflow_id not in self._states:
            logger.error("Cannot update non-existent workflow", workflow_id=workflow_id)
            return False
        
        self._states[workflow_id] = state
        self._metadata[workflow_id]["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info("Updated workflow state", workflow_id=workflow_id, next_step=state.get("next_step"))
        
        return True
    
    def get_metadata(self, workflow_id: str) -> Optional[dict]:
        """Get workflow metadata"""
        return self._metadata.get(workflow_id)
    
    def set_status(self, workflow_id: str, status: str) -> bool:
        """Update workflow status"""
        if workflow_id not in self._metadata:
            return False
        
        self._metadata[workflow_id]["status"] = status
        self._metadata[workflow_id]["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info("Updated workflow status", workflow_id=workflow_id, status=status)
        
        return True
    
    def approve_step(self, workflow_id: str) -> bool:
        """Approve a workflow step requiring human review"""
        state = self.get_state(workflow_id)
        
        if not state:
            return False
        
        state["human_approval"] = ApprovalStatus.APPROVED
        self.update_state(workflow_id, state)
        
        logger.info("Workflow step approved", workflow_id=workflow_id)
        
        return True
    
    def reject_step(self, workflow_id: str) -> bool:
        """Reject a workflow step requiring human review"""
        state = self.get_state(workflow_id)
        
        if not state:
            return False
        
        state["human_approval"] = ApprovalStatus.REJECTED
        self.update_state(workflow_id, state)
        
        logger.info("Workflow step rejected", workflow_id=workflow_id)
        
        return True
    
    def list_workflows(self) -> list:
        """List all workflows with metadata"""
        workflows = []
        
        for workflow_id, metadata in self._metadata.items():
            state = self._states.get(workflow_id)
            
            workflows.append({
                "workflow_id": workflow_id,
                "user_goal": state["user_goal"] if state else "",
                "status": metadata.get("status", "unknown"),
                "created_at": metadata.get("created_at"),
                "updated_at": metadata.get("updated_at"),
                "current_step": state.get("next_step") if state else "unknown"
            })
        
        return workflows


# Global state manager instance
state_manager = WorkflowStateManager()
