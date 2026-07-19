import pytest
from app.workflows.context import WorkflowContext
from app.workflows.base import BaseWorkflow

class MockWorkflow(BaseWorkflow):
    def register_states(self) -> None:
        self.states = {
            "init": self.state_init,
            "step_one": self.state_step_one,
            "completed": self.state_completed
        }

    async def state_init(self, context: WorkflowContext) -> None:
        context.transition("step_one")

    async def state_step_one(self, context: WorkflowContext) -> None:
        context.results["step"] = 1
        context.transition("completed")

    async def state_completed(self, context: WorkflowContext) -> None:
        pass

@pytest.mark.asyncio
async def test_workflow_state_transitions():
    workflow = MockWorkflow()
    context = WorkflowContext(
        session_id="session-1",
        user_id=1,
        intent="mock_intent"
    )
    
    result_context = await workflow.execute(context)
    
    assert result_context.current_state == "completed"
    assert result_context.results["step"] == 1
    assert result_context.history == ["init", "step_one"]

class ErrorWorkflow(BaseWorkflow):
    def register_states(self) -> None:
        self.states = {
            "init": self.state_init,
            "completed": self.state_completed
        }

    async def state_init(self, context: WorkflowContext) -> None:
        raise ValueError("Intentional crash")

    async def state_completed(self, context: WorkflowContext) -> None:
        pass

@pytest.mark.asyncio
async def test_workflow_graceful_failure():
    workflow = ErrorWorkflow()
    context = WorkflowContext(
        session_id="session-2",
        user_id=1,
        intent="error_intent"
    )
    
    result_context = await workflow.execute(context)
    
    assert result_context.current_state == "failed"
    assert len(result_context.errors) == 1
    assert "Intentional crash" in result_context.errors[0]
