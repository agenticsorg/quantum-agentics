"""
Tests for the scheduler module.
"""
import pytest
from qam.scheduler import Task, Agent, QUBOScheduler, QUBOTerm, TimeWindow

def test_time_window():
    """Test TimeWindow functionality."""
    window = TimeWindow(start=1, end=4)
    
    # Test contains
    assert 1 in window
    assert 2 in window
    assert 3 in window
    assert 4 not in window
    assert 0 not in window
    
    # Test overlaps
    window2 = TimeWindow(start=3, end=6)
    assert window.overlaps(window2)
    assert window2.overlaps(window)
    
    window3 = TimeWindow(start=4, end=7)
    assert not window.overlaps(window3)
    
    # Test duration
    assert window.duration() == 3

def test_task_time_windows():
    """Test task time window generation."""
    task = Task(id="task1", duration=2)
    
    # Test with default window size (task duration)
    windows = task.get_time_windows(horizon=5)
    assert len(windows) == 4  # Can start at t=0,1,2,3
    assert all(w.duration() == 2 for w in windows)
    
    # Test with custom window size
    windows = task.get_time_windows(horizon=5, window_size=3)
    assert len(windows) == 2  # Two windows: [0-3) and [3-5)
    
    # Test with release time
    task = Task(id="task2", duration=2, release_time=2)
    windows = task.get_time_windows(horizon=5)
    assert len(windows) == 2  # Can start at t=2,3
    assert all(w.start >= 2 for w in windows)
    
    # Test with deadline
    task = Task(id="task3", duration=2, deadline=4)
    windows = task.get_time_windows(horizon=5)
    assert len(windows) == 3  # Can start at t=0,1,2
    assert all(w.end <= 4 for w in windows)

def test_window_size_optimization():
    """Test window size optimization logic."""
    scheduler = QUBOScheduler()
    
    # Test with single task
    task1 = Task(id="task1", duration=4)
    scheduler.add_task(task1)
    scheduler._create_variable_mapping(horizon=8)
    assert scheduler._window_size == 4
    
    # Test with multiple tasks having GCD
    scheduler = QUBOScheduler()
    task1 = Task(id="task1", duration=4)
    task2 = Task(id="task2", duration=6)
    scheduler.add_task(task1)
    scheduler.add_task(task2)
    scheduler._create_variable_mapping(horizon=12)
    assert scheduler._window_size == 2  # GCD of 4 and 6
    
    # Test with coprime durations
    scheduler = QUBOScheduler()
    task1 = Task(id="task1", duration=3)
    task2 = Task(id="task2", duration=4)
    scheduler.add_task(task1)
    scheduler.add_task(task2)
    scheduler._create_variable_mapping(horizon=12)
    assert scheduler._window_size == 1  # GCD is 1

def test_variable_mapping_with_windows():
    """Test QUBO variable mapping creation with time windows."""
    scheduler = QUBOScheduler()
    
    # Add tasks with different durations
    task1 = Task(id="task1", duration=2)
    task2 = Task(id="task2", duration=4)
    agent = Agent(id="agent1")
    
    scheduler.add_task(task1)
    scheduler.add_task(task2)
    scheduler.add_agent(agent)
    
    scheduler._create_variable_mapping(horizon=6)
    
    # Check variable creation
    # For task1 (duration=2): Can start at t=0,2,4
    # For task2 (duration=4): Can start at t=0,2
    expected_vars = 5  # 3 windows for task1 + 2 windows for task2
    assert len(scheduler._variable_map) == expected_vars
    
    # Test variable index retrieval
    assert scheduler.get_variable_index("task1", "agent1", 0) is not None
    assert scheduler.get_variable_index("task1", "agent1", 1) is not None
    assert scheduler.get_variable_index("task2", "agent1", 0) is not None
    assert scheduler.get_variable_index("task2", "agent1", 5) is None  # Invalid due to horizon

def test_task_assignment_constraints_with_windows():
    """Test QUBO terms for task assignment constraints with time windows."""
    scheduler = QUBOScheduler()
    
    task = Task(id="task1", duration=2)
    agent1 = Agent(id="agent1")
    agent2 = Agent(id="agent2")
    
    scheduler.add_task(task)
    scheduler.add_agent(agent1)
    scheduler.add_agent(agent2)
    
    scheduler._create_variable_mapping(horizon=4)
    terms = scheduler._build_task_assignment_constraints()
    
    # Verify we have both linear and quadratic terms
    linear_terms = [term for term in terms if len(term.indices) == 1]
    quadratic_terms = [term for term in terms if len(term.indices) == 2]
    
    assert len(linear_terms) > 0
    assert len(quadratic_terms) > 0
    
    # Each task should be assigned exactly once
    task_vars = set()
    for key, idx in scheduler._variable_map.items():
        if key[0] == "task1":
            task_vars.add(idx)
    
    # Should have one negative linear term per variable
    assert len([t for t in linear_terms if t.coefficient < 0]) == len(task_vars)

def test_agent_overlap_constraints_with_windows():
    """Test QUBO terms for agent overlap constraints with time windows."""
    scheduler = QUBOScheduler()
    
    task1 = Task(id="task1", duration=2)
    task2 = Task(id="task2", duration=2)
    agent = Agent(id="agent1")
    
    scheduler.add_task(task1)
    scheduler.add_task(task2)
    scheduler.add_agent(agent)
    
    scheduler._create_variable_mapping(horizon=4)
    terms = scheduler._build_agent_overlap_constraints()
    
    # Should have terms preventing overlapping assignments
    assert len(terms) > 0
    # All terms should be quadratic (between pairs of variables)
    assert all(len(term.indices) == 2 for term in terms)
    
    # Verify overlapping windows have penalty terms
    overlapping_count = 0
    for key1, idx1 in scheduler._variable_map.items():
        for key2, idx2 in scheduler._variable_map.items():
            if (key1[1] == key2[1] == agent.id and  # Same agent
                key1 != key2 and  # Different assignments
                key1[2].overlaps(key2[2])):  # Overlapping windows
                overlapping_count += 1
    
    # Each overlapping pair should have a penalty term
    assert len(terms) == overlapping_count // 2  # Divide by 2 as each pair is counted twice

def test_makespan_objective_with_windows():
    """Test QUBO terms for makespan minimization with time windows."""
    scheduler = QUBOScheduler()
    
    task = Task(id="task1", duration=2)
    agent = Agent(id="agent1")
    
    scheduler.add_task(task)
    scheduler.add_agent(agent)
    
    scheduler._create_variable_mapping(horizon=4)
    terms = scheduler._build_makespan_objective(weight=1.0)
    
    # Should have terms for each possible window
    assert len(terms) > 0
    # All terms should be linear (single variable)
    assert all(len(term.indices) == 1 for term in terms)
    
    # Later windows should have higher coefficients
    windows = []
    for key, idx in scheduler._variable_map.items():
        if key[0] == task.id and key[1] == agent.id:
            windows.append((key[2].start, idx))
    windows.sort()  # Sort by start time
    
    # Get coefficients for each window
    coeffs = []
    for _, idx in windows:
        term = next(t for t in terms if t.indices[0] == idx)
        coeffs.append(term.coefficient)
    
    # Verify coefficients increase with later windows
    assert all(coeffs[i] < coeffs[i+1] for i in range(len(coeffs)-1))

def test_complete_qubo_formulation_with_windows():
    """Test complete QUBO problem formulation with time windows."""
    scheduler = QUBOScheduler()
    
    task1 = Task(id="task1", duration=2)
    task2 = Task(id="task2", duration=3)
    agent1 = Agent(id="agent1")
    agent2 = Agent(id="agent2")
    
    scheduler.add_task(task1)
    scheduler.add_task(task2)
    scheduler.add_agent(agent1)
    scheduler.add_agent(agent2)
    
    terms = scheduler.build_qubo(horizon=6, makespan_weight=1.0)
    
    # Verify we have all types of terms
    assert len(terms) > 0
    linear_terms = [term for term in terms if len(term.indices) == 1]
    quadratic_terms = [term for term in terms if len(term.indices) == 2]
    assert len(linear_terms) > 0
    assert len(quadratic_terms) > 0

def test_azure_qubo_format_with_windows():
    """Test formatting QUBO with time windows for Azure Quantum submission."""
    scheduler = QUBOScheduler()
    
    task = Task(id="task1", duration=2)
    agent = Agent(id="agent1")
    
    scheduler.add_task(task)
    scheduler.add_agent(agent)
    
    terms = scheduler.build_qubo(horizon=4)
    azure_qubo = scheduler.format_qubo_for_azure(terms)
    
    assert "problem_type" in azure_qubo
    assert azure_qubo["problem_type"] == "qubo"
    assert "terms" in azure_qubo
    assert isinstance(azure_qubo["terms"], list)
    assert all("c" in term and "ids" in term for term in azure_qubo["terms"])