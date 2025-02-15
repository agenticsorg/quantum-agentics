import unittest
import numpy as np
from qam.hierarchical_qubo import HierarchicalQUBO, QUBOLevel

class TestHierarchicalQUBO(unittest.TestCase):
    def setUp(self):
        self.qubo = HierarchicalQUBO()
        
    def test_add_level(self):
        # Create simple QUBO matrix
        matrix = np.array([[1, -1], [-1, 1]])
        variables = ['x0', 'x1']
        constraints = {'x0': 1}
        
        # Add level
        level_idx = self.qubo.add_level(matrix, variables, constraints)
        
        # Verify level was added
        self.assertEqual(level_idx, 0)
        self.assertEqual(len(self.qubo.levels), 1)
        
        # Verify level properties
        level = self.qubo.levels[0]
        np.testing.assert_array_equal(level.matrix, matrix)
        self.assertEqual(level.variables, variables)
        self.assertEqual(level.constraints, constraints)
        
    def test_add_level_validation(self):
        # Test non-square matrix
        non_square = np.array([[1, -1]])
        with self.assertRaises(ValueError):
            self.qubo.add_level(non_square)
            
        # Test mismatched variables
        matrix = np.array([[1, -1], [-1, 1]])
        variables = ['x0']  # Should be length 2
        with self.assertRaises(ValueError):
            self.qubo.add_level(matrix, variables)
            
    def test_add_connection(self):
        # Add two levels
        matrix1 = np.array([[1, -1], [-1, 1]])
        matrix2 = np.array([[1, 0], [0, 1]])
        
        level1_idx = self.qubo.add_level(matrix1)
        level2_idx = self.qubo.add_level(matrix2)
        
        # Add connection
        success = self.qubo.add_connection(level1_idx, level2_idx, 0.5)
        self.assertTrue(success)
        self.assertEqual(len(self.qubo.connections), 1)
        
        # Test duplicate connection
        success = self.qubo.add_connection(level1_idx, level2_idx, 0.5)
        self.assertFalse(success)
        
        # Test invalid indices
        success = self.qubo.add_connection(99, level2_idx, 0.5)
        self.assertFalse(success)
        
    def test_optimize_simple(self):
        # Create simple one-level QUBO
        matrix = np.array([[1, -1], [-1, 1]])
        self.qubo.add_level(matrix)
        
        # Optimize
        result = self.qubo.optimize()
        
        # Verify result structure
        self.assertIn('level_0', result)
        self.assertIsInstance(result['level_0'], np.ndarray)
        self.assertEqual(len(result['level_0']), 2)
        
    def test_optimize_hierarchical(self):
        # Create two-level QUBO
        matrix1 = np.array([[1, -1], [-1, 1]])
        matrix2 = np.array([[1, 0], [0, 1]])
        
        self.qubo.add_level(matrix1)
        self.qubo.add_level(matrix2)
        self.qubo.add_connection(0, 1, 0.5)
        
        # Optimize
        result = self.qubo.optimize()
        
        # Verify results for both levels
        self.assertIn('level_0', result)
        self.assertIn('level_1', result)
        self.assertEqual(len(result['level_0']), 2)
        self.assertEqual(len(result['level_1']), 2)
        
    def test_optimize_with_constraints(self):
        # Create QUBO with constraints
        matrix = np.array([[1, -1], [-1, 1]])
        variables = ['x0', 'x1']
        constraints = {'x0': 1}  # Constrain x0 to be 1
        
        self.qubo.add_level(matrix, variables, constraints)
        
        # Optimize
        result = self.qubo.optimize()
        
        # Verify result respects constraint
        self.assertIn('level_0', result)
        solution = result['level_0']
        self.assertEqual(solution[0], 1)  # x0 should be 1
        
    def test_get_level_info(self):
        # Add level with variables and constraints
        matrix = np.array([[1, -1], [-1, 1]])
        variables = ['x0', 'x1']
        constraints = {'x0': 1}
        
        level_idx = self.qubo.add_level(matrix, variables, constraints)
        
        # Test get_level_variables
        vars = self.qubo.get_level_variables(level_idx)
        self.assertEqual(vars, variables)
        
        # Test get_level_constraints
        cons = self.qubo.get_level_constraints(level_idx)
        self.assertEqual(cons, constraints)
        
        # Test invalid level index
        self.assertIsNone(self.qubo.get_level_variables(99))
        self.assertIsNone(self.qubo.get_level_constraints(99))
        
    def test_empty_optimization(self):
        # Test optimization with no levels
        result = self.qubo.optimize()
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()