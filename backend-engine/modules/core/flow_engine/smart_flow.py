# core/flow_engine/smart_flow.py
from typing import List, Optional, Callable, Any
from playwright.sync_api import Page
from .step import Step, StepResult, StepStatus
from .state_handler import StateHandlerRegistry

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
    """
    def __init__(self, steps: List[Step], state_registry: Optional[StateHandlerRegistry] = None, logger=None):
        super().__init__(logger=logger)
        self.steps = steps
        self.state_registry = state_registry

    def _check_page_state(self, page) -> Optional[StepResult]:
        """
        Check if we're on an unexpected page and handle it.
        Returns StepResult if page was handled and flow should abort/retry, None if page is expected.
        """
        if not self.state_registry:
            return None
            
        try:
            page_id = self.state_registry.identify(page)
            
            # Check if there's a handler for this unexpected page
            handler = self.state_registry.get_handler(page_id)
            
            if handler:
                if self.logger:
                    self.logger.warning(f"SequentialFlow: Unexpected page detected: {page_id}. Running handler...")
                
                action = handler.handle(page)
                
                if action == "abort":
                    return StepResult(status=StepStatus.FAILURE, message=f"Flow aborted by {page_id} handler")
                elif action == "retry":
                    return StepResult(status=StepStatus.RETRY, message=f"Retry requested by {page_id} handler")
                # continue -> return None
                    
        except Exception as e:
            if self.logger:
                self.logger.error(f"SequentialFlow: Error during page state check: {e}")
        
        return None

    def run(self, page: Page) -> StepResult:
        last_result = StepResult(status=StepStatus.SUCCESS)
        
        for i, step in enumerate(self.steps):
            step_name = step.__class__.__name__
            
            # Check state before step
            state_result = self._check_page_state(page)
            if state_result:
                if state_result.status == StepStatus.FAILURE:
                    return state_result
                if state_result.status == StepStatus.RETRY:
                    # If handler says retry, we should probably retry the *current* step?
                    # But we haven't started it yet.
                    # So we just continue to execute the step.
                    # Wait, if handler fixed it (e.g. closed popup), we proceed.
                    pass

            # Retry loop for the step
            attempt = 0
            max_retries = getattr(step, 'max_retries', 1)
            
            while attempt < max_retries:
                attempt += 1
                
                if self.logger:
                    self.logger.info(f"SequentialFlow: Executing step {i+1}/{len(self.steps)}: {step_name} (Attempt {attempt}/{max_retries})")
                
                try:
                    result = step.run(page)
                    last_result = result
                    
                    if result.status == StepStatus.SUCCESS:
                        if self.logger:
                            self.logger.info(f"SequentialFlow: Step {step_name} succeeded")
                        break
                    
                    if result.status == StepStatus.FAILURE:
                        if self.logger:
                            self.logger.error(f"SequentialFlow: Step {step_name} failed: {result.message}")
                        return result
                    
                    if result.status == StepStatus.RETRY:
                        if attempt < max_retries:
                            if self.logger:
                                self.logger.warning(f"SequentialFlow: Step {step_name} requested retry: {result.message}")
                            page.wait_for_timeout(1000)
                            continue
                        else:
                            if self.logger:
                                self.logger.error(f"SequentialFlow: Step {step_name} failed after {max_retries} attempts")
                            return StepResult(status=StepStatus.FAILURE, message=f"Max retries exceeded for {step_name}")
                        
                    if result.status == StepStatus.SKIP:
                        if self.logger:
                            self.logger.info(f"SequentialFlow: Step {step_name} skipped: {result.message}")
                        break

                except Exception as e:
                    if self.logger:
                        self.logger.error(f"SequentialFlow: Exception in {step_name}: {e}")
                    return StepResult(status=StepStatus.FAILURE, message=str(e))
            else:
                 # Loop finished without break -> max retries exceeded (if not handled inside)
                 pass
                
        return StepResult(status=StepStatus.SUCCESS, message="SequentialFlow completed", payload=last_result.payload)

class StatefulFlow(Flow):
    """
    Executes a loop of Identify -> Handle -> Check Goal.
    Useful for non-linear processes like Authentication.
    """
    def __init__(self, 
                 state_registry: StateHandlerRegistry, 
                 goal_checker: Callable[[Page], bool], 
                 max_steps: int = 20, 
                 logger=None):
        super().__init__(logger=logger)
        self.state_registry = state_registry
        self.goal_checker = goal_checker
        self.max_steps = max_steps

    def run(self, page: Page) -> StepResult:
        steps_taken = 0
        if self.logger:
            self.logger.info(f"StatefulFlow: Starting (max_steps={self.max_steps})")

        while steps_taken < self.max_steps:
            steps_taken += 1
            
            # 1. Check Goal
            try:
                if self.goal_checker(page):
                    if self.logger:
                        self.logger.info("StatefulFlow: Goal reached!")
                    return StepResult(status=StepStatus.SUCCESS, message="Goal reached")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"StatefulFlow: Goal check failed: {e}")

            # 2. Identify State
            page_id = self.state_registry.identify(page)
            if self.logger:
                self.logger.debug(f"StatefulFlow: Identified state: {page_id}")
            
            # 3. Handle State
            handler = self.state_registry.get_handler(page_id)
            if handler:
                if self.logger:
                    self.logger.info(f"StatefulFlow: Handling state '{page_id}'")
                
                action = handler.handle(page)
                
                if action == "abort":
                    return StepResult(status=StepStatus.FAILURE, message=f"Aborted by handler for {page_id}")
                elif action == "retry":
                    # Handler requests retry (usually means it fixed something and wants to try again)
                    page.wait_for_timeout(1000)
                    continue
                elif action == "continue":
                    # Handler processed state, continue loop
                    page.wait_for_timeout(1000)
                    continue
            else:
                # No handler for this state
                if page_id == "unknown":
                     if self.logger:
                         self.logger.warning("StatefulFlow: Unknown state and no handler. Retrying identification...")
                     page.wait_for_timeout(2000)
                     continue
                else:
                    # Identified but no handler?
                    if self.logger:
                        self.logger.warning(f"StatefulFlow: No handler for state '{page_id}'")
                    page.wait_for_timeout(2000)
                    continue
                
        return StepResult(status=StepStatus.FAILURE, message="Max steps exceeded in StatefulFlow")
