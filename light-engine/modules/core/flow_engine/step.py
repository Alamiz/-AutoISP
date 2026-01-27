# core/flow_engine/step.py
from typing import Optional, Any
from dataclasses import dataclass
from playwright.sync_api import Page
from modules.core.flow_state import FlowResult

@dataclass
class StepResult:
    """Result of a step execution, containing status, optional payload, and message."""
    status: FlowResult
    payload: Optional[Any] = None
    message: Optional[str] = None

class Step:
    """
    Base Step: deterministic unit of action in a flow.
    Implement `run` in subclasses.
    """
    max_retries = 2  # per step

    def __init__(self, automation=None, logger=None):
        self.automation = automation
        self.logger = logger
        self.account = automation.account if automation else None

    def run(self, page: Page) -> StepResult:
        """
        Perform the action. Must return StepResult.
        """
        raise NotImplementedError("Subclasses must implement run()")