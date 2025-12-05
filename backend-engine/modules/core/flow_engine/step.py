# core/flow_engine/step.py
from enum import Enum
from typing import Optional, Any
from playwright.sync_api import Page

class StepStatus(Enum):
    SUCCESS = "success"
    RETRY = "retry"
    SKIP = "skip"
    FAILURE = "failure"

class StepResult:
    def __init__(self, status: StepStatus, payload: Optional[Any] = None, message: Optional[str] = None):
        self.status = status
        self.payload = payload
        self.message = message

class Step:
    """
    Base Step: deterministic unit of action in a flow.
    Implement `run` in subclasses.
    """
    max_retries = 2  # per step

    def __init__(self, human_action=None, logger=None):
        self.human = human_action
        self.logger = logger

    def run(self, page: Page) -> StepResult:
        """
        Perform the action. Must return StepResult.
        """
        raise NotImplementedError("Subclasses must implement run()")
