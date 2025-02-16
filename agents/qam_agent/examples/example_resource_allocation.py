#!/usr/bin/env python3
import sys
import os
# Add project root to sys.path (same approach as example_agent_run.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, project_root)

from agents.qam_agent.tools.qam_tools import QAMTools

def run_resource_allocation_example():
    sample_config = {
        "agent_name": "ResourceAllocationExample",
        "settings": {
            "qaoa_p_steps": 2
        }
    }
    
    tools = QAMTools(sample_config)
    
    tasks = [
        {"id": "T1", "dependencies": [], "resources": ["R1"]},
        {"id": "T2", "dependencies": ["T1"], "resources": ["R1", "R2"]},
        {"id": "T3", "dependencies": ["T2"], "resources": ["R2"]}
    ]
    
    resources = {
        "R1": {"capacity": 1},
        "R2": {"capacity": 1}
    }
    
    print("Running Resource Allocation Example...")
    schedule_result = tools.optimize_quantum_schedule(tasks, resources)
    
    print("Optimized Schedule:")
    print(schedule_result)
    
    validation_results = tools.validate_quantum_solution(schedule_result.get('schedule', {}), tasks, resources)
    
    print("Validation Results:")
    print(validation_results)

if __name__ == "__main__":
    run_resource_allocation_example()