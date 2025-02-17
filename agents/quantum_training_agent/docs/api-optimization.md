# Optimization API

This document details the optimization API for the Quantum Training Agent, including interfaces for quantum optimization and solver integration.

## Optimization Classes

### 1. Quantum Optimizer

```python
class QuantumOptimizer:
    """Main interface for quantum optimization."""
    
    def __init__(
        self,
        workspace: str,
        solver: str = "parallel-tempering",
        **kwargs
    ):
        """
        Initialize quantum optimizer.
        
        Args:
            workspace: Azure Quantum workspace
            solver: Quantum solver type
            **kwargs: Additional solver parameters
        """
        self.workspace = workspace
        self.solver = solver
        self.setup_solver()
    
    def optimize(
        self,
        problem: OptimizationProblem,
        timeout: int = 300
    ) -> OptimizationResult:
        """
        Solve optimization problem using quantum resources.
        
        Args:
            problem: Problem to optimize
            timeout: Maximum solving time in seconds
            
        Returns:
            Optimization results
        """
        qubo = self.formulate_qubo(problem)
        solution = self.solve_qubo(qubo, timeout)
        return self.process_solution(solution)
    
    def solve_qubo(
        self,
        qubo: Dict[Tuple[int, int], float],
        timeout: int
    ) -> Dict[int, int]:
        """
        Solve QUBO problem using quantum solver.
        
        Args:
            qubo: QUBO problem coefficients
            timeout: Maximum solving time
            
        Returns:
            Binary solution vector
        """
        job = self.submit_job(qubo)
        return self.wait_for_results(job, timeout)
```

### 2. Problem Formulation

```python
class ProblemFormulator:
    """Handles conversion of optimization problems to QUBO format."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize problem formulator.
        
        Args:
            max_size: Maximum problem size
        """
        self.max_size = max_size
        
    def formulate_qubo(
        self,
        problem: OptimizationProblem
    ) -> Dict[Tuple[int, int], float]:
        """
        Convert optimization problem to QUBO format.
        
        Args:
            problem: Problem to convert
            
        Returns:
            QUBO coefficients
        """
        variables = self.encode_variables(problem)
        objective = self.encode_objective(problem, variables)
        constraints = self.encode_constraints(problem, variables)
        return self.combine_terms(objective, constraints)
    
    def encode_variables(
        self,
        problem: OptimizationProblem
    ) -> Dict[str, List[int]]:
        """
        Encode problem variables as binary variables.
        
        Args:
            problem: Problem containing variables
            
        Returns:
            Mapping of variables to binary indices
        """
        return {
            var: self.binary_encoding(val, bits)
            for var, (val, bits) in problem.variables.items()
        }
```

### 3. Solver Integration

```python
class QuantumSolver:
    """Interface for quantum solver integration."""
    
    def __init__(
        self,
        workspace: AzureQuantumWorkspace,
        solver_type: str = "parallel-tempering"
    ):
        """
        Initialize quantum solver.
        
        Args:
            workspace: Azure Quantum workspace
            solver_type: Type of quantum solver
        """
        self.workspace = workspace
        self.solver = self.get_solver(solver_type)
        
    def submit_job(
        self,
        problem: Dict[Tuple[int, int], float],
        params: dict = None
    ) -> QuantumJob:
        """
        Submit job to quantum solver.
        
        Args:
            problem: QUBO problem
            params: Solver parameters
            
        Returns:
            Quantum job handle
        """
        job = self.solver.submit(
            problem,
            **(params or {})
        )
        return job
    
    def get_results(
        self,
        job: QuantumJob,
        timeout: int = 300
    ) -> QuantumResult:
        """
        Get results from quantum job.
        
        Args:
            job: Quantum job handle
            timeout: Maximum wait time
            
        Returns:
            Job results
        """
        return job.get_results(timeout=timeout)
```

## Optimization Utilities

### 1. QUBO Utilities

```python
class QUBOUtils:
    """Utilities for QUBO problem handling."""
    
    @staticmethod
    def validate_qubo(
        qubo: Dict[Tuple[int, int], float]
    ) -> bool:
        """
        Validate QUBO problem format.
        
        Args:
            qubo: QUBO problem to validate
            
        Returns:
            True if valid
        """
        return all(
            isinstance(k, tuple) and
            len(k) == 2 and
            isinstance(v, (int, float))
            for k, v in qubo.items()
        )
    
    @staticmethod
    def compress_qubo(
        qubo: Dict[Tuple[int, int], float],
        tolerance: float = 1e-10
    ) -> Dict[Tuple[int, int], float]:
        """
        Remove near-zero terms from QUBO.
        
        Args:
            qubo: QUBO to compress
            tolerance: Minimum magnitude
            
        Returns:
            Compressed QUBO
        """
        return {
            k: v for k, v in qubo.items()
            if abs(v) > tolerance
        }
```

### 2. Result Processing

```python
class ResultProcessor:
    """Processes and analyzes optimization results."""
    
    def __init__(self):
        """Initialize result processor."""
        self.metrics = {}
        
    def process_result(
        self,
        result: QuantumResult
    ) -> OptimizationResult:
        """
        Process quantum optimization results.
        
        Args:
            result: Raw quantum results
            
        Returns:
            Processed optimization results
        """
        solution = self.extract_solution(result)
        energy = self.compute_energy(solution)
        metrics = self.compute_metrics(result)
        return OptimizationResult(
            solution=solution,
            energy=energy,
            metrics=metrics
        )
```

## Usage Examples

### 1. Basic Optimization

```python
# Initialize optimizer
optimizer = QuantumOptimizer(
    workspace="azure-quantum",
    solver="parallel-tempering"
)

# Solve problem
problem = OptimizationProblem(...)
result = optimizer.optimize(problem)
```

### 2. Custom Problem Formulation

```python
# Custom QUBO formulation
formulator = ProblemFormulator()
qubo = formulator.formulate_qubo(problem)

# Solve with specific parameters
solver = QuantumSolver(workspace)
job = solver.submit_job(
    qubo,
    params={
        "timeout": 600,
        "max_iterations": 1000
    }
)
```

## Related Documentation
- [Configuration API](api-configuration.md)
- [Training API](api-training.md)
- [Evaluation API](api-evaluation.md)