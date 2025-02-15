import unittest
import json
import os
from agents.qam_agent.agent import QAMAgent

class TestQAMAgent(unittest.TestCase):
    def setUp(self):
        self.config = {
            "agent_name": "UnitTestQAMAgent",
            "mode": "unittest",
            "settings": {
                "argument1": "test_value",
                "argument2": 3,
                "evaluation_options": ["optionA", "optionB"]
            }
        }
        self.agent = QAMAgent(self.config)

    def test_run_returns_decisions(self):
        decisions = self.agent.run()
        self.assertIsInstance(decisions, list)
        self.assertEqual(len(decisions), 3)

    def test_default_configuration(self):
        default_config = {}
        agent = QAMAgent(default_config)
        decisions = agent.run()
        self.assertTrue(any("Task_0" in d for d in decisions))

if __name__ == "__main__":
    unittest.main()