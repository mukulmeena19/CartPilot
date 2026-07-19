"""
Workflow Context.
Passes state reliably through the state machine.
"""
from __future__ import annotations

from typing import Dict, Any
from pydantic import BaseModel, Field


class WorkflowContext(BaseModel):
    session_id: str
    user_id: int
    intent: str
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
    
    # Internal state for the state machine
    current_state: str = "init"
    history: list[str] = Field(default_factory=list)
    results: Dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)

    def transition(self, new_state: str) -> None:
        self.history.append(self.current_state)
        self.current_state = new_state
