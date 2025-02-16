#!/usr/bin/env python3
from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass, field

@dataclass
class OptimizationResult:
    """Represents the result of a QAOA optimization."""
    solution: np.ndarray
    energy: float
    parameters: Dict[str, float]
    success: bool
    iterations: int
    history: List[float] = field(default_factory=list)

class QAOAOptimizer:
    """Implements QAOA for various optimization tasks."""
    
    def __init__(self):
        self.circuit_parameters: Dict[str, float] = {
            'p_steps': 2,  # Number of QAOA steps
            'learning_rate': 0.1,
            'max_iterations': 100,
            'convergence_threshold': 1e-5
        }
        self.optimization_history: List[OptimizationResult] = []
        
    def optimize(self, problem_hamiltonian: np.ndarray,
                initial_state: Optional[np.ndarray] = None) -> OptimizationResult:
        """
        Run QAOA optimization on the given problem.
        
        Args:
            problem_hamiltonian: Matrix representing the problem Hamiltonian
            initial_state: Optional initial state vector
            
        Returns:
            OptimizationResult: Optimization results and metrics
        """
        n_qubits = int(np.log2(problem_hamiltonian.shape[0]))
        
        # Initialize state if not provided
        if initial_state is None:
            initial_state = self._create_uniform_superposition(n_qubits)
            
        # Initialize optimization parameters
        gamma = np.random.uniform(0, 2*np.pi, self.circuit_parameters['p_steps'])
        beta = np.random.uniform(0, np.pi, self.circuit_parameters['p_steps'])
        
        # Optimization loop
        energies = []
        current_state = initial_state.copy()
        
        for iteration in range(self.circuit_parameters['max_iterations']):
            # Apply QAOA circuit
            evolved_state = self._apply_qaoa_circuit(
                current_state,
                problem_hamiltonian,
                gamma,
                beta
            )
            
            # Calculate energy
            energy = self._calculate_energy(evolved_state, problem_hamiltonian)
            energies.append(energy)
            
            # Check convergence
            if iteration > 0 and abs(energies[-1] - energies[-2]) < self.circuit_parameters['convergence_threshold']:
                break
                
            # Update parameters
            gamma, beta = self._update_parameters(
                gamma,
                beta,
                problem_hamiltonian,
                evolved_state,
                energy
            )
            
            current_state = evolved_state
            
        # Get final solution
        solution = self._measure_state(current_state)
        
        # Create result
        result = OptimizationResult(
            solution=solution,
            energy=energies[-1],
            parameters={
                'gamma': gamma.tolist(),
                'beta': beta.tolist()
            },
            success=len(energies) < self.circuit_parameters['max_iterations'],
            iterations=len(energies),
            history=energies
        )
        
        # Record optimization
        self.optimization_history.append(result)
        
        return result
        
    def _create_uniform_superposition(self, n_qubits: int) -> np.ndarray:
        """Create uniform superposition state."""
        state = np.ones(2**n_qubits, dtype=np.complex128) / np.sqrt(2**n_qubits)
        return state
        
    def _apply_qaoa_circuit(self, state: np.ndarray,
                           hamiltonian: np.ndarray,
                           gamma: np.ndarray,
                           beta: np.ndarray) -> np.ndarray:
        """Apply QAOA circuit to the state."""
        current_state = state.copy()
        
        for p in range(len(gamma)):
            # Problem unitary
            current_state = self._apply_phase_separator(current_state, hamiltonian, gamma[p])
            # Mixing unitary
            current_state = self._apply_mixing_operator(current_state, beta[p])
            
        return current_state
        
    def _apply_phase_separator(self, state: np.ndarray,
                             hamiltonian: np.ndarray,
                             gamma: float) -> np.ndarray:
        """Apply phase separation operator using diagonal form."""
        phases = np.diag(hamiltonian)
        return state * np.exp(-1j * gamma * phases)
        
    def _apply_mixing_operator(self, state: np.ndarray,
                             beta: float) -> np.ndarray:
        """Apply mixing operator using single-qubit rotations."""
        n_qubits = int(np.log2(len(state)))
        new_state = np.zeros_like(state, dtype=np.complex128)
        
        # Apply X rotation to each qubit
        for q in range(n_qubits):
            # Create rotation matrix for single qubit
            cos_beta = np.cos(beta)
            sin_beta = np.sin(beta)
            rot = np.array([[cos_beta, -1j*sin_beta],
                           [-1j*sin_beta, cos_beta]], dtype=np.complex128)
            
            # Apply rotation to each basis state
            for i in range(0, 2**n_qubits, 2**(q+1)):
                for j in range(2**q):
                    idx0 = i + j
                    idx1 = idx0 + 2**q
                    # Apply 2x2 rotation
                    new_state[idx0] = rot[0,0] * state[idx0] + rot[0,1] * state[idx1]
                    new_state[idx1] = rot[1,0] * state[idx0] + rot[1,1] * state[idx1]
                    
        return new_state
        
    def _calculate_energy(self, state: np.ndarray,
                         hamiltonian: np.ndarray) -> float:
        """Calculate energy expectation value."""
        return float(np.real(state.conj() @ hamiltonian @ state))
        
    def _update_parameters(self, gamma: np.ndarray,
                          beta: np.ndarray,
                          hamiltonian: np.ndarray,
                          state: np.ndarray,
                          energy: float) -> Tuple[np.ndarray, np.ndarray]:
        """Update QAOA parameters using stable gradient estimation."""
        lr = self.circuit_parameters['learning_rate'] * 0.1
        eps = 1e-7
        
        gamma_grad = np.zeros_like(gamma)
        beta_grad = np.zeros_like(beta)
        
        # Calculate gradients using central difference
        for p in range(len(gamma)):
            # Gamma gradient
            gamma_plus = gamma.copy()
            gamma_minus = gamma.copy()
            gamma_plus[p] += eps
            gamma_minus[p] -= eps
            
            energy_plus = self._calculate_energy(
                self._apply_qaoa_circuit(state, hamiltonian, gamma_plus, beta),
                hamiltonian
            )
            energy_minus = self._calculate_energy(
                self._apply_qaoa_circuit(state, hamiltonian, gamma_minus, beta),
                hamiltonian
            )
            
            gamma_grad[p] = (energy_plus - energy_minus) / (2 * eps)
            
            # Beta gradient
            beta_plus = beta.copy()
            beta_minus = beta.copy()
            beta_plus[p] += eps
            beta_minus[p] -= eps
            
            energy_plus = self._calculate_energy(
                self._apply_qaoa_circuit(state, hamiltonian, gamma, beta_plus),
                hamiltonian
            )
            energy_minus = self._calculate_energy(
                self._apply_qaoa_circuit(state, hamiltonian, gamma, beta_minus),
                hamiltonian
            )
            
            beta_grad[p] = (energy_plus - energy_minus) / (2 * eps)
        
        # Clip gradients
        max_grad = 1.0
        gamma_grad = np.clip(gamma_grad, -max_grad, max_grad)
        beta_grad = np.clip(beta_grad, -max_grad, max_grad)
        
        # Update parameters
        gamma = gamma - lr * gamma_grad
        beta = beta - lr * beta_grad
        
        return gamma, beta
        
    def _measure_state(self, state: np.ndarray) -> np.ndarray:
        """Perform measurement on the final state."""
        probabilities = np.abs(state)**2
        # Return most probable basis state
        return np.eye(len(state))[np.argmax(probabilities)]
        
    def get_optimization_history(self) -> List[OptimizationResult]:
        """Get history of optimization results."""
        return self.optimization_history.copy()
        
    def set_circuit_parameters(self, parameters: Dict[str, float]) -> None:
        """Update circuit parameters."""
        self.circuit_parameters.update(parameters)
