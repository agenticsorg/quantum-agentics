#!/usr/bin/env python3
import sys
import os
import numpy as np
# Add project root to sys.path so that modules can be found (following the example_agent_run.py approach)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, project_root)

from agents.qam_agent.tools.qam_tools import QAMTools

def run_qaoa_optimization():
    sample_config = {
        "agent_name": "QAOAOptimizationExample",
        "settings": {
            "qaoa_p_steps": 4,
            "qaoa_learning_rate": 0.1
        }
    }
    
    tools = QAMTools(sample_config)
    
    # Create problem Hamiltonian
    n_vars = 3  # x1, x2, x3
    n_states = 2**n_vars
    
    # Initialize Hamiltonian with scaled coefficients to improve numerical stability
    hamiltonian = np.zeros((n_states, n_states), dtype=np.complex128)
    
    # QUBO coefficients (scaled down)
    scale = 0.1  # Scaling factor to prevent numerical overflow
    qubo_coeffs = {
        (0, 0): 1.0 * scale,    # x1*x1
        (0, 1): -1.0 * scale,   # x1*x2
        (1, 1): 2.0 * scale,    # x2*x2
        (1, 2): -0.5 * scale,   # x2*x3
        (2, 2): 1.5 * scale     # x3*x3
    }
    
    # Convert QUBO to Hamiltonian
    for state in range(n_states):
        binary = format(state, f'0{n_vars}b')
        bits = [int(b) for b in binary]
        
        # Diagonal terms
        energy = 0
        for i in range(n_vars):
            if (i, i) in qubo_coeffs:
                energy += qubo_coeffs[(i, i)] * bits[i]
        
        # Off-diagonal terms
        for (i, j), coeff in qubo_coeffs.items():
            if i != j:
                energy += coeff * bits[i] * bits[j]
                
        hamiltonian[state, state] = energy
            
    print("Running QAOA Optimization Example using QAMTools...")
    try:
        optimized_params = tools.qaoa_optimizer.optimize(hamiltonian)
    except Exception as e:
        optimized_params = {"error": str(e)}
    
    print("Optimized QAOA Parameters:")
    print(optimized_params)

if __name__ == "__main__":
    run_qaoa_optimization()
