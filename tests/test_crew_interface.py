"""
Tests for CrewAI integration.
"""
import pytest
from unittest.mock import Mock, patch
from qam.crew_interface import (
    AgentConfig,
    TaskConfig,
    QAMManagerAgent,
    Process
)
from qam.azure_quantum import AzureQuantumConfig
from qam.scheduler import QUBOScheduler

@pytest.fixture
def azure_config():
    """Fixture for Azure Quantum configuration."""
    return AzureQuantumConfig(
        resource_group="test-group",
        workspace_name="test-workspace",
        location="westus"
    )

@pytest.fixture
def mock_azure_client():
    """Fixture for mocked Azure Quantum client."""
    with patch('qam.crew_interface.AzureQuantumClient') as mock:
        # Mock successful job submission and result
        mock.return_value.submit_qubo.return_value = "test-job-id"
        mock.return_value.wait_for_job.return_value = {
            "solution": [0, 1, 0, 1],  # Example solution
            "cost": -2.5
        }
        yield mock

@pytest.fixture
def mock_scheduler():
    """Fixture for mocked QUBO scheduler."""
    scheduler = Mock(spec=QUBOScheduler)
    
    # Mock variable mapping
    scheduler.decode_variable_index.side_effect = [
        ("task1", "agent1", 0),  # For first 1 in solution
        ("task1", "agent1", 2)   # For second 1 in solution
    ]
    
    # Mock QUBO building
    scheduler.build_qubo.return_value = [
        {"indices": (0,), "coefficient": 1.0},
        {"indices": (0, 1), "coefficient": 2.0}
    ]
    
    # Mock Azure format conversion
    scheduler.format_qubo_for_azure.return_value = {
        "problem_type": "qubo",
        "terms": [
            {"c": 1.0, "ids": [0]},
            {"c": 2.0, "ids": [0, 1]}
        ]
    }
    
    return scheduler

def test_create_agent(azure_config, mock_azure_client, mock_scheduler):
    """Test agent creation."""
    with patch('qam.azure_quantum.subprocess.run'):  # Mock subprocess.run
        manager = QAMManagerAgent(azure_config, scheduler=mock_scheduler)
    
    config = AgentConfig(
        id="agent1",
        name="Test Agent",
        role="tester",
        goal="test things",
        backstory="professional tester",
        capabilities=["testing"]
    )
    
    agent = manager.create_agent(config)
    
    # Verify agent creation
    assert agent.name == "Test Agent"
    assert agent.role == "tester"
    assert agent.goal == "test things"
    assert agent.backstory == "professional tester"
    assert not agent.allow_delegation
    assert agent.tasks == []
    
    # Verify scheduler agent creation
    mock_scheduler.add_agent.assert_called_once()
    assert "agent1" in manager._agent_map

def test_create_task(azure_config, mock_azure_client, mock_scheduler):
    """Test task creation."""
    manager = QAMManagerAgent(azure_config, scheduler=mock_scheduler)
    
    config = TaskConfig(
        id="task1",
        name="Test Task",
        description="test something",
        duration=2,
        requirements=["testing"]
    )
    
    task = manager.create_task(config)
    
    # Verify task creation
    assert task.description == "test something"
    assert task.expected_output == "Completed task: Test Task"
    assert task.context == {
        'task_id': "task1",
        'requirements': ["testing"]
    }
    assert task.agent is None
    
    # Verify scheduler task creation
    mock_scheduler.add_task.assert_called_once()
    assert "task1" in manager._task_map

def test_optimize_schedule(azure_config, mock_azure_client, mock_scheduler):
    """Test schedule optimization."""
    manager = QAMManagerAgent(azure_config, scheduler=mock_scheduler)
    
    # Create test task and agent
    task_config = TaskConfig(
        id="task1",
        name="Test Task",
        description="test something",
        duration=2
    )
    agent_config = AgentConfig(
        id="agent1",
        name="Test Agent",
        role="tester",
        goal="test things",
        backstory="professional tester"
    )
    
    manager.create_agent(agent_config)
    manager.create_task(task_config)
    
    # Run optimization
    schedule = manager.optimize_schedule(horizon=10)
    mock_scheduler.decode_variable_index.assert_called()
    
    # Verify QUBO creation and submission
    mock_scheduler.build_qubo.assert_called_once_with(10)
    mock_scheduler.format_qubo_for_azure.assert_called_once()
    mock_azure_client.return_value.submit_qubo.assert_called_once()
    
    # Verify schedule structure
    assert "agent1" in schedule
    assert len(schedule["agent1"]) > 0
    assert all(key in schedule["agent1"][0] for key in ['task_id', 'start_time', 'duration'])

def test_setup_crew(azure_config, mock_azure_client, mock_scheduler):
    """Test crew setup."""
    manager = QAMManagerAgent(azure_config, scheduler=mock_scheduler)
    
    agents = [
        AgentConfig(
            id="agent1",
            name="Agent 1",
            role="role1",
            goal="goal1",
            backstory="backstory1"
        ),
        AgentConfig(
            id="agent2",
            name="Agent 2",
            role="role2",
            goal="goal2",
            backstory="backstory2"
        )
    ]
    
    tasks = [
        TaskConfig(
            id="task1",
            name="Task 1",
            description="desc1",
            duration=2
        ),
        TaskConfig(
            id="task2",
            name="Task 2",
            description="desc2",
            duration=3
        )
    ]
    
    manager.setup_crew(agents, tasks)
    
    # Verify crew creation
    assert manager.crew is not None
    assert len(manager.crew.agents) == 2
    assert len(manager.crew.tasks) == 2
    assert manager.crew.process == Process.sequential
    
    # Verify agent and task creation
    assert len(manager._agent_map) == 2
    assert len(manager._task_map) == 2

def test_execute_workflow(azure_config, mock_azure_client, mock_scheduler):
    """Test end-to-end execution workflow."""
    manager = QAMManagerAgent(azure_config, scheduler=mock_scheduler)
    
    # Set up a simple crew
    agents = [
        AgentConfig(
            id="agent1",
            name="Agent 1",
            role="role1",
            goal="goal1",
            backstory="backstory1"
        )
    ]
    
    tasks = [
        TaskConfig(
            id="task1",
            name="Task 1",
            description="desc1",
            duration=2
        )
    ]
    
    # Set up and execute
    manager.setup_crew(agents, tasks)
    manager.execute()
    
    # Verify optimization and execution
    mock_scheduler.build_qubo.assert_called_once()
    mock_azure_client.return_value.submit_qubo.assert_called_once()
    
    # Verify task assignment
    assert len(manager.crew.agents[0].tasks) > 0
    assert manager.crew.agents[0].tasks[0].context.get('start_time') is not None

def test_execute_without_setup(azure_config, mock_azure_client, mock_scheduler):
    """Test execution without crew setup."""
    manager = QAMManagerAgent(azure_config, scheduler=mock_scheduler)
    
    with pytest.raises(RuntimeError) as exc_info:
        manager.execute()
    
    assert "Crew not set up" in str(exc_info.value)