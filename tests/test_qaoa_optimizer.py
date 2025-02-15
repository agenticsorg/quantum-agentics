import unittest
import numpy as np
from qam.qaoa_optimizer import QAOAOptimizer, OptimizationResult

class TestQAOAOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = QAOAOptimizer()
        
    def test_simple_optimization(self):
        # Create a simple 2-qubit problem Hamiltonian
        hamiltonian = np.array([
            [1, 0, 0, 0],
            [0, -1, 0, 0],
            [0, 0, -1, 0],
            [0, 0, 0, 1]
        ])
        
        # Run optimization
        result = self.optimizer.optimize(hamiltonian)
        
        # Verify result structure
        self.assertIsInstance(result, OptimizationResult)
        self.assertIsInstance(result.solution, np.ndarray)
        self.assertIsInstance(result.energy, float)
        self.assertIsInstance(result.parameters, dict)
        self.assertIsInstance(result.history, list)
        
        # Verify solution dimensions
        self.assertEqual(result.solution.shape, (4,))
        
        # Verify energy is real
        self.assertIsInstance(result.energy, float)
        
        # Verify parameters contain gamma and beta
        self.assertIn('gamma', result.parameters)
        self.assertIn('beta', result.parameters)
        
    def test_optimization_convergence(self):
        # Create a simple optimization problem
        hamiltonian = np.array([
            [1, -1],
            [-1, 1]
        ])
        
        # Set strict convergence parameters
        self.optimizer.set_circuit_parameters({
            'convergence_threshold': 1e-6,
            'max_iterations': 50
        })
        
        # Run optimization
        result = self.optimizer.optimize(hamiltonian)
        
        # Verify convergence
        if len(result.history) > 1:
            final_improvement = abs(result.history[-1] - result.history[-2])
            self.assertLess(final_improvement, 1e-6)
            
    def test_parameter_updates(self):
        # Test parameter update functionality
        new_params = {
            'p_steps': 3,
            'learning_rate': 0.05
        }
        
        self.optimizer.set_circuit_parameters(new_params)
        
        # Verify parameters were updated
        self.assertEqual(self.optimizer.circuit_parameters['p_steps'], 3)
        self.assertEqual(self.optimizer.circuit_parameters['learning_rate'], 0.05)
        
        # Verify other parameters remain unchanged
        self.assertIn('max_iterations', self.optimizer.circuit_parameters)
        self.assertIn('convergence_threshold', self.optimizer.circuit_parameters)
        
    def test_optimization_history(self):
        # Create simple problem
        hamiltonian = np.array([
            [1, 0],
            [0, -1]
        ])
        
        # Run multiple optimizations
        self.optimizer.optimize(hamiltonian)
        self.optimizer.optimize(hamiltonian)
        
        # Get history
        history = self.optimizer.get_optimization_history()
        
        # Verify history
        self.assertEqual(len(history), 2)
        self.assertIsInstance(history[0], OptimizationResult)
        self.assertIsInstance(history[1], OptimizationResult)
        
    def test_initial_state(self):
        # Create simple Hamiltonian
        hamiltonian = np.array([
            [1, 0],
            [0, -1]
        ])
        
        # Create custom initial state
        initial_state = np.array([1, 0]) / np.sqrt(2)
        
        # Run optimization with custom state
        result = self.optimizer.optimize(hamiltonian, initial_state)
        
        # Verify optimization completed
        self.assertIsNotNone(result)
        self.assertIsInstance(result.solution, np.ndarray)
        
    def test_energy_calculation(self):
        # Create simple Hamiltonian
        hamiltonian = np.array([
            [1, 0],
            [0, -1]
        ])
        
        # Create test state
        state = np.array([0, 1])  # Should give energy -1
        
        # Calculate energy
        energy = self.optimizer._calculate_energy(state, hamiltonian)
        
        # Verify energy
        self.assertAlmostEqual(energy, -1.0)
        
    def test_uniform_superposition(self):
        # Test 2-qubit superposition
        state = self.optimizer._create_uniform_superposition(2)
        
        # Verify state properties
        self.assertEqual(len(state), 4)
        self.assertAlmostEqual(np.sum(np.abs(state)**2), 1.0)  # Normalized
        self.assertTrue(np.allclose(np.abs(state), 0.5))  # Equal superposition

if __name__ == '__main__':
    unittest.main()