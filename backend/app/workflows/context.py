"""
Workflow Context.
Passes state reliably through the state machine.
"""
from __future__ import annotations

from typing import Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class WorkflowContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    session_id: str
    user_id: int
    intent: str
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
    
    # Internal state for the state machine
    current_state: str = "init"
    history: list[str] = Field(default_factory=list)
    results: Dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    
    # Callback to push events into the SSE stream
    emit_cb: Any = Field(default=None, exclude=True)

    def transition(self, new_state: str) -> None:
        self.history.append(self.current_state)
        self.current_state = new_state

