"""
Tests for the scheduler module.
"""
import pytest
from qam.scheduler import Task, Agent, QUBOScheduler, QUBOTerm

def test_task_creation():
    """Test basic task creation."""
    task = Task(id="task1", duration=3)
    assert task.id == "task1"
    assert task.duration == 3
    assert task.release_time == 0
    assert task.deadline is None

def test_agent_creation():
    """Test basic agent creation."""
    agent = Agent(id="agent1", capabilities=["compute", "io"])
    assert agent.id == "agent1"
    assert "compute" in agent.capabilities
    assert "io" in agent.capabilities

def test_scheduler_initialization():
    """Test scheduler initialization."""
    scheduler = QUBOScheduler()
    assert len(scheduler.tasks) == 0
    assert len(scheduler.agents) == 0
    assert len(scheduler._variable_map) == 0
    assert len(scheduler._reverse_map) == 0
    assert scheduler._next_var_index == 0

def test_add_task_and_agent():
    """Test adding tasks and agents to scheduler."""
    scheduler = QUBOScheduler()
    task = Task(id="task1", duration=3)
    agent = Agent(id="agent1")
    
    scheduler.add_task(task)
    scheduler.add_agent(agent)
    
    assert len(scheduler.tasks) == 1
    assert len(scheduler.agents) == 1
    assert scheduler.tasks[0].id == "task1"
    assert scheduler.agents[0].id == "agent1"

def test_variable_mapping():
    """Test QUBO variable mapping creation."""
    scheduler = QUBOScheduler()
    
    # Add a task and agent
    task = Task(id="task1", duration=2)
    agent = Agent(id="agent1")
    scheduler.add_task(task)
    scheduler.add_agent(agent)
    
    # Create variable mapping with horizon=5
    scheduler._create_variable_mapping(horizon=5)
    
    # Should have variables for t=0,1,2,3 (can't start at 4 with duration=2)
    assert len(scheduler._variable_map) == 4
    
    # Test variable index retrieval
    assert scheduler.get_variable_index("task1", "agent1", 0) is not None
    assert scheduler.get_variable_index("task1", "agent1", 3) is not None
    assert scheduler.get_variable_index("task1", "agent1", 4) is None  # Invalid due to duration

def test_task_assignment_constraints():
    """Test QUBO terms for task assignment constraints."""
    scheduler = QUBOScheduler()
    
    task = Task(id="task1", duration=1)
    agent1 = Agent(id="agent1")
    agent2 = Agent(id="agent2")
    
    scheduler.add_task(task)
    scheduler.add_agent(agent1)
    scheduler.add_agent(agent2)
    
    scheduler._create_variable_mapping(horizon=2)
    terms = scheduler._build_task_assignment_constraints()
    
    # For one task with two possible start times (0,1) and two agents
    # We should have terms ensuring exactly one assignment
    assert len(terms) > 0
    
    # Verify we have both linear and quadratic terms
    linear_terms = [term for term in terms if len(term.indices) == 1]
    quadratic_terms = [term for term in terms if len(term.indices) == 2]
    
    assert len(linear_terms) > 0
    assert len(quadratic_terms) > 0

def test_agent_overlap_constraints():
    """Test QUBO terms for agent overlap constraints."""
    scheduler = QUBOScheduler()
    
    task1 = Task(id="task1", duration=2)
    task2 = Task(id="task2", duration=2)
    agent = Agent(id="agent1")
    
    scheduler.add_task(task1)
    scheduler.add_task(task2)
    scheduler.add_agent(agent)
    
    scheduler._create_variable_mapping(horizon=3)
    terms = scheduler._build_agent_overlap_constraints()
    
    # Should have terms preventing overlapping assignments
    assert len(terms) > 0
    # All terms should be quadratic (between pairs of variables)
    assert all(len(term.indices) == 2 for term in terms)

def test_makespan_objective():
    """Test QUBO terms for makespan minimization."""
    scheduler = QUBOScheduler()
    
    task = Task(id="task1", duration=2)
    agent = Agent(id="agent1")
    
    scheduler.add_task(task)
    scheduler.add_agent(agent)
    
    scheduler._create_variable_mapping(horizon=3)
    terms = scheduler._build_makespan_objective(weight=1.0)
    
    # Should have terms for each possible start time
    assert len(terms) > 0
    # All terms should be linear (single variable)
    assert all(len(term.indices) == 1 for term in terms)
    # Later start times should have higher coefficients
    start_time_0 = next(term for term in terms if scheduler.decode_variable_index(term.indices[0])[2] == 0)
    start_time_1 = next(term for term in terms if scheduler.decode_variable_index(term.indices[0])[2] == 1)
    assert start_time_1.coefficient > start_time_0.coefficient

def test_complete_qubo_formulation():
    """Test complete QUBO problem formulation."""
    scheduler = QUBOScheduler()
    
    task1 = Task(id="task1", duration=1)
    task2 = Task(id="task2", duration=1)
    agent1 = Agent(id="agent1")
    agent2 = Agent(id="agent2")
    
    scheduler.add_task(task1)
    scheduler.add_task(task2)
    scheduler.add_agent(agent1)
    scheduler.add_agent(agent2)
    
    terms = scheduler.build_qubo(horizon=3, makespan_weight=1.0)
    
    # Verify we have all types of terms
    assert len(terms) > 0
    linear_terms = [term for term in terms if len(term.indices) == 1]
    quadratic_terms = [term for term in terms if len(term.indices) == 2]
    assert len(linear_terms) > 0
    assert len(quadratic_terms) > 0

def test_azure_qubo_format():
    """Test formatting QUBO for Azure Quantum submission."""
    scheduler = QUBOScheduler()
    
    task = Task(id="task1", duration=1)
    agent = Agent(id="agent1")
    
    scheduler.add_task(task)
    scheduler.add_agent(agent)
    
    terms = scheduler.build_qubo(horizon=2)
    azure_qubo = scheduler.format_qubo_for_azure(terms)
    
    assert "problem_type" in azure_qubo
    assert azure_qubo["problem_type"] == "qubo"
    assert "terms" in azure_qubo
    assert isinstance(azure_qubo["terms"], list)
    assert all("c" in term and "ids" in term for term in azure_qubo["terms"])