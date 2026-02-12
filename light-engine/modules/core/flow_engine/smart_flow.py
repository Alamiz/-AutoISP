from typing import List, Optional, Callable
from playwright.sync_api import Page
from .step import Step, StepResult
from .state_handler import StateHandlerRegistry
from core.models import Account
from modules.core.flow_state import FlowResult

class Flow(Step):
    """
    Base class for a Flow, which is a composite Step that manages execution of other steps.
    """
    def run(self, page: Page) -> StepResult:
        raise NotImplementedError("Subclasses must implement run()")

class SequentialFlow(Flow):
    """
    Executes a predefined list of steps in order.
    Fails if any step fails.
    Supports RESTART: if a step returns RESTART, the entire flow re-runs from step 1 (up to max_restarts times).
    """
    def __init__(self, steps: List[Step], state_registry: Optional[StateHandlerRegistry] = None, account=None, logger=None, max_restarts: int = 3):
        super().__init__(logger=logger)
        self.steps = steps
        self.state_registry = state_registry
        self.account = account
        self.max_restarts = max_restarts

    def _check_page_state(self, page) -> Optional[StepResult]:
        """
        Check if we're on an unexpected page and handle it.
        Returns StepResult if page was handled and flow should abort/retry, None if page is expected.
        Retries identification multiple times if page is unknown.
        """
        if not self.state_registry:
            return None
            
        try:
            # Retry identification for unknown pages (similar to StatefulFlow)
            page_id = "unknown"
            max_id_attempts = 4
            
            for attempt in range(1, max_id_attempts + 1):
                page_id = self.state_registry.identify(page)
                if page_id != "unknown":
                    break
                
                if attempt < max_id_attempts:
                    wait_time = attempt * 5  # 5s, 10s, 15s
                    if self.logger:
                        self.logger.debug(
                            f"Page identification returned 'unknown'. Retrying in {wait_time}s... (Attempt {attempt}/{max_id_attempts})",
                            extra={"account_id": self.account.id if self.account else None}
                        )
                    page.wait_for_timeout(wait_time * 1000)
            
            # If still unknown after retries, log warning but continue
            if page_id == "unknown":
                if self.logger:
                    self.logger.warning(
                        "Page still unknown after multiple identification attempts. Continuing with step...",
                        extra={"account_id": self.account.id if self.account else None}
                    )
                return None
            
            # Check if there's a handler for this page
            handler = self.state_registry.get_handler(page_id)
            
            if handler:
                if self.logger:
                    self.logger.warning(f"Unexpected page detected: {page_id}. Running handler...", extra={"account_id": self.account.id})
                
                result = handler.handle(page)
                
                # If handler returns a specific failure state, return it immediately
                if result in (FlowResult.ABORT, FlowResult.FAILED, FlowResult.LOCKED, 
                              FlowResult.WRONG_EMAIL, FlowResult.WRONG_PASSWORD, 
                              FlowResult.SUSPENDED, FlowResult.PHONE_VERIFICATION, FlowResult.CAPTCHA):
                    return StepResult(status=result, message=f"Flow aborted by {page_id} handler")
                
                elif result == FlowResult.RETRY:
                    return StepResult(status=FlowResult.RETRY, message=f"Retry requested by {page_id} handler")
                
                elif result == FlowResult.RESTART:
                    return StepResult(status=FlowResult.RESTART, message=f"Restart requested by {page_id} handler")
                
                elif result == FlowResult.COMPLETED:
                     return StepResult(status=FlowResult.COMPLETED, message=f"Completed by {page_id} handler")

                # SUCCESS/SKIP -> return None to continue with current step
                    
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during page state check: {e}", extra={"account_id": self.account.id if self.account else None})
        
        return None

    def run(self, page: Page) -> StepResult:
        restart_count = 0
        
        while True:
            result = self._run_steps(page)
            
            if result.status == FlowResult.RESTART:
                restart_count += 1
                if restart_count > self.max_restarts:
                    if self.logger:
                        self.logger.error(
                            f"Max restarts ({self.max_restarts}) exceeded. Marking as FAILED.",
                            extra={"account_id": self.account.id if self.account else None}
                        )
                    return StepResult(status=FlowResult.FAILED, message=f"Max restarts ({self.max_restarts}) exceeded")
                
                if self.logger:
                    self.logger.warning(
                        f"Restarting flow from beginning (Restart {restart_count}/{self.max_restarts}): {result.message}",
                        extra={"account_id": self.account.id if self.account else None}
                    )
                page.wait_for_timeout(3000)
                continue
            
            return result

    def _run_steps(self, page: Page) -> StepResult:
        """Execute all steps sequentially. Returns the final result."""
        last_result = StepResult(status=FlowResult.SUCCESS)
        
        for i, step in enumerate(self.steps):
            # Check cancellation
            if self.logger and hasattr(step, 'job_id') and step.job_id:
                pass

            step_name = step.__class__.__name__
            
            # Check state before step
            state_result = self._check_page_state(page)
            if state_result:
                if state_result.status != FlowResult.SUCCESS:
                    # If state check returned a non-success result (ABORT, RETRY, RESTART, COMPLETED, etc.)
                    # We might need to handle RETRY specially here?
                    # If RETRY, we should probably retry the *current* step.
                    if state_result.status == FlowResult.RETRY:
                        pass # Continue to execute the step
                    else:
                        return state_result

            # Retry loop for the step
            attempt = 0
            max_retries = getattr(step, 'max_retries', 1)
            
            while attempt < max_retries:
                attempt += 1
                
                if self.logger:
                    self.logger.debug(f"Executing step {i+1}/{len(self.steps)}: {step_name} (Attempt {attempt}/{max_retries})", extra={"account_id": self.account.id})
                
                try:
                    result = step.run(page)
                    last_result = result
                    
                    if result.status == FlowResult.SUCCESS:
                        if self.logger:
                            self.logger.info(f"Step {step_name} succeeded", extra={"account_id": self.account.id})
                        break
                    
                    if result.status == FlowResult.COMPLETED:
                        if self.logger:
                            self.logger.info(f"Step {step_name} completed the flow", extra={"account_id": self.account.id})
                        return result

                    if result.status == FlowResult.SKIP:
                        if self.logger:
                            self.logger.info(f"Step {step_name} skipped: {result.message}", extra={"account_id": self.account.id})
                        break
                    
                    if result.status == FlowResult.RETRY:
                        if attempt < max_retries:
                            if self.logger:
                                self.logger.warning(f"Step {step_name} requested retry: {result.message}", extra={"account_id": self.account.id})
                            continue
                        else:
                            if self.logger:
                                self.logger.error(f"Step {step_name} failed after {max_retries} attempts", extra={"account_id": self.account.id})
                            return StepResult(status=FlowResult.FAILED, message=f"Max retries exceeded for {step_name}")
                    
                    if result.status == FlowResult.RESTART:
                         return result
                    
                    # Handle failure states
                    if result.status in (FlowResult.FAILED, FlowResult.ABORT, FlowResult.LOCKED, 
                                         FlowResult.WRONG_EMAIL, FlowResult.WRONG_PASSWORD,
                                         FlowResult.SUSPENDED, FlowResult.PHONE_VERIFICATION, FlowResult.CAPTCHA):
                        if self.logger:
                            self.logger.error(f"Step {step_name} failed with status {result.status.name}: {result.message}", extra={"account_id": self.account.id})
                        return result

                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Exception in {step_name}: {e}", extra={"account_id": self.account.id})
                    return StepResult(status=FlowResult.FAILED, message=str(e))
            else:
                 # Loop finished without break -> max retries exceeded
                 return StepResult(status=FlowResult.FAILED, message=f"Max retries exceeded for {step_name}")
                
        return StepResult(status=FlowResult.SUCCESS, message="SequentialFlow completed", payload=last_result.payload)

class StatefulFlow(Flow):
    """
    Executes a loop of Identify -> Handle -> Check Goal.
    Useful for non-linear processes like Authentication.
    """
    def __init__(
            self, 
            state_registry: StateHandlerRegistry, 
            account: Account,
            goal_checker: Callable[[Page], bool], 
            max_steps: int = 20, 
            job_id: Optional[str] = None,
            logger=None):

        super().__init__(logger=logger)
        self.state_registry = state_registry
        self.account = account
        self.goal_checker = goal_checker
        self.max_steps = max_steps
        self.job_id = job_id

    def run(self, page: Page) -> StepResult:
        steps_taken = 0
        if self.logger:
            self.logger.debug(f"Starting (max_steps={self.max_steps})", extra={"account_id": self.account.id})

        while steps_taken < self.max_steps:
            steps_taken += 1
            
            # Check cancellation
            if self.job_id:
                pass
            
            # 1. Check Goal
            try:
                if self.goal_checker(page):
                    if self.logger:
                        self.logger.debug("Goal reached!", extra={"account_id": self.account.id})
                    return StepResult(status=FlowResult.SUCCESS, message="Goal reached")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Goal check failed: {e}", extra={"account_id": self.account.id})

            # 2. Identify State
            page_id = "unknown"
            max_id_attempts = 4
            for attempt in range(1, max_id_attempts + 1):
                page_id = self.state_registry.identify(page)
                if page_id != "unknown":
                    break
                
                if attempt < max_id_attempts:
                    wait_time = attempt * 5 # 5s, 10s
                    if self.logger:
                        self.logger.debug(f"Identification returned 'unknown'. Retrying in {wait_time}s... (Attempt {attempt}/{max_id_attempts})", extra={"account_id": self.account.id})
                    page.wait_for_timeout(wait_time * 1000)
            
            if self.logger:
                self.logger.debug(f"Identified state: {page_id}", extra={"account_id": self.account.id})
            
            # 3. Handle State
            handler = self.state_registry.get_handler(page_id)
            if handler:
                if self.logger:
                    self.logger.info(f"Handling state '{page_id}'", extra={"account_id": self.account.id})
                
                result = handler.handle(page)
                
                if result == FlowResult.COMPLETED:
                    return StepResult(status=FlowResult.COMPLETED, message=f"Completed by {page_id}")
                
                elif result == FlowResult.SUCCESS:
                    # Handler succeeded, continue loop
                    continue
                    
                elif result == FlowResult.RETRY:
                    # Handler requests retry (usually means it fixed something and wants to try again)
                    continue
                    
                elif result == FlowResult.SKIP:
                    # Skip current handler (maybe not applicable here, but safe to continue)
                    continue
                    
                elif result == FlowResult.RESTART:
                    return StepResult(status=FlowResult.RESTART, message=f"Restart requested by {page_id}")
                
                elif result in (FlowResult.ABORT, FlowResult.FAILED, FlowResult.LOCKED, 
                              FlowResult.WRONG_EMAIL, FlowResult.WRONG_PASSWORD, 
                              FlowResult.SUSPENDED, FlowResult.PHONE_VERIFICATION, FlowResult.CAPTCHA):
                    return StepResult(status=result, message=f"Flow terminated by {page_id} handler")
                    
            else:
                # No handler for this state
                if page_id == "unknown":
                     if self.logger:
                         self.logger.warning("Unknown state after multiple identification attempts.", extra={"account_id": self.account.id})
                     page.wait_for_timeout(2000)
                     continue
                else:
                    # Identified but no handler?
                    if self.logger:
                        self.logger.warning(f"No handler for state '{page_id}'", extra={"account_id": self.account.id})
                    continue
                
        return StepResult(status=FlowResult.FAILED, message="Max steps exceeded in StatefulFlow")
