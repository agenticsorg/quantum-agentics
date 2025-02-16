#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

import numpy as np
from qam.hierarchical_qubo import HierarchicalQUBO, QUBOLevel

def test_hierarchical_qubo():
    print("\nTesting HierarchicalQUBO...")
    
    # Test 1: Create QUBO
    print("\n1. Testing QUBO creation")
    qubo = HierarchicalQUBO()
    print("QUBO created successfully")
    
    # Test 2: Add level with matrix
    print("\n2. Testing level addition")
    matrix1 = np.array([[1, -1], [-1, 1]])
    variables1 = ["x1", "x2"]
    constraints1 = {"x1": 1.0}
    
    level_idx1 = qubo.add_level(
        qubo_matrix=matrix1,
        variables=variables1,
        constraints=constraints1,
        weight=1.0
    )
    print(f"Added level with index {level_idx1}")
    
    # Test 3: Add another level
    print("\n3. Testing multiple level addition")
    matrix2 = np.array([[2, 0], [0, 2]])
    variables2 = ["y1", "y2"]
    level_idx2 = qubo.add_level(
        qubo_matrix=matrix2,
        variables=variables2,
        weight=0.5
    )
    print(f"Added second level with index {level_idx2}")
    
    # Test 4: Add connection between levels
    print("\n4. Testing level connection")
    connection_added = qubo.add_connection(level_idx1, level_idx2, weight=0.3)
    print(f"Connection added: {connection_added}")
    
    # Test 5: Get level variables
    print("\n5. Testing variable retrieval")
    level1_vars = qubo.get_level_variables(level_idx1)
    print(f"Level 1 variables: {level1_vars}")
    assert level1_vars == variables1
    
    # Test 6: Get level constraints
    print("\n6. Testing constraint retrieval")
    level1_constraints = qubo.get_level_constraints(level_idx1)
    print(f"Level 1 constraints: {level1_constraints}")
    assert level1_constraints == constraints1
    
    # Test 7: Optimize
    print("\n7. Testing optimization")
    results = qubo.optimize()
    print("Optimization results:")
    for level_name, solution in results.items():
        print(f"{level_name}: {solution}")
    assert len(results) == 2  # Should have solutions for both levels
    
    # Test 8: Error handling
    print("\n8. Testing error handling")
    try:
        # Try adding invalid matrix
        invalid_matrix = np.array([[1, 2]])  # Not square
        qubo.add_level(invalid_matrix)
        print("❌ Should have raised ValueError for non-square matrix")
    except ValueError as e:
        print(f"✅ Correctly caught error: {e}")
        
    try:
        # Try adding invalid variables
        invalid_vars = ["x1"]  # Wrong length
        qubo.add_level(matrix1, variables=invalid_vars)
        print("❌ Should have raised ValueError for mismatched variables")
    except ValueError as e:
        print(f"✅ Correctly caught error: {e}")
    
    # Test 9: Default variable names
    print("\n9. Testing default variable names")
    matrix3 = np.array([[1, 0], [0, 1]])
    level_idx3 = qubo.add_level(qubo_matrix=matrix3)  # No variables provided
    vars3 = qubo.get_level_variables(level_idx3)
    print(f"Default variable names: {vars3}")
    assert len(vars3) == matrix3.shape[0]
    
    # Test 10: Optimization parameters
    print("\n10. Testing optimization parameters")
    original_params = qubo.optimization_parameters.copy()
    qubo.optimization_parameters['inter_level_weight'] = 0.8
    results_new = qubo.optimize()
    print(f"Results with modified parameters: {len(results_new)} levels")
    
    # Reset parameters
    qubo.optimization_parameters = original_params

if __name__ == "__main__":
    try:
        test_hierarchical_qubo()
        print("\n✅ All hierarchical QUBO tests completed successfully")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")