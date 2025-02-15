import pytest
import numpy as np
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