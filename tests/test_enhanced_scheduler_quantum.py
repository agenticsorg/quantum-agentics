import pytest
import numpy as np
from qam.enhanced_scheduler import EnhancedQUBOScheduler
from qam.quantum_reasoning import QuantumReasoningState

def test_enhanced_scheduler_initialization():
    """Test enhanced scheduler initialization."""
    scheduler = EnhancedQUBOScheduler()
    assert isinstance(scheduler.hierarchical_levels, list)
    assert isinstance(scheduler.cluster_assignments, dict)
    assert scheduler.max_parallel_jobs > 0

def test_build_hierarchical_qubo():
    """Test building hierarchical QUBO structure."""
    scheduler = EnhancedQUBOScheduler()
    
    # Create test tasks
    tasks = [
        {"id": "task1", "dependencies": []},
        {"id": "task2", "dependencies": ["task1"]},
        {"id": "task3", "dependencies": []}
    ]
    
    # Create test clusters
    clusters = {
        "cluster1": {"size": 2},
        "cluster2": {"size": 1}
    }
    
    # Build hierarchical QUBO
    levels = scheduler.build_hierarchical_qubo(tasks, clusters, max_cluster_size=2)
    
    assert isinstance(levels, list)
    assert all(isinstance(level, np.ndarray) for level in levels)
    assert all(level.shape[0] == level.shape[1] for level in levels)

def test_cluster_qubo_processing():
    """Test QUBO processing for a single cluster."""
    scheduler = EnhancedQUBOScheduler()
    
    # Test tasks for one cluster
    tasks = [
        {"id": "task1", "dependencies": []},
        {"id": "task2", "dependencies": ["task1"]}
    ]
    
    # Process cluster QUBO
    result = scheduler._build_and_solve_cluster_qubo(tasks, horizon=2)
    
    assert isinstance(result, np.ndarray)
    assert result.shape == (2, 2)
    assert np.all(result >= 0)  # Weights should be non-negative

def test_decision_path_generation():
    """Test generation of quantum decision paths."""
    scheduler = EnhancedQUBOScheduler()
    state = QuantumReasoningState()
    
    # Test tasks
    tasks = [
        {"id": "task1", "dependencies": []},
        {"id": "task2", "dependencies": ["task1"]}
    ]
    
    # Add decision paths
    scheduler._add_cluster_decision_paths(state, tasks)
    
    # Verify state has paths
    assert len(state.amplitudes) > 0
    
    # Verify probabilities sum to approximately 1
    total_prob = sum(abs(amp) ** 2 for amp in state.amplitudes.values())
    assert np.isclose(total_prob, 1.0, atol=1e-10)

def test_parallel_optimization():
    """Test parallel quantum optimization."""
    scheduler = EnhancedQUBOScheduler()
    
    # Create larger set of tasks
    tasks = [
        {"id": f"task{i}", "dependencies": []} for i in range(6)
    ]
    tasks[1]["dependencies"] = ["task0"]
    tasks[3]["dependencies"] = ["task2"]
    tasks[5]["dependencies"] = ["task4"]
    
    # Create clusters
    clusters = {
        "cluster1": {"size": 3},
        "cluster2": {"size": 3}
    }
    
    # Test parallel optimization
    levels = scheduler.build_hierarchical_qubo(tasks, clusters, max_cluster_size=3)
    
    assert isinstance(levels, list)
    assert len(levels) > 0
    assert all(isinstance(level, np.ndarray) for level in levels)

def test_enhanced_schedule_optimization():
    """Test complete schedule optimization with quantum solving."""
    scheduler = EnhancedQUBOScheduler()
    state = QuantumReasoningState()
    
    # Create test tasks
    tasks = [
        {"id": "task1", "dependencies": []},
        {"id": "task2", "dependencies": ["task1"]},
        {"id": "task3", "dependencies": []}
    ]
    
    # Optimize schedule
    result = scheduler.optimize_schedule_with_reasoning(tasks, horizon=3, reasoning_state=state)
    
    assert isinstance(result, dict)
    assert "schedule" in result
    assert "objective_value" in result
    assert isinstance(result["schedule"], dict)
    assert isinstance(result["objective_value"], float)

def test_error_handling():
    """Test error handling in quantum operations."""
    scheduler = EnhancedQUBOScheduler()
    
    # Test with invalid tasks
    invalid_tasks = [
        {"id": "task1"},  # Missing dependencies
        {"invalid": "task2"}  # Invalid format
    ]
    
    # Should not raise exception but return empty result
    levels = scheduler.build_hierarchical_qubo(invalid_tasks, {}, max_cluster_size=2)
    assert isinstance(levels, list)
    
    # Test with invalid horizon
    state = QuantumReasoningState()
    result = scheduler.optimize_schedule_with_reasoning(invalid_tasks, horizon=0, reasoning_state=state)
    assert isinstance(result, dict)
    assert result.get("schedule", {}) == {}