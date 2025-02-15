"""
Tests for Azure Quantum integration.
"""
import json
import subprocess
import pytest
from unittest.mock import patch, Mock
from qam.azure_quantum import AzureQuantumConfig, AzureQuantumClient

@pytest.fixture
def azure_config():
    """Fixture for Azure Quantum configuration."""
    return AzureQuantumConfig(
        resource_group="test-group",
        workspace_name="test-workspace",
        location="westus",
        subscription_id="test-sub"
    )

def create_mock_response(stdout="", stderr="", returncode=0):
    """Create a mock subprocess response."""
    mock = Mock()
    mock.stdout = stdout
    mock.stderr = stderr
    mock.returncode = returncode
    return mock

@pytest.fixture
def mock_subprocess():
    """Fixture to mock subprocess calls."""
    with patch('subprocess.run') as mock_run:
        # Default successful response
        mock_run.return_value = create_mock_response(
            stdout=json.dumps([{"name": "quantum"}])
        )
        yield mock_run

def test_client_initialization(azure_config, mock_subprocess):
    """Test Azure Quantum client initialization."""
    # Set up mock responses for initialization sequence
    mock_subprocess.side_effect = [
        # CLI version check
        create_mock_response(stdout=json.dumps({"azure-cli": "2.0.0"})),
        # Extension list
        create_mock_response(stdout=json.dumps([{"name": "quantum"}])),
        # Workspace setup
        create_mock_response(),
        # Target setup
        create_mock_response()
    ]
    
    client = AzureQuantumClient(azure_config)
    assert client.config == azure_config

def test_submit_qubo(azure_config, mock_subprocess):
    """Test QUBO problem submission."""
    # Set up mock responses
    mock_subprocess.side_effect = [
        # CLI version check
        create_mock_response(stdout=json.dumps({"azure-cli": "2.0.0"})),
        # Extension list
        create_mock_response(stdout=json.dumps([{"name": "quantum"}])),
        # Workspace setup
        create_mock_response(),
        # Target setup
        create_mock_response(),
        # Job submission
        create_mock_response(stdout=json.dumps({"id": "test-job-id", "status": "Waiting"}))
    ]
    
    client = AzureQuantumClient(azure_config)
    problem = {
        "problem_type": "qubo",
        "terms": [
            {"c": 1.0, "ids": [0]},
            {"c": 2.0, "ids": [0, 1]}
        ]
    }
    
    job_id = client.submit_qubo(problem)
    assert job_id == "test-job-id"

def test_get_job_status(azure_config, mock_subprocess):
    """Test job status retrieval."""
    # Set up mock responses
    mock_subprocess.side_effect = [
        # CLI version check
        create_mock_response(stdout=json.dumps({"azure-cli": "2.0.0"})),
        # Extension list
        create_mock_response(stdout=json.dumps([{"name": "quantum"}])),
        # Workspace setup
        create_mock_response(),
        # Target setup
        create_mock_response(),
        # Status check
        create_mock_response(stdout=json.dumps({"id": "test-job-id", "status": "Succeeded"}))
    ]
    
    client = AzureQuantumClient(azure_config)
    status = client.get_job_status("test-job-id")
    assert status == "Succeeded"

def test_get_job_result(azure_config, mock_subprocess):
    """Test job result retrieval."""
    mock_result = {
        "solution": [0, 1, 0],
        "cost": -2.5
    }
    # Set up mock responses
    mock_subprocess.side_effect = [
        # CLI version check
        create_mock_response(stdout=json.dumps({"azure-cli": "2.0.0"})),
        # Extension list
        create_mock_response(stdout=json.dumps([{"name": "quantum"}])),
        # Workspace setup
        create_mock_response(),
        # Target setup
        create_mock_response(),
        # Result retrieval
        create_mock_response(stdout=json.dumps(mock_result))
    ]
    
    client = AzureQuantumClient(azure_config)
    result = client.get_job_result("test-job-id")
    assert result == mock_result

def test_wait_for_job(azure_config, mock_subprocess):
    """Test job wait functionality."""
    mock_result = {
        "solution": [1, 0],
        "cost": -1.5
    }
    # Set up mock responses
    mock_subprocess.side_effect = [
        # CLI version check
        create_mock_response(stdout=json.dumps({"azure-cli": "2.0.0"})),
        # Extension list
        create_mock_response(stdout=json.dumps([{"name": "quantum"}])),
        # Workspace setup
        create_mock_response(),
        # Target setup
        create_mock_response(),
        # Wait command
        create_mock_response(),
        # Result retrieval
        create_mock_response(stdout=json.dumps(mock_result))
    ]
    
    client = AzureQuantumClient(azure_config)
    result = client.wait_for_job("test-job-id", timeout_seconds=60)
    assert result == mock_result

def test_wait_for_job_timeout(azure_config, mock_subprocess):
    """Test job wait timeout handling."""
    # Set up mock responses
    mock_subprocess.side_effect = [
        # CLI version check
        create_mock_response(stdout=json.dumps({"azure-cli": "2.0.0"})),
        # Extension list
        create_mock_response(stdout=json.dumps([{"name": "quantum"}])),
        # Workspace setup
        create_mock_response(),
        # Target setup
        create_mock_response(),
        # Wait command - timeout error
        subprocess.CalledProcessError(1, "cmd", stderr="timeout")
    ]
    
    client = AzureQuantumClient(azure_config)
    with pytest.raises(TimeoutError) as exc_info:
        client.wait_for_job("test-job-id", timeout_seconds=1)
    assert "did not complete within" in str(exc_info.value)

def test_cli_not_installed(azure_config, mock_subprocess):
    """Test handling of missing Azure CLI."""
    mock_subprocess.side_effect = FileNotFoundError()
    
    with pytest.raises(RuntimeError) as exc_info:
        AzureQuantumClient(azure_config)
    assert "Azure CLI not found" in str(exc_info.value)

def test_workspace_setup_failure(azure_config, mock_subprocess):
    """Test handling of workspace setup failure."""
    # Set up mock responses
    mock_subprocess.side_effect = [
        # CLI version check
        create_mock_response(stdout=json.dumps({"azure-cli": "2.0.0"})),
        # Extension list
        create_mock_response(stdout=json.dumps([{"name": "quantum"}])),
        # Workspace setup failure
        subprocess.CalledProcessError(1, "cmd", stderr="workspace error")
    ]
    
    with pytest.raises(RuntimeError) as exc_info:
        AzureQuantumClient(azure_config)
    assert "Failed to set up Azure Quantum workspace" in str(exc_info.value)