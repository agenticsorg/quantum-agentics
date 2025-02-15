"""Unit tests for QAM Agent implementation."""

import unittest
import json
import os
from pathlib import Path
import yaml
import sys

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, project_root)

from agents.qam_agent.agent import QAMAgent
from agents.qam_agent.tools.custom_tool import QuantumSchedulingTools

class TestQAMAgent(unittest.TestCase):
    def setUp(self):
        # Load test configuration
        config_dir = Path(__file__).parent.parent / 'config'
        
        with open(config_dir / 'tasks.yaml', 'r') as f:
            self.tasks_config = yaml.safe_load(f)
            
        self.test_config = {
            "agent_name": "TestQAMAgent",
            "mode": "test",
            "settings": {
                "qaoa_p_steps": 3,
                "qaoa_learning_rate": 0.1,
                "cluster_threshold": 50,
                "optimization_target": 0.8
            }
        }
        self.agent = QAMAgent(self.test_config)
        self.tools = QuantumSchedulingTools()

    def test_agent_initialization(self):
        """Test agent initialization with configuration."""
        self.assertEqual(self.agent.agent_name, "TestQAMAgent")
        self.assertEqual(self.agent.mode, "test")
        self.assertIsNotNone(self.agent.scheduler)
        self.assertIsNotNone(self.agent.settings)
        
    def test_dependency_analysis(self):
        """Test task dependency analysis tool."""
        sample_tasks = self.tasks_config['sample_scheduling_problem']['tasks']
        analysis = self.tools.analyze_task_dependencies(sample_tasks)
        
        self.assertIn('dependency_graph', analysis)
        self.assertIn('critical_paths', analysis)
        self.assertIn('max_path_length', analysis)
        
        # Verify critical path length
        self.assertEqual(analysis['max_path_length'], 4)
        
    def test_resource_optimization(self):
        """Test resource allocation optimization."""
        sample_tasks = self.tasks_config['sample_scheduling_problem']['tasks']
        sample_resources = self.tasks_config['sample_scheduling_problem']['resources']
        
        result = self.tools.optimize_resource_allocation(
            sample_tasks,
            sample_resources
        )
        
        self.assertIn('allocations', result)
        self.assertIn('utilization', result)
        
        # Verify resource utilization is within bounds
        for resource, util in result['utilization'].items():
            self.assertGreaterEqual(util, 0.0)
            self.assertLessEqual(util, 1.0)
            
    def test_quantum_schedule_generation(self):
        """Test quantum-optimized schedule generation."""
        sample_tasks = self.tasks_config['sample_scheduling_problem']['tasks']
        sample_resources = self.tasks_config['sample_scheduling_problem']['resources']
        
        parameters = {
            'qaoa_p_steps': 3,
            'qaoa_learning_rate': 0.1,
            'convergence_threshold': 1e-5
        }
        
        result = self.tools.generate_quantum_schedule(
            sample_tasks,
            sample_resources,
            parameters
        )
        
        self.assertIn('schedule', result)
        self.assertIn('objective_value', result)
        self.assertIn('reasoning_influence', result)
        
        # Verify schedule properties
        schedule = result['schedule']
        self.assertEqual(len(schedule), len(sample_tasks))
        
        # Verify time slots are within bounds
        max_time = self.tasks_config['sample_scheduling_problem']['constraints']['deadline']
        for task_id, time_slot in schedule.items():
            self.assertLessEqual(time_slot, max_time)
            
    def test_react_validation(self):
        """Test ReACT methodology validation."""
        from agents.qam_agent.config.react_validation import ReACTValidator
        
        validator = ReACTValidator()
        test_response = """
[THOUGHT] Analyzing the quantum scheduling problem requires careful consideration of task dependencies and resource constraints. The critical path analysis suggests potential bottlenecks in quantum processor utilization. We need to analyze the QUBO formulation and QAOA parameters to optimize the scheduling solution. The reasoning process must account for both quantum and classical resource requirements.

[ACTION] Initialize QUBO formulation with the following steps:
1. Map task dependencies to matrix constraints
2. Configure QAOA parameters for optimization
3. Setup resource allocation tracking
4. Prepare quantum state initialization
5. Define measurement strategy

[OBSERVATION] Initial analysis reveals:
- Critical path length: 4 time units
- Resource contention on quantum processor
- Potential for parallel classical preprocessing
- QAOA parameter sensitivity analysis needed
- Quantum state preparation overhead identified

[REFLECTION] The quantum optimization approach shows promise for this scheduling problem because of the complex resource interactions and multiple viable execution paths. The analysis suggests that careful tuning of QAOA parameters and quantum resource allocation will be crucial for achieving optimal results. Further investigation of the parameter landscape may reveal additional optimization opportunities.
"""
        results = validator.validate_response(test_response)
        
        # Verify all ReACT components are present and valid
        self.assertTrue(all(results.values()))
        
        # Verify optimization reasoning
        thought_content = test_response.split('[ACTION]')[0].split('[THOUGHT]')[1]
        self.assertTrue(validator.validate_optimization_reasoning(thought_content))
        
    def test_output_generation(self):
        """Test agent output generation and saving."""
        decisions = self.agent.run()
        
        # Verify decisions are generated
        self.assertIsInstance(decisions, list)
        self.assertGreater(len(decisions), 0)
        
        # Verify output file is created
        output_file = "qam_agent_output.json"
        self.assertTrue(os.path.exists(output_file))
        
        # Verify output format
        with open(output_file, 'r') as f:
            output = json.load(f)
        self.assertIn('decisions', output)
        self.assertEqual(len(output['decisions']), len(decisions))

if __name__ == '__main__':
    unittest.main()