from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass

@dataclass
class QUBOLevel:
    """Represents a level in the hierarchical QUBO structure."""
    matrix: np.ndarray
    variables: List[str]
    constraints: Dict[str, float]
    weight: float = 1.0

class HierarchicalQUBO:
    """Multi-level QUBO for large-scale problems."""
    
    def __init__(self):
        self.levels: List[QUBOLevel] = []
        self.connections: List[Tuple[int, int, float]] = []  # (level1, level2, weight)
        self.optimization_parameters: Dict[str, float] = {
            'inter_level_weight': 0.5,
            'constraint_weight': 10.0,  # Increased weight for constraints
            'convergence_threshold': 1e-6,
            'max_iterations': 1000
        }
        
    def add_level(self, qubo_matrix: np.ndarray,
                  variables: Optional[List[str]] = None,
                  constraints: Optional[Dict[str, float]] = None,
                  weight: float = 1.0) -> int:
        """
        Add a new hierarchical level.
        
        Args:
            qubo_matrix: QUBO matrix for this level
            variables: Optional list of variable names
            constraints: Optional dictionary of constraints
            weight: Weight for this level's contribution
            
        Returns:
            int: Index of the new level
        """
        if not isinstance(qubo_matrix, np.ndarray):
            raise ValueError("QUBO matrix must be a numpy array")
            
        if qubo_matrix.shape[0] != qubo_matrix.shape[1]:
            raise ValueError("QUBO matrix must be square")
            
        # Generate default variable names if not provided
        if variables is None:
            variables = [f"x{i}" for i in range(qubo_matrix.shape[0])]
            
        if len(variables) != qubo_matrix.shape[0]:
            raise ValueError("Number of variables must match matrix dimensions")
            
        # Initialize empty constraints if not provided
        if constraints is None:
            constraints = {}
            
        level = QUBOLevel(
            matrix=qubo_matrix,
            variables=variables,
            constraints=constraints,
            weight=weight
        )
        
        self.levels.append(level)
        return len(self.levels) - 1
        
    def add_connection(self, level1_idx: int, level2_idx: int,
                      weight: float) -> bool:
        """
        Add connection between hierarchical levels.
        
        Args:
            level1_idx: Index of first level
            level2_idx: Index of second level
            weight: Connection weight
            
        Returns:
            bool: Success status
        """
        if not (0 <= level1_idx < len(self.levels) and 
                0 <= level2_idx < len(self.levels)):
            return False
            
        connection = (level1_idx, level2_idx, weight)
        if connection not in self.connections:
            self.connections.append(connection)
            return True
            
        return False
        
    def optimize(self) -> Dict[str, np.ndarray]:
        """
        Perform hierarchical optimization.
        
        Returns:
            Dict[str, np.ndarray]: Solutions for each level
        """
        if not self.levels:
            return {}
            
        # Build combined QUBO matrix
        combined_size = sum(level.matrix.shape[0] for level in self.levels)
        combined_matrix = np.zeros((combined_size, combined_size))
        
        # Fill in level matrices
        offset = 0
        for level in self.levels:
            size = level.matrix.shape[0]
            combined_matrix[offset:offset+size, offset:offset+size] = level.matrix * level.weight
            offset += size
            
        # Add inter-level connections
        offset_map = self._calculate_offsets()
        for level1_idx, level2_idx, weight in self.connections:
            self._add_connection_terms(
                combined_matrix,
                offset_map,
                level1_idx,
                level2_idx,
                weight
            )
            
        # Add constraint terms
        self._add_constraint_terms(combined_matrix, offset_map)
        
        # Solve combined QUBO
        solution = self._solve_qubo(combined_matrix, offset_map)
        
        # Extract solutions for each level
        results = {}
        offset = 0
        for i, level in enumerate(self.levels):
            size = level.matrix.shape[0]
            level_solution = solution[offset:offset+size]
            results[f"level_{i}"] = level_solution
            offset += size
            
        return results
        
    def _calculate_offsets(self) -> Dict[int, int]:
        """Calculate matrix offsets for each level."""
        offsets = {}
        current_offset = 0
        for i, level in enumerate(self.levels):
            offsets[i] = current_offset
            current_offset += level.matrix.shape[0]
        return offsets
        
    def _add_connection_terms(self, combined_matrix: np.ndarray,
                            offset_map: Dict[int, int],
                            level1_idx: int,
                            level2_idx: int,
                            weight: float) -> None:
        """Add inter-level connection terms to combined matrix."""
        level1 = self.levels[level1_idx]
        level2 = self.levels[level2_idx]
        
        offset1 = offset_map[level1_idx]
        offset2 = offset_map[level2_idx]
        
        # Add coupling terms with adjusted weight
        coupling_weight = weight * self.optimization_parameters['inter_level_weight']
        
        for i in range(level1.matrix.shape[0]):
            for j in range(level2.matrix.shape[0]):
                combined_matrix[offset1 + i, offset2 + j] = coupling_weight
                combined_matrix[offset2 + j, offset1 + i] = coupling_weight
                
    def _add_constraint_terms(self, combined_matrix: np.ndarray,
                            offset_map: Dict[int, int]) -> None:
        """Add constraint terms to combined matrix."""
        constraint_weight = self.optimization_parameters['constraint_weight']
        
        for level_idx, level in enumerate(self.levels):
            offset = offset_map[level_idx]
            
            for var_idx, var_name in enumerate(level.variables):
                if var_name in level.constraints:
                    target_value = level.constraints[var_name]
                    # Add quadratic constraint term (x - target)^2
                    combined_matrix[offset + var_idx, offset + var_idx] += constraint_weight * 2
                    # Add linear term -2*target*x
                    combined_matrix[offset + var_idx, offset + var_idx] -= constraint_weight * 2 * target_value
                    
    def _solve_qubo(self, matrix: np.ndarray, offset_map: Dict[int, int]) -> np.ndarray:
        """
        Solve QUBO problem using classical optimization.
        
        This is a simplified solver - in practice, you would use
        quantum hardware or more sophisticated classical methods.
        """
        size = matrix.shape[0]
        
        # Initialize solution with constraints
        solution = np.zeros(size)
        for level_idx, level in enumerate(self.levels):
            offset = offset_map[level_idx]
            for var_idx, var_name in enumerate(level.variables):
                if var_name in level.constraints:
                    solution[offset + var_idx] = level.constraints[var_name]
                else:
                    solution[offset + var_idx] = np.random.randint(0, 2)
                    
        energy = solution @ matrix @ solution
        
        # Simple greedy optimization
        for _ in range(self.optimization_parameters['max_iterations']):
            improved = False
            for level_idx, level in enumerate(self.levels):
                offset = offset_map[level_idx]
                for var_idx, var_name in enumerate(level.variables):
                    if var_name not in level.constraints:  # Only flip unconstrained variables
                        # Try flipping
                        solution[offset + var_idx] = 1 - solution[offset + var_idx]
                        new_energy = solution @ matrix @ solution
                        
                        if new_energy < energy:
                            energy = new_energy
                            improved = True
                        else:
                            # Revert flip if no improvement
                            solution[offset + var_idx] = 1 - solution[offset + var_idx]
                            
            if not improved:
                break
                
        return solution
        
    def get_level_variables(self, level_idx: int) -> Optional[List[str]]:
        """Get variable names for a specific level."""
        if 0 <= level_idx < len(self.levels):
            return self.levels[level_idx].variables.copy()
        return None
        
    def get_level_constraints(self, level_idx: int) -> Optional[Dict[str, float]]:
        """Get constraints for a specific level."""
        if 0 <= level_idx < len(self.levels):
            return self.levels[level_idx].constraints.copy()
        return None