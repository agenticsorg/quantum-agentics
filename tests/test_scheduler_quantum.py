import pytest
import numpy as np
from qam.scheduler import QUBOScheduler, QUBOTerm
from qam.quantum_reasoning import QuantumReasoningState

def test_qubo_term_creation():
    """Test basic QUBO term creation."""
    term = QUBOTerm(0, 1, 1.0)
    assert term.i == 0
    assert term.j == 1
    assert term.weight == 1.0

def test_build_qubo_with_reasoning():
    """Test QUBO problem construction with quantum reasoning."""
    scheduler = QUBOScheduler()
    state = QuantumReasoningState()
    
    # Build small QUBO problem
    terms = scheduler.build_qubo_with_reasoning(2, state)
    
    assert len(terms) > 0
    assert all(isinstance(term, QUBOTerm) for term in terms)

def test_prepare_quantum_problem():
    """Test conversion of QUBO terms to Azure Quantum format."""
    scheduler = QUBOScheduler()
    terms = [
        QUBOTerm(0, 0, 1.0),
        QUBOTerm(0, 1, -2.0)
    ]
    
    problem = scheduler._prepare_quantum_problem(terms)
    
    assert problem["type"] == "optimization"
    assert problem["format"] == "microsoft.qio.v2"
    assert problem["problem"]["problem_type"] == "pubo"
    assert len(problem["problem"]["terms"]) == 2
    
    # Check single variable term
    assert problem["problem"]["terms"][0]["ids"] == [0]
    assert problem["problem"]["terms"][0]["c"] == 1.0
    
    # Check interaction term
    assert problem["problem"]["terms"][1]["ids"] == [0, 1]
    assert problem["problem"]["terms"][1]["c"] == -2.0

def test_quantum_solving():
    """Test quantum solving with Azure Quantum."""
    scheduler = QUBOScheduler()
    terms = [
        QUBOTerm(0, 0, 1.0),
        QUBOTerm(1, 1, 1.0),
        QUBOTerm(0, 1, -2.0)
    ]
    
    # Try quantum solving
    solution = scheduler._solve_quantum(terms, 2)
    
    assert isinstance(solution, np.ndarray)
    assert solution.shape == (2,)
    assert all(x in [0, 1] for x in solution)

def test_classical_fallback():
    """Test classical solving fallback."""
    scheduler = QUBOScheduler()
    terms = [
        QUBOTerm(0, 0, 1.0),
        QUBOTerm(1, 1, 1.0),
        QUBOTerm(0, 1, -2.0)
    ]
    
    # Force classical solving
    solution = scheduler._solve_classical(terms, 2)
    
    assert isinstance(solution, np.ndarray)
    assert solution.shape == (2,)
    assert all(x in [0, 1] for x in solution)

def test_energy_calculation():
    """Test energy calculation for solutions."""
    scheduler = QUBOScheduler()
    terms = [
        QUBOTerm(0, 0, 1.0),
        QUBOTerm(1, 1, 1.0),
        QUBOTerm(0, 1, -2.0)
    ]
    
    # Test known configuration
    solution = np.array([1, 1])
    energy = scheduler._calculate_energy(solution, terms)
    
    # For this problem, energy should be 0.0 when both qubits are 1
    # (1.0 * 1 + 1.0 * 1 + -2.0 * 1 * 1 = 0)
    assert np.isclose(energy, 0.0)

def test_end_to_end_scheduling():
    """Test complete scheduling workflow with quantum solving."""
    scheduler = QUBOScheduler()
    state = QuantumReasoningState()
    
    # Build and solve small scheduling problem
    terms = scheduler.build_qubo_with_reasoning(2, state)
    solution = scheduler._solve_quantum(terms, 2)
    
    assert isinstance(solution, np.ndarray)
    assert solution.shape == (2,)
    assert all(x in [0, 1] for x in solution)
    
    # Verify energy is reasonable
    energy = scheduler._calculate_energy(solution, terms)
    assert isinstance(energy, float)
    assert not np.isnan(energy)