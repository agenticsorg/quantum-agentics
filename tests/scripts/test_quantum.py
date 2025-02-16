#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

from qam.azure_quantum import AzureQuantumConfig, AzureQuantumClient
import json

def main():
    # Configure Azure Quantum workspace
    config = AzureQuantumConfig(
        resource_group="AzureQuantum",
        workspace_name="QuantumGPT",
        location="eastus",
        target_id="ionq.simulator"  # Using IonQ simulator
    )

    # Initialize client
    client = AzureQuantumClient(config)

    # Create a simple quantum circuit in JSON format
    problem = {
        "input_qubits": 2,
        "input_params": [],
        "operations": [
            {
                "gate": "h",
                "targets": [0]
            },
            {
                "gate": "cnot",
                "controls": [0],
                "targets": [1]
            }
        ]
    }

    print("Submitting quantum circuit...")
    
    # Submit the problem
    job_id = client.submit_qubo(problem)
    print(f"Job ID: {job_id}")

    # Wait for the job to complete
    print("Waiting for results...")
    result = client.wait_for_job(job_id)
    
    # Print results
    print("\nResults:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()