#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

import numpy as np
from qam.quantum_reasoning import (
    DecisionPath,
    Decision,
    Outcome,
    QuantumReasoningState,
    QuantumReACT
)

def test_quantum_reasoning():
    print("\nTesting Quantum Reasoning Components...")
    
    # Test 1: Create DecisionPath
    print("\n1. Testing DecisionPath creation")
    path = DecisionPath(
        id="test_path_1",
        probability=0.7,
        actions=["action1", "action2"]
    )
    print(f"Decision path created: {path}")
    assert path.probability == 0.7
    assert len(path.actions) == 2
    
    # Test 2: Create Decision
    print("\n2. Testing Decision creation")
    decision = Decision(
        id="test_decision_1",
        action="action1",
        confidence=0.8,
        path=path
    )
    print(f"Decision created: {decision}")
    assert decision.confidence == 0.8
    assert decision.path == path
    
    # Test 3: Create Outcome
    print("\n3. Testing Outcome creation")
    outcome = Outcome(
        decision_id="test_decision_1",
        success=True,
        feedback={"result": "success"},
        timestamp=float(np.datetime64('now').astype('float64'))
    )
    print(f"Outcome created: {outcome}")
    assert outcome.success
    
    # Test 4: QuantumReasoningState
    print("\n4. Testing QuantumReasoningState")
    state = QuantumReasoningState()
    
    # Add decision paths
    path1 = DecisionPath(id="path1", probability=0.6, actions=["a1"])
    path2 = DecisionPath(id="path2", probability=0.4, actions=["a2"])
    
    state.add_decision_path(path1, np.sqrt(0.6))
    state.add_decision_path(path2, np.sqrt(0.4))
    
    # Test state vector
    state_vector = state.get_state_vector()
    print(f"State vector shape: {state_vector.shape}")
    assert len(state_vector) == 2
    
    # Test probabilities
    probs = state.get_probabilities()
    print(f"Probabilities: {probs}")
    assert len(probs) == 2
    assert np.isclose(sum(probs.values()), 1.0)
    
    # Test measurement
    measured_path = state.measure()
    print(f"Measured path: {measured_path}")
    assert isinstance(measured_path, DecisionPath)
    
    # Test 5: QuantumReACT
    print("\n5. Testing QuantumReACT")
    react = QuantumReACT()
    
    # Test decision making
    context = {
        'available_actions': ['action1', 'action2'],
        'uncertainty': 0.3
    }
    
    decision = react.make_decision(context, state)
    print(f"Made decision: {decision.action}")
    assert decision.action in context['available_actions']
    
    # Test reflection
    outcome = Outcome(
        decision_id=decision.id,
        success=True,
        feedback={'action': decision.action},
        timestamp=float(np.datetime64('now').astype('float64'))
    )
    react.reflect_and_adjust(outcome, state)
    print("Reflection completed")
    
    # Test 6: State evolution
    print("\n6. Testing state evolution")
    # Create a simple Hamiltonian
    hamiltonian = np.array([[1, -1], [-1, 1]])
    state.evolve(hamiltonian)
    print("State evolved")
    
    # Test 7: Multiple decisions
    print("\n7. Testing multiple decisions")
    decisions = []
    for _ in range(3):
        decision = react.make_decision(context, state)
        decisions.append(decision)
        outcome = Outcome(
            decision_id=decision.id,
            success=True,
            feedback={'action': decision.action},
            timestamp=float(np.datetime64('now').astype('float64'))
        )
        react.reflect_and_adjust(outcome, state)
    print(f"Made {len(decisions)} decisions")
    assert len(decisions) == 3
    
    # Test 8: Learning rate effect
    print("\n8. Testing learning rate effect")
    original_rate = react.learning_rate
    react.learning_rate = 0.5
    decision = react.make_decision(context, state)
    print(f"Decision with modified learning rate: {decision.action}")
    react.learning_rate = original_rate
    
    # Test 9: State validation
    print("\n9. Testing state validation")
    # Add paths with unnormalized amplitudes
    state = QuantumReasoningState()
    state.add_decision_path(path1, 1.0)
    state.add_decision_path(path2, 1.0)
    # State should automatically normalize
    probs = state.get_probabilities()
    print(f"Normalized probabilities: {probs}")
    assert np.isclose(sum(probs.values()), 1.0)

if __name__ == "__main__":
    try:
        test_quantum_reasoning()
        print("\n✅ All quantum reasoning tests completed successfully")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")