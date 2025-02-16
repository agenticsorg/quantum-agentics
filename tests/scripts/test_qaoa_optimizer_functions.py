#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

import numpy as np
from qam.qaoa_optimizer import QAOAOptimizer, OptimizationResult

def test_qaoa_optimizer():
    print("\nTesting QAOAOptimizer...")
    
    # Test 1: Create optimizer
    print("\n1. Testing optimizer creation")
    optimizer = QAOAOptimizer()
    print("Optimizer created successfully")
    
    # Test 2: Set circuit parameters
    print("\n2. Testing parameter setting")
    new_params = {
        'p_steps': 3,
        'learning_rate': 0.05,
        'max_iterations': 50
    }
    optimizer.set_circuit_parameters(new_params)
    print(f"Parameters updated: {optimizer.circuit_parameters}")
    assert optimizer.circuit_parameters['p_steps'] == 3
    
    # Test 3: Create test problem
    print("\n3. Testing problem creation")
    n_qubits = 3
    problem_size = 2**n_qubits
    # Create a simple test Hamiltonian (diagonal in computational basis)
    hamiltonian = np.diag(np.random.uniform(-1, 1, problem_size))
    print(f"Created {n_qubits}-qubit problem")
    
    # Test 4: Create uniform superposition
    print("\n4. Testing initial state creation")
    initial_state = optimizer._create_uniform_superposition(n_qubits)
    print(f"Initial state created with shape: {initial_state.shape}")
    assert len(initial_state) == problem_size
    assert np.isclose(np.sum(np.abs(initial_state)**2), 1.0)
    
    # Test 5: Apply mixing operator
    print("\n5. Testing mixing operator")
    beta = 0.5
    mixed_state = optimizer._apply_mixing_operator(initial_state, beta)
    print("Mixing operator applied")
    assert len(mixed_state) == problem_size
    assert np.isclose(np.sum(np.abs(mixed_state)**2), 1.0)
    
    # Test 6: Apply phase separator
    print("\n6. Testing phase separator")
    gamma = 0.3
    phase_state = optimizer._apply_phase_separator(initial_state, hamiltonian, gamma)
    print("Phase separator applied")
    assert len(phase_state) == problem_size
    assert np.isclose(np.sum(np.abs(phase_state)**2), 1.0)
    
    # Test 7: Calculate energy
    print("\n7. Testing energy calculation")
    energy = optimizer._calculate_energy(initial_state, hamiltonian)
    print(f"Energy calculated: {energy}")
    assert isinstance(energy, float)
    
    # Test 8: Update parameters
    print("\n8. Testing parameter updates")
    gamma_arr = np.array([0.1, 0.2])
    beta_arr = np.array([0.3, 0.4])
    new_gamma, new_beta = optimizer._update_parameters(
        gamma_arr, beta_arr, hamiltonian, initial_state, energy
    )
    print("Parameters updated")
    assert len(new_gamma) == len(gamma_arr)
    assert len(new_beta) == len(beta_arr)
    
    # Test 9: Full optimization
    print("\n9. Testing full optimization")
    result = optimizer.optimize(hamiltonian)
    print(f"Optimization completed in {result.iterations} iterations")
    print(f"Final energy: {result.energy}")
    assert isinstance(result, OptimizationResult)
    assert len(result.solution) == problem_size
    
    # Test 10: Optimization history
    print("\n10. Testing optimization history")
    history = optimizer.get_optimization_history()
    print(f"History length: {len(history)}")
    assert len(history) == 1  # Should have one optimization result
    
    # Test 11: Multiple optimizations
    print("\n11. Testing multiple optimizations")
    # Create a different Hamiltonian
    new_hamiltonian = np.diag(np.random.uniform(-1, 1, problem_size))
    result2 = optimizer.optimize(new_hamiltonian)
    print(f"Second optimization completed in {result2.iterations} iterations")
    history = optimizer.get_optimization_history()
    assert len(history) == 2  # Should have two optimization results
    
    # Test 12: Measure state
    print("\n12. Testing state measurement")
    final_state = np.zeros(problem_size)
    final_state[0] = 1.0  # Create a definite state
    measured = optimizer._measure_state(final_state)
    print(f"Measured state shape: {measured.shape}")
    assert np.array_equal(measured, final_state)  # Should return same state for definite input

if __name__ == "__main__":
    try:
        test_qaoa_optimizer()
        print("\n✅ All QAOA optimizer tests completed successfully")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")