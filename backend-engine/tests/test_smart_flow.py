import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from unittest.mock import MagicMock
from core.flow_engine.smart_flow import SequentialFlow, StatefulFlow
from core.flow_engine.step import Step, StepResult, StepStatus
from core.flow_engine.state_handler import StateHandlerRegistry

class MockStep(Step):
    def __init__(self, name, result_status=StepStatus.SUCCESS, result_message=""):
        super().__init__()
        self.name = name
        self.result_status = result_status
        self.result_message = result_message
        self.run_count = 0

    def run(self, page):
        self.run_count += 1
        return StepResult(status=self.result_status, message=self.result_message)

class TestSequentialFlow(unittest.TestCase):
    def setUp(self):
        self.page = MagicMock()
        self.logger = MagicMock()

    def test_sequential_execution(self):
        step1 = MockStep("Step1")
        step2 = MockStep("Step2")
        flow = SequentialFlow([step1, step2], logger=self.logger)
        
        result = flow.run(self.page)
        
        self.assertEqual(result.status, StepStatus.SUCCESS)
        self.assertEqual(step1.run_count, 1)
        self.assertEqual(step2.run_count, 1)

    def test_failure_stops_execution(self):
        step1 = MockStep("Step1", StepStatus.FAILURE, "Failed")
        step2 = MockStep("Step2")
        flow = SequentialFlow([step1, step2], logger=self.logger)
        
        result = flow.run(self.page)
        
        self.assertEqual(result.status, StepStatus.FAILURE)
        self.assertEqual(step1.run_count, 1)
        self.assertEqual(step2.run_count, 0)

    def test_retry_logic(self):
        # Mock a step that fails once then succeeds? 
        # Currently MockStep is static. Let's make a dynamic one.
        step = MagicMock(spec=Step)
        step.max_retries = 3
        # First call returns RETRY, second returns SUCCESS
        step.run.side_effect = [
            StepResult(StepStatus.RETRY, message="Try again"),
            StepResult(StepStatus.SUCCESS, message="Done")
        ]
        
        flow = SequentialFlow([step], logger=self.logger)
        result = flow.run(self.page)
        
        self.assertEqual(result.status, StepStatus.SUCCESS)
        self.assertEqual(step.run.call_count, 2)

class TestStatefulFlow(unittest.TestCase):
    def setUp(self):
        self.page = MagicMock()
        self.logger = MagicMock()
        self.registry = MagicMock(spec=StateHandlerRegistry)

    def test_goal_reached_immediately(self):
        goal_checker = MagicMock(return_value=True)
        flow = StatefulFlow(self.registry, goal_checker, logger=self.logger)
        
        result = flow.run(self.page)
        
        self.assertEqual(result.status, StepStatus.SUCCESS)
        goal_checker.assert_called_once()

    def test_handle_state_then_goal(self):
        # 1. Goal check fails
        # 2. Identify returns "login"
        # 3. Handler fixes it
        # 4. Goal check succeeds
        goal_checker = MagicMock(side_effect=[False, True])
        
        self.registry.identify.return_value = "login"
        handler = MagicMock()
        handler.handle.return_value = "continue"
        self.registry.get_handler.return_value = handler
        
        flow = StatefulFlow(self.registry, goal_checker, max_steps=5, logger=self.logger)
        result = flow.run(self.page)
        
        self.assertEqual(result.status, StepStatus.SUCCESS)
        self.assertEqual(goal_checker.call_count, 2)
        handler.handle.assert_called_once()

if __name__ == '__main__':
    unittest.main()
