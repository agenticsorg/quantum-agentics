#!/usr/bin/env python3
"""
Example of using ReACT with Azure Quantum optimization.

To run this example, you need:
1. Azure CLI installed and configured
2. Azure Quantum workspace set up
3. Environment variables set:
   - AZURE_RESOURCE_GROUP: Your Azure resource group name
   - AZURE_WORKSPACE_NAME: Your Azure Quantum workspace name
   - AZURE_LOCATION: Azure region (e.g., 'westus')
   - AZURE_SUBSCRIPTION_ID: Your Azure subscription ID
   - AZURE_TARGET_ID: (Optional) Target quantum processor/simulator

Example:
    export AZURE_RESOURCE_GROUP="my-resource-group"
    export AZURE_WORKSPACE_NAME="my-workspace"
    export AZURE_LOCATION="westus"
    export AZURE_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    python example_react_azure_quantum.py
"""
import sys
import os
import json
import subprocess
import time
from typing import Dict, Optional

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, project_root)

from agents.qam_agent.agent import QAMAgent

def check_azure_cli() -> bool:
    """Check if Azure CLI and quantum extension are installed."""
    try:
        print("🔍 Checking Azure CLI installation...")
        subprocess.run(
            ["az", "--version"],
            check=True, capture_output=True, text=True
        )
        
        print("🔍 Checking Azure Quantum extension...")
        ext_result = subprocess.run(
            ["az", "extension", "list"],
            check=True, capture_output=True, text=True
        )
        
        try:
            extensions = json.loads(ext_result.stdout)
            has_quantum = any(ext.get('name') == 'quantum' for ext in extensions)
        except json.JSONDecodeError:
            has_quantum = False
        
        if not has_quantum:
            print("📦 Installing Azure Quantum extension...")
            subprocess.run(
                ["az", "extension", "add", "-n", "quantum"],
                check=True, capture_output=True, text=True
            )
            
        return True
                
    except FileNotFoundError:
        print("❌ Azure CLI not found. Please install Azure CLI.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Azure CLI check failed: {e.stderr or str(e)}")
        return False

def submit_azure_quantum_job(problem_data: Dict, config: Dict) -> Optional[str]:
    """Submit job to Azure Quantum using CLI."""
    try:
        # Create temporary file for problem data
        with open("problem.json", "w") as f:
            json.dump(problem_data, f)
            
        print("🚀 Submitting job to Azure Quantum...")
        result = subprocess.run(
            ["az", "quantum", "job", "submit",
             "--target-id", config['azure'].get('target_id', 'microsoft.paralleltempering.cpu'),
             "--job-input-file", "problem.json",
             "--job-input-format", "ionq.circuit.v1",
             "--job-output-format", "ionq.quantum-results.v1",
             "--shots", "1000",
             "-o", "json"],
            check=True, capture_output=True, text=True
        )
        
        # Parse job ID
        try:
            job_data = json.loads(result.stdout)
            return job_data.get('id')
        except json.JSONDecodeError:
            print("❌ Failed to parse job submission response")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to submit job: {e.stderr or str(e)}")
        return None
    finally:
        # Clean up temporary file
        if os.path.exists("problem.json"):
            os.remove("problem.json")

def get_job_status(job_id: str) -> Optional[Dict]:
    """Get Azure Quantum job status using CLI."""
    try:
        result = subprocess.run(
            ["az", "quantum", "job", "show",
             "--job-id", job_id,
             "-o", "json"],
            check=True, capture_output=True, text=True
        )
        
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"❌ Failed to get job status: {str(e)}")
        return None

def run_react_azure_quantum():
    # Configuration with Azure settings
    sample_config = {
        "agent_name": "ReACTAzureQuantumAgent",
        "mode": "test",  # Use test mode for verbose output
        "settings": {
            "qaoa_p_steps": 3,
            "qaoa_learning_rate": 0.05,
            "optimization_target": 0.95
        },
        # Use environment variables for Azure Quantum workspace details
        "azure": {
            "resource_group": os.getenv("AZURE_RESOURCE_GROUP", ""),
            "workspace_name": os.getenv("AZURE_WORKSPACE_NAME", ""),
            "location": os.getenv("AZURE_LOCATION", ""),
            "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID", ""),
            "target_id": os.getenv("AZURE_TARGET_ID", "microsoft.paralleltempering.cpu")
        }
    }
    
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║               ReACT Azure Quantum Optimization                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    # Check Azure CLI and setup
    if not check_azure_cli():
        print("\n⚠️ Azure CLI not found. Using local QAOA optimization instead.")
        sample_config.pop('azure', None)
    elif not all([sample_config['azure']['resource_group'], 
                  sample_config['azure']['workspace_name'],
                  sample_config['azure']['subscription_id']]):
        print("\n⚠️ Azure Quantum credentials not found in environment variables. Using local QAOA optimization instead.")
        sample_config.pop('azure', None)
    
    # Create agent instance
    agent = QAMAgent(sample_config)
    
    # Define optimization task with ReACT prompts
    optimization_task = """
    Optimize a QUBO problem using Azure Quantum with the following objectives:
    1. Minimize total execution time
    2. Maximize resource utilization
    3. Respect task dependencies
    4. Achieve solution quality above 0.95
    
    Use ReACT methodology to:
    1. Analyze the problem structure
    2. Formulate QUBO representation
    3. Submit to Azure Quantum or use local QAOA
    4. Monitor job progress and analyze results
    5. Adjust parameters and resubmit if needed
    """
    
    # Run agent with ReACT reasoning
    try:
        decisions = agent.run(
            prompt=optimization_task,
            task_type="both"  # Use both research and implementation
        )
        
        if decisions:
            print("\n🎯 Final Optimization Results:")
            for decision in decisions:
                print(f"   ➤ {decision}")
    except KeyboardInterrupt:
        print("\n⚠️ Optimization interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during optimization: {str(e)}")

if __name__ == "__main__":
    run_react_azure_quantum()
