#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

import os
import json
from unittest.mock import patch, MagicMock
from qam.azure_quantum import AzureQuantumConfig, AzureQuantumClient

def create_mock_subprocess_run(return_values):
    def mock_run(*args, **kwargs):
        mock = MagicMock()
        command = args[0][0:2] if args and args[0] else []
        
        if command == ["az", "--version"]:
            mock.stdout = "azure-cli 2.50.0"
        elif command == ["az", "extension"]:
            if "list" in args[0]:
                mock.stdout = json.dumps([{"name": "quantum"}])
        elif command == ["az", "quantum"]:
            if "job" in args[0]:
                if "submit" in args[0]:
                    mock.stdout = json.dumps({"id": "test-job-id"})
                elif "show" in args[0]:
                    mock.stdout = json.dumps({"status": "Completed"})
                elif "output" in args[0]:
                    mock.stdout = json.dumps({"result": {"solution": [1, 0]}})
        return mock
    return mock_run

def test_azure_quantum():
    print("Testing Azure Quantum Functions...")
    
    # Test 1: Create config
    print("\n1. Testing AzureQuantumConfig creation")
    config = AzureQuantumConfig(
        resource_group="test-group",
        workspace_name="test-workspace",
        location="westus",
        subscription_id="test-subscription",
        target_id="microsoft.paralleltempering.cpu"
    )
    print(f"Config created: {config}")

    # Mock subprocess.run
    with patch('subprocess.run', side_effect=create_mock_subprocess_run({})) as mock_run:
        try:
            # Test 2: Create client
            print("\n2. Testing AzureQuantumClient creation")
            client = AzureQuantumClient(config)
            print("Client created successfully")

            # Test 3: Submit QUBO
            print("\n3. Testing QUBO submission")
            problem = {
                "type": "qubo",
                "terms": [{"c": 1.0, "ids": [0, 1]}],
                "size": 2
            }
            job_id = client.submit_qubo(problem)
            print(f"Job submitted with ID: {job_id}")

            # Test 4: Get job status
            print("\n4. Testing job status retrieval")
            status = client.get_job_status(job_id)
            print(f"Job status: {status}")

            # Test 5: Get job results
            print("\n5. Testing job result retrieval")
            results = client.get_job_result(job_id)
            print(f"Job results: {json.dumps(results, indent=2)}")

            # Test 6: Wait for job
            print("\n6. Testing wait_for_job")
            results = client.wait_for_job(job_id, timeout_seconds=60)
            print(f"Wait for job results: {json.dumps(results, indent=2)}")

            print("\nVerifying mock calls:")
            print(f"Total mock calls: {len(mock_run.call_args_list)}")
            for i, call in enumerate(mock_run.call_args_list, 1):
                args = call[0][0] if call[0] else []
                print(f"Call {i}: {' '.join(args)}")

        except Exception as e:
            print(f"\n❌ Error during testing: {str(e)}")
            return

    print("\n✅ Azure Quantum testing complete")

if __name__ == "__main__":
    test_azure_quantum()