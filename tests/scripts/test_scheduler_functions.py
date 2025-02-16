#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

import numpy as np
from unittest.mock import patch, MagicMock
from qam.scheduler import QUBOScheduler, QUBOTerm
from qam.quantum_reasoning import QuantumReasoningState, DecisionPath

def create_mock_quantum_state():
    state = QuantumReasoningState()
    path1 = DecisionPath(id="path1", probability=0.6, actions=["schedule_0"])
    path2 = DecisionPath(id="path2", probability=0.4, actions=["schedule_1"])
    state.add_decision_path(path1, np.sqrt(0.6))
    state.add_decision_path(path2, np.sqrt(0.4))
    return state

def test_scheduler():
    print("\nTesting QUBOScheduler...")
    
    # Mock Azure Quantum client
    mock_quantum_client = MagicMock()
    mock_quantum_client.submit_qubo.return_value = "test-job-id"
    mock_quantum_client.wait_for_job.return_value = {
        "solutions": [{
            "configuration": {"0": 1.0, "1": 0.0}
        }]
    }
    
    with patch('qam.scheduler.AzureQuantumClient', return_value=mock_quantum_client):
        # Test 1: Create scheduler
        print("\n1. Testing scheduler creation")
        scheduler = QUBOScheduler()
        print("Scheduler created successfully")
        
        # Test 2: Create QUBO term
        print("\n2. Testing QUBO term creation")
        term = QUBOTerm(i=0, j=1, weight=0.5)
        print(f"QUBO term created: i={term.i}, j={term.j}, weight={term.weight}")
        assert term.weight == 0.5
        
        # Test 3: Build QUBO with reasoning
        print("\n3. Testing QUBO building with reasoning")
        state = create_mock_quantum_state()
        terms = scheduler.build_qubo_with_reasoning(horizon=2, reasoning_state=state)
        print(f"Built {len(terms)} QUBO terms")
        assert len(terms) > 0
        
        # Test 4: Calculate term weights
        print("\n4. Testing term weight calculation")
        weight = scheduler._calculate_term_weight(0, 1)
        print(f"Calculated weight: {weight}")
        assert isinstance(weight, float)
        
        # Test 5: Prepare quantum problem
        print("\n5. Testing quantum problem preparation")
        problem = scheduler._prepare_quantum_problem(terms)
        print(f"Problem prepared with {len(problem['problem']['terms'])} terms")
        assert 'problem' in problem
        assert 'terms' in problem['problem']
        
        # Test 6: Schedule optimization
        print("\n6. Testing schedule optimization")
        tasks = [
            {
                "id": "task1",
                "dependencies": [],
                "resources": ["cpu"]
            },
            {
                "id": "task2",
                "dependencies": ["task1"],
                "resources": ["memory"]
            }
        ]
        
        result = scheduler.optimize_schedule_with_reasoning(
            tasks=tasks,
            horizon=2,
            reasoning_state=state
        )
        print(f"Optimization result: {result}")
        assert 'schedule' in result
        assert 'objective_value' in result
        
        # Test 7: Dependency validation
        print("\n7. Testing dependency validation")
        schedule = {"task1": 0, "task2": 1}
        valid = scheduler._validate_dependencies(tasks, schedule)
        print(f"Dependency validation: {valid}")
        assert valid
        
        # Invalid schedule (dependency violation)
        invalid_schedule = {"task1": 1, "task2": 0}
        valid = scheduler._validate_dependencies(tasks, schedule)
        print(f"Invalid dependency validation: {valid}")
        
        # Test 8: Resource validation
        print("\n8. Testing resource validation")
        valid = scheduler._validate_resources(tasks, schedule)
        print(f"Resource validation: {valid}")
        assert valid
        
        # Test resource conflict
        conflicting_tasks = [
            {
                "id": "task1",
                "resources": ["cpu"]
            },
            {
                "id": "task2",
                "resources": ["cpu"]
            }
        ]
        conflict_schedule = {"task1": 0, "task2": 0}
        valid = scheduler._validate_resources(conflicting_tasks, conflict_schedule)
        print(f"Resource conflict validation: {not valid}")
        assert not valid
        
        # Test 9: Classical solver
        print("\n9. Testing classical solver")
        solution = scheduler._solve_classical(terms, size=2)
        print(f"Classical solution: {solution}")
        assert len(solution) == 2
        
        # Test 10: Energy calculation
        print("\n10. Testing energy calculation")
        energy = scheduler._calculate_energy(solution, terms)
        print(f"Calculated energy: {energy}")
        assert isinstance(energy, float)
        
        # Test 11: Empty task list
        print("\n11. Testing empty task list")
        result = scheduler.optimize_schedule_with_reasoning([], horizon=2, reasoning_state=state)
        print(f"Empty task result: {result}")
        assert result['schedule'] == {}
        
        # Test 12: Large schedule
        print("\n12. Testing large schedule")
        large_tasks = []
        for i in range(10):
            large_tasks.append({
                "id": f"task{i}",
                "dependencies": [f"task{j}" for j in range(max(0, i-1), i)],
                "resources": ["cpu"] if i % 2 == 0 else ["memory"]
            })
        
        result = scheduler.optimize_schedule_with_reasoning(
            tasks=large_tasks,
            horizon=5,
            reasoning_state=state
        )
        print(f"Large schedule optimization completed with {len(result['schedule'])} tasks")
        assert len(result['schedule']) > 0

if __name__ == "__main__":
    try:
        test_scheduler()
        print("\n✅ All scheduler tests completed successfully")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")