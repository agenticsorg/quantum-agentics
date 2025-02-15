import pytest
import numpy as np
import time
import psutil
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from qam.scheduler import QUBOScheduler, QUBOTerm
from qam.quantum_reasoning import QuantumReasoningState, DecisionPath

def test_qubo_term_creation():
    term = QUBOTerm(1, 2, 0.5)
    assert term.i == 1
    assert term.j == 2
    assert term.weight == 0.5

def test_build_qubo_with_reasoning():
    scheduler = QUBOScheduler()
    state = QuantumReasoningState()
    
    # Add some decision paths to the state
    path1 = DecisionPath(id="1", probability=0.6, actions=["schedule_0"])
    path2 = DecisionPath(id="2", probability=0.4, actions=["schedule_1"])
    
    state.add_decision_path(path1, np.sqrt(0.6))
    state.add_decision_path(path2, np.sqrt(0.4))
    
    # Build QUBO terms
    horizon = 2
    terms = scheduler.build_qubo_with_reasoning(horizon, state)
    
    # Verify basic properties
    assert len(terms) == 3  # For horizon 2, expect 3 terms (2 diagonal + 1 off-diagonal)
    assert all(isinstance(term, QUBOTerm) for term in terms)
    
    # Verify weights are influenced by reasoning state
    diagonal_terms = [t for t in terms if t.i == t.j]
    assert len(diagonal_terms) == 2
    
    # First position should have higher weight due to path1's higher probability
    assert diagonal_terms[0].weight > diagonal_terms[1].weight

def test_optimize_schedule_with_reasoning():
    scheduler = QUBOScheduler()
    state = QuantumReasoningState()
    
    # Create a state that strongly prefers early scheduling
    path = DecisionPath(id="1", probability=1.0, actions=["schedule_0"])
    state.add_decision_path(path, 1.0)
    
    # Create some tasks
    tasks = [
        {'id': 'task1', 'duration': 1},
        {'id': 'task2', 'duration': 1}
    ]
    
    # Optimize schedule
    result = scheduler.optimize_schedule_with_reasoning(tasks, 2, state)
    
    # Verify result structure
    assert 'schedule' in result
    assert 'objective_value' in result
    assert 'reasoning_influence' in result
    
    # Verify schedule assignments
    assert len(result['schedule']) == 2
    assert all(isinstance(pos, int) for pos in result['schedule'].values())
    
    # Verify reasoning influence
    assert 0 <= result['reasoning_influence'] <= 1.0

def test_reasoning_weight_calculation():
    scheduler = QUBOScheduler()
    state = QuantumReasoningState()
    
    # Add paths with different probabilities
    paths = [
        DecisionPath(id="1", probability=0.7, actions=["schedule_0"]),
        DecisionPath(id="2", probability=0.3, actions=["schedule_1"])
    ]
    
    for path in paths:
        state.add_decision_path(path, np.sqrt(path.probability))
    
    # Build QUBO to initialize reasoning weights
    scheduler.build_qubo_with_reasoning(2, state)
    
    # Calculate reasoning factors
    factor_0 = scheduler._calculate_reasoning_factor(0, 0)  # Diagonal term
    factor_01 = scheduler._calculate_reasoning_factor(0, 1)  # Off-diagonal term
    
    # Verify reasoning factors
    assert factor_0 > 0  # Diagonal term should be positive
    assert factor_01 < 0  # Off-diagonal term should be negative (penalty)
    assert factor_0 > abs(factor_01)  # Diagonal influence should be stronger

def test_empty_reasoning_state():
    scheduler = QUBOScheduler()
    state = QuantumReasoningState()
    
    # Build QUBO with empty state
    terms = scheduler.build_qubo_with_reasoning(2, state)
    
    # Should still create basic QUBO terms
    assert len(terms) > 0
    
    # Weights should be based only on base calculations
    for term in terms:
        if term.i == term.j:
            assert np.isclose(term.weight, 1.0)  # Diagonal terms
        else:
            assert term.weight < 1.0  # Off-diagonal terms

def test_schedule_optimization_consistency():
    scheduler = QUBOScheduler()
    state = QuantumReasoningState()
    
    # Create balanced state
    paths = [
        DecisionPath(id="1", probability=0.5, actions=["schedule_0"]),
        DecisionPath(id="2", probability=0.5, actions=["schedule_1"])
    ]
    
    for path in paths:
        state.add_decision_path(path, np.sqrt(path.probability))
    
    tasks = [
        {'id': 'task1', 'duration': 1},
        {'id': 'task2', 'duration': 1}
    ]
    
    # Run optimization multiple times
    results = [
        scheduler.optimize_schedule_with_reasoning(tasks, 2, state)
        for _ in range(5)
    ]
    
    # Verify objective values are consistent
    objective_values = [r['objective_value'] for r in results]
    assert max(objective_values) - min(objective_values) < 1e-10
    
    # Verify reasoning influence is consistent
    influences = [r['reasoning_influence'] for r in results]
    assert all(i == influences[0] for i in influences)

def test_performance_benchmarks():
    """Test performance metrics of the scheduler."""
    scheduler = QUBOScheduler()
    state = QuantumReasoningState()
    
    # Create complex state with multiple paths
    for i in range(10):
        path = DecisionPath(
            id=str(i),
            probability=1.0/10,
            actions=[f"schedule_{i}"]
        )
        state.add_decision_path(path, np.sqrt(1.0/10))
    
    # Create large task set
    tasks = [
        {'id': f'task{i}', 'duration': 1}
        for i in range(20)
    ]
    
    # Measure execution time
    start_time = time.time()
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    result = scheduler.optimize_schedule_with_reasoning(tasks, 20, state)
    
    end_time = time.time()
    final_memory = process.memory_info().rss
    
    # Performance assertions
    execution_time = end_time - start_time
    memory_usage = final_memory - initial_memory
    
    logger.debug(f"Execution time: {execution_time:.3f}s")
    logger.debug(f"Memory usage: {memory_usage / 1024 / 1024:.2f}MB")
    
    assert execution_time < 1.0  # Should complete within 1 second
    assert memory_usage < 50 * 1024 * 1024  # Should use less than 50MB additional memory
    assert len(result['schedule']) == len(tasks)

def test_complex_scheduling_scenario():
    """Test scheduler with complex constraints and dependencies."""
    scheduler = QUBOScheduler()
    state = QuantumReasoningState()
    
    # Create state with complex scheduling preferences
    paths = [
        DecisionPath(id="1", probability=0.4, actions=["schedule_0", "schedule_2"]),
        DecisionPath(id="2", probability=0.3, actions=["schedule_1", "schedule_3"]),
        DecisionPath(id="3", probability=0.3, actions=["schedule_2", "schedule_0"])
    ]
    
    for path in paths:
        state.add_decision_path(path, np.sqrt(path.probability))
    
    # Create tasks with dependencies
    tasks = [
        {'id': 'task1', 'duration': 1, 'dependencies': []},
        {'id': 'task2', 'duration': 2, 'dependencies': ['task1']},
        {'id': 'task3', 'duration': 1, 'dependencies': []},
        {'id': 'task4', 'duration': 1, 'dependencies': ['task2']}
    ]
    
    result = scheduler.optimize_schedule_with_reasoning(tasks, 4, state)
    schedule = result['schedule']
    
    logger.debug(f"Generated schedule: {schedule}")
    
    # Verify schedule respects dependencies
    assert schedule['task1'] < schedule['task2'], f"Task1 ({schedule['task1']}) should be before Task2 ({schedule['task2']})"
    assert schedule['task2'] < schedule['task4'], f"Task2 ({schedule['task2']}) should be before Task4 ({schedule['task4']})"

def test_edge_cases():
    """Test scheduler behavior with edge cases."""
    scheduler = QUBOScheduler()
    state = QuantumReasoningState()
    
    # Test with single task
    single_task = [{'id': 'task1', 'duration': 1}]
    result = scheduler.optimize_schedule_with_reasoning(single_task, 1, state)
    assert result['schedule']['task1'] == 0
    
    # Test with no tasks
    empty_result = scheduler.optimize_schedule_with_reasoning([], 1, state)
    assert len(empty_result['schedule']) == 0
    
    # Test with horizon smaller than tasks
    tasks = [
        {'id': f'task{i}', 'duration': 1}
        for i in range(5)
    ]
    result = scheduler.optimize_schedule_with_reasoning(tasks, 3, state)
    assert len(result['schedule']) == 3  # Should only schedule first 3 tasks

def test_resource_utilization():
    """Test resource utilization tracking."""
    scheduler = QUBOScheduler()
    state = QuantumReasoningState()
    
    # Create resource-constrained tasks
    tasks = [
        {'id': 'task1', 'duration': 1, 'resources': ['cpu', 'memory']},
        {'id': 'task2', 'duration': 1, 'resources': ['cpu']},
        {'id': 'task3', 'duration': 1, 'resources': ['memory']},
        {'id': 'task4', 'duration': 1, 'resources': ['cpu', 'memory']}
    ]
    
    result = scheduler.optimize_schedule_with_reasoning(tasks, 4, state)
    schedule = result['schedule']
    
    logger.debug(f"Resource utilization schedule: {schedule}")
    
    # Verify resource constraints
    for i, task1 in enumerate(tasks):
        for j, task2 in enumerate(tasks[i+1:], i+1):
            if set(task1['resources']) & set(task2['resources']):
                # Tasks sharing resources should not be scheduled at same time
                assert schedule[task1['id']] != schedule[task2['id']], \
                    f"Tasks {task1['id']} and {task2['id']} share resources but scheduled at same time {schedule[task1['id']]}"