#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

from unittest.mock import Mock, patch
import numpy as np
from qam.enhanced_scheduler import EnhancedQUBOScheduler
from qam.quantum_reasoning import QuantumReasoningState, DecisionPath
from qam.scheduler import QUBOScheduler, QUBOTerm

class MockQUBOScheduler(QUBOScheduler):
    def __init__(self):
        self.terms = []
        
    def build_qubo_with_reasoning(self, horizon, state):
        return [QUBOTerm(coefficient=1.0, variables=[0, 1])]
        
    def _solve_quantum(self, terms, horizon):
        return np.ones(horizon)

def create_mock_quantum_state():
    state = Mock(spec=QuantumReasoningState)
    state.add_decision_path = Mock()
    state.get_probabilities = Mock(return_value={})
    return state

def test_enhanced_scheduler():
    print("\nTesting EnhancedQUBOScheduler...")
    
    with patch('qam.enhanced_scheduler.QUBOScheduler', MockQUBOScheduler):
        # Test 1: Create scheduler
        print("\n1. Testing scheduler creation")
        scheduler = EnhancedQUBOScheduler()
        print("Scheduler created successfully")
        
        # Test 2: Build hierarchical QUBO
        print("\n2. Testing hierarchical QUBO building")
        tasks = [
            {
                "id": "task1",
                "dependencies": [],
                "required_resources": ["cpu", "memory"]
            },
            {
                "id": "task2",
                "dependencies": ["task1"],
                "required_resources": ["gpu", "memory"]
            }
        ]
        
        clusters = {
            "cluster1": {
                "available_resources": ["cpu", "memory"],
                "current_load": 0.5,
                "capacity": 1.0
            },
            "cluster2": {
                "available_resources": ["gpu", "memory"],
                "current_load": 0.3,
                "capacity": 1.0
            }
        }
        
        levels = scheduler.build_hierarchical_qubo(tasks, clusters, max_cluster_size=2)
        print(f"Built {len(levels)} hierarchical levels")
        
        # Test 3: Cluster assignments
        print("\n3. Testing cluster assignments")
        assignments = scheduler.optimize_cluster_assignments(tasks, clusters)
        print(f"Cluster assignments: {assignments}")
        assert len(assignments) == len(tasks)
        
        # Test 4: Task to cluster assignment
        print("\n4. Testing task to cluster assignment")
        task_clusters = scheduler._assign_tasks_to_clusters(tasks, clusters, max_cluster_size=2)
        print(f"Task clusters: {task_clusters}")
        assert len(task_clusters) == len(clusters)
        
        # Test 5: Schedule optimization with reasoning
        print("\n5. Testing schedule optimization with reasoning")
        mock_state = create_mock_quantum_state()
        
        with patch('qam.enhanced_scheduler.QuantumReasoningState', return_value=mock_state):
            result = scheduler.optimize_schedule_with_reasoning(tasks, horizon=2, reasoning_state=mock_state)
            print(f"Optimization result: {result}")
        
        # Test 6: Cluster decision paths
        print("\n6. Testing cluster decision paths")
        state = QuantumReasoningState()
        scheduler._add_cluster_decision_paths(state, tasks)
        print(f"Added decision paths to state")
        
        # Test 7: Build and solve cluster QUBO
        print("\n7. Testing cluster QUBO building and solving")
        qubo_result = scheduler._build_and_solve_cluster_qubo(tasks, horizon=2)
        if qubo_result is not None:
            print(f"QUBO matrix shape: {qubo_result.shape}")
            assert isinstance(qubo_result, np.ndarray)
            assert qubo_result.shape == (2, 2)  # Should match horizon
        
        # Test 8: Parallel processing
        print("\n8. Testing parallel processing")
        large_tasks = []
        for i in range(10):  # Create more tasks to test parallel processing
            large_tasks.append({
                "id": f"task{i}",
                "dependencies": [],
                "required_resources": ["cpu"]
            })
        
        levels = scheduler.build_hierarchical_qubo(large_tasks, clusters, max_cluster_size=3)
        print(f"Processed {len(levels)} levels in parallel")

if __name__ == "__main__":
    try:
        test_enhanced_scheduler()
        print("\n✅ All enhanced scheduler tests completed successfully")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")