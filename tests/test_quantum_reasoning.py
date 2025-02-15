import pytest
import numpy as np
from qam.quantum_reasoning import (
    QuantumReasoningState, 
    QuantumReACT,
    DecisionPath,
    Decision,
    Outcome
)

def test_quantum_state_initialization():
    state = QuantumReasoningState()
    assert state.amplitudes == {}
    assert state.history == []

def test_add_decision_path():
    state = QuantumReasoningState()
    path = DecisionPath(id="test1", probability=0.5, actions=["action1"])
    
    # Add single path
    state.add_decision_path(path, 1.0)
    assert len(state.amplitudes) == 1
    assert np.isclose(abs(state.amplitudes[path]), 1.0)
    
    # Add second path - should normalize automatically
    path2 = DecisionPath(id="test2", probability=0.5, actions=["action2"])
    state.add_decision_path(path2, 1.0)
    assert len(state.amplitudes) == 2
    assert np.isclose(abs(state.amplitudes[path]), 1/np.sqrt(2))
    assert np.isclose(abs(state.amplitudes[path2]), 1/np.sqrt(2))

def test_state_evolution():
    state = QuantumReasoningState()
    path1 = DecisionPath(id="1", probability=0.5, actions=["a1"])
    path2 = DecisionPath(id="2", probability=0.5, actions=["a2"])
    
    # Initialize with equal superposition
    state.add_decision_path(path1, 1/np.sqrt(2))
    state.add_decision_path(path2, 1/np.sqrt(2))
    
    # Create simple rotation Hamiltonian
    theta = np.pi/4  # 45 degree rotation
    hamiltonian = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])
    
    # Evolve state
    state.evolve(hamiltonian)
    
    # Verify evolution maintains normalization
    evolved_vector = state.get_state_vector()
    assert np.isclose(np.sum(np.abs(evolved_vector)**2), 1.0)
    
    # Verify unitary evolution
    assert len(evolved_vector) == 2
    assert np.allclose(hamiltonian @ hamiltonian.T, np.eye(2))

def test_quantum_react_initialization():
    react = QuantumReACT()
    assert len(react.outcomes) == 0
    assert len(react.decision_weights) == 0

def test_decision_making():
    react = QuantumReACT()
    state = QuantumReasoningState()
    
    context = {
        'available_actions': ['action1', 'action2'],
        'uncertainty': 0.5
    }
    
    decision = react.make_decision(context, state)
    
    assert isinstance(decision, Decision)
    assert decision.action in context['available_actions']
    assert 0 <= decision.confidence <= 1
    assert isinstance(decision.path, DecisionPath)

def test_reflection_and_adjustment():
    react = QuantumReACT()
    state = QuantumReasoningState()
    
    # Make initial decision
    context = {
        'available_actions': ['action1', 'action2'],
        'uncertainty': 0.5
    }
    
    decision = react.make_decision(context, state)
    initial_weight = react.decision_weights.get(decision.action, 1.0)
    
    # Create successful outcome
    outcome = Outcome(
        decision_id=decision.id,
        success=True,
        feedback={'action': decision.action},
        timestamp=float(np.datetime64('now').astype('float64'))
    )
    
    # Reflect on outcome
    react.reflect_and_adjust(outcome, state)
    
    # Verify weight adjustment
    assert len(react.decision_weights) > 0
    assert react.decision_weights[decision.action] > initial_weight

def test_multiple_decisions_learning():
    np.random.seed(42)  # For reproducibility
    react = QuantumReACT()
    
    # Make several decisions and provide feedback
    for _ in range(5):
        state = QuantumReasoningState()  # Fresh state for each decision
        context = {
            'available_actions': ['action1', 'action2'],  # Fixed list syntax
            'uncertainty': 0.5
        }
        
        decision = react.make_decision(context, state)
        
        # Simulate success for action1, failure for action2
        success = decision.action == 'action1'
        
        outcome = Outcome(
            decision_id=decision.id,
            success=success,
            feedback={'action': decision.action},
            timestamp=float(np.datetime64('now').astype('float64'))
        )
        
        react.reflect_and_adjust(outcome, state)
    
    # After several iterations, action1 should have higher weight
    assert react.decision_weights['action1'] > react.decision_weights['action2']

def test_hamiltonian_generation():
    react = QuantumReACT()
    
    # Test with 2 actions
    context = {'available_actions': ['a1', 'a2'], 'uncertainty': 0.5}
    hamiltonian = react._create_evolution_hamiltonian(context)
    assert hamiltonian.shape == (2, 2)
    assert np.allclose(hamiltonian @ hamiltonian.T, np.eye(2))  # Should be unitary
    
    # Test with 3 actions
    context = {'available_actions': ['a1', 'a2', 'a3'], 'uncertainty': 0.5}
    hamiltonian = react._create_evolution_hamiltonian(context)
    assert hamiltonian.shape == (3, 3)
    assert np.allclose(hamiltonian @ hamiltonian.T, np.eye(3))  # Should be unitary

def test_empty_context():
    react = QuantumReACT()
    state = QuantumReasoningState()
    
    context = {
        'available_actions': [],
        'uncertainty': 0.5
    }
    
    # Should handle empty action list gracefully
    hamiltonian = react._create_evolution_hamiltonian(context)
    assert hamiltonian.size == 0  # Empty array
    
    # Should raise ValueError when trying to make decision with no actions
    with pytest.raises(ValueError, match="No available actions in context"):
        react.make_decision(context, state)