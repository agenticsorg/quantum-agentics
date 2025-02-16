#!/usr/bin/env python3
import sys
import os
# Add project root to sys.path so that modules can be found (same as example_agent_run.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, project_root)

from agents.qam_agent.tools.qam_tools import QAMTools

def run_hybrid_scheduler():
    sample_config = {
        "agent_name": "HybridSchedulerExample",
        "settings": {
            "qaoa_p_steps": 2,
            "qaoa_learning_rate": 0.1,
            "cluster_threshold": 3
        },
        # Azure configuration is required for Azure Quantum features
        # Replace these values with your actual Azure Quantum workspace details
        # "azure": {
        #     "resource_group": "your-resource-group",
        #     "workspace_name": "your-workspace-name",
        #     "subscription_id": "your-subscription-id",
        #     "location": "your-location",
        #     "target_id": "microsoft.paralleltempering.cpu"
        # }
    }
    
    tools = QAMTools(sample_config)
    
    # Simulate tasks with dependencies and resource requirements
    tasks = [
        {"id": "Task_0", "dependencies": [], "resources": ["R1"]},
        {"id": "Task_1", "dependencies": ["Task_0"], "resources": ["R1", "R2"]},
        {"id": "Task_2", "dependencies": ["Task_1"], "resources": ["R2"]}
    ]
    
    # Define available resources
    resources = {
        "R1": {"capacity": 2},
        "R2": {"capacity": 1}
    }
    
    print("Running Hybrid Scheduler Example...")
    print("Initial tasks:")
    for task in tasks:
        print(task)
    
    quantum_schedule_result = tools.optimize_quantum_schedule(tasks, resources)
    print("Optimized Hybrid Schedule Result:")
    print(quantum_schedule_result)

if __name__ == "__main__":
    run_hybrid_scheduler()
