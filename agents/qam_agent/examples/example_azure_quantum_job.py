#!/usr/bin/env python3
import sys
import os

# Add project root to sys.path so that the 'qam' module can be found.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, project_root)

from agents.qam_agent.tools.qam_tools import QAMTools

def run_azure_quantum_job():
    # Sample configuration including Azure Quantum credentials
    sample_config = {
        "agent_name": "AzureQuantumJobExample",
        "settings": {
            "qaoa_p_steps": 3,
            "qaoa_learning_rate": 0.05
        },
        "azure": {
            "resource_group": "myResourceGroup",
            "workspace_name": "myWorkspace",
            "subscription_id": "mySubscriptionId",
            "location": "westus",
            "target_id": "microsoft.paralleltempering.cpu"
        }
    }
    
    # Instantiate QAMTools with the sample config
    tools = QAMTools(sample_config)
    
    # Define a sample QUBO problem (a simple simulated QUBO)
    qubo_problem = {
        "Q": {
            ("x1", "x1"): 1.0,
            ("x1", "x2"): -0.5,
            ("x2", "x2"): 2.0
        }
    }
    
    print("Starting Azure Quantum Job Submission via QAMTools...")
    print("Submitting QUBO problem to Azure Quantum...")
    
    # Execute job on Azure Quantum using QAMTools
    azure_result = tools.execute_on_azure_quantum(qubo_problem)
    
    print("Azure Quantum Job Result:")
    print(azure_result)

if __name__ == "__main__":
    run_azure_quantum_job()