#!/usr/bin/env python3
import sys
import os
import json
import time
import subprocess
from dotenv import load_dotenv

# Add project root to sys.path so that the 'qam' module can be found.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, project_root)

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from agents.qam_agent.tools.qam_tools import QAMTools

def analyze_bell_state_results(results):
    """Analyze and format Bell state measurement results"""
    if not results:
        return "No measurement results available"
        
    # Expected Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
    # Should see approximately 50% |00⟩ and 50% |11⟩
    counts = {
        "00": 0,  # Both qubits in |0⟩
        "01": 0,  # First qubit |0⟩, second |1⟩
        "10": 0,  # First qubit |1⟩, second |0⟩
        "11": 0   # Both qubits in |1⟩
    }
    
    total_shots = 0
    if isinstance(results, dict):
        if 'histogram' in results:  # IonQ format
            for state_idx, probability in results['histogram'].items():
                # Convert index to binary string
                state = format(int(state_idx), '02b')
                counts[state] = int(probability * 1000)  # Convert probability to count (1000 shots)
                total_shots += counts[state]
        elif 'ro' in results:  # Rigetti format
            for shot in results['ro']:
                # Convert measurement array to state string
                state = ''.join(str(bit) for bit in shot)
                counts[state] = counts.get(state, 0) + 1
                total_shots += 1
            
    analysis = []
    analysis.append("📊 Bell State Analysis")
    analysis.append("====================")
    analysis.append(f"Total shots: {total_shots}")
    analysis.append("\nMeasurement Probabilities:")
    
    if total_shots > 0:
        for state, count in counts.items():
            prob = count / total_shots * 100
            analysis.append(f"|{state}⟩: {count} shots ({prob:.1f}%)")
            
        # Check if results match Bell state expectations
        bell_state_quality = "Excellent"
        if counts['01'] + counts['10'] > 0.1 * total_shots:
            bell_state_quality = "Poor"
        elif abs(counts['00'] - counts['11']) > 0.2 * total_shots:
            bell_state_quality = "Fair"
            
        analysis.append(f"\nBell State Quality: {bell_state_quality}")
        
        # Add quantum state interpretation
        analysis.append("\nQuantum State Interpretation:")
        if bell_state_quality == "Excellent":
            analysis.append("The measured state closely approximates the Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2")
            analysis.append("This demonstrates quantum entanglement between the two qubits")
        elif bell_state_quality == "Fair":
            analysis.append("The measured state shows some quantum correlation, but with significant asymmetry")
        else:
            analysis.append("The measured state shows significant deviations from the expected Bell state")
            
    return "\n".join(analysis)

def run_azure_quantum_job():
    # Azure Quantum configuration
    sample_config = {
        "agent_name": "AzureQuantumJobExample",
        "settings": {
            "qaoa_p_steps": 3,
            "qaoa_learning_rate": 0.05
        },
        "azure": {
            "resource_group": os.getenv("AZURE_RESOURCE_GROUP"),
            "workspace_name": os.getenv("AZURE_WORKSPACE_NAME"),
            "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID"),
            "location": os.getenv("AZURE_LOCATION", "westus"),
            "target_id": os.getenv("AZURE_TARGET_ID", "ionq.simulator")
        }
    }
    
    # Check Azure environment variables
    required_vars = [
        "AZURE_RESOURCE_GROUP",
        "AZURE_WORKSPACE_NAME",
        "AZURE_SUBSCRIPTION_ID"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("❌ Missing required Azure environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables and try again.")
        return
        
    print("🔍 Checking Azure Quantum setup...")
    
    # Set Azure Quantum workspace
    try:
        subprocess.run([
            "az", "quantum", "workspace", "set",
            "-g", sample_config['azure']['resource_group'],
            "-w", sample_config['azure']['workspace_name'],
            "-l", sample_config['azure']['location'],
            "--subscription", sample_config['azure']['subscription_id']
        ], check=True, capture_output=True, text=True)
        
        print("✅ Azure Quantum workspace configured")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set Azure Quantum workspace: {e.stderr}")
        return
        
    # Define Bell state circuit for IonQ
    circuit = {
        "format": "ionq.circuit.v1",
        "body": {
            "qubits": 2,
            "circuit": [
                {"gate": "gpi2", "target": 0, "phase": 0},  # Initialize in |0⟩ state
                {"gate": "gpi2", "target": 1, "phase": 0},  # Initialize in |0⟩ state
                {"gate": "h", "target": 0},  # Hadamard on first qubit
                {"gate": "cnot", "control": 0, "target": 1},  # CNOT between qubits
                {"gate": "measure", "target": [0, 1]}  # Measure both qubits
            ]
        }
    }
    
    # Save circuit to file
    with open("circuit.json", "w") as f:
        json.dump(circuit, f)
        
    print("\n🚀 Submitting job to Azure Quantum...")
    print("\nCircuit Description:")
    print("1. Initialize two qubits in |00⟩ state")
    print("2. Apply Hadamard gate to first qubit")
    print("3. Apply CNOT gate between qubits")
    print("4. Measure both qubits")
    print("\nExpected Result: Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2")
    
    try:
        # Submit job using Azure CLI
        result = subprocess.run([
            "az", "quantum", "job", "submit",
            "--target-id", sample_config['azure']['target_id'],
            "--job-input-file", "circuit.json",
            "--job-input-format", "ionq.circuit.v1",
            "--job-output-format", "ionq.quantum-results.v1",
            "--shots", "1000",
            "-o", "json"
        ], check=True, capture_output=True, text=True)
        
        job_data = json.loads(result.stdout)
        job_id = job_data['id']
        print(f"✅ Job submitted successfully (ID: {job_id})")
        
        # Poll for job completion
        print("\n⏳ Waiting for job completion...")
        while True:
            status_result = subprocess.run([
                "az", "quantum", "job", "show",
                "--job-id", job_id,
                "-o", "json"
            ], check=True, capture_output=True, text=True)
            
            status_data = json.loads(status_result.stdout)
            status = status_data.get('status', '')
            
            if status.lower() == 'succeeded':
                print("\n✨ Job completed successfully!")
                # Get job output
                output_result = subprocess.run([
                    "az", "quantum", "job", "output",
                    "--job-id", job_id,
                    "-o", "json"
                ], check=True, capture_output=True, text=True)
                results = json.loads(output_result.stdout)
                print("\n" + analyze_bell_state_results(results))
                break
            elif status.lower() in ['failed', 'cancelled']:
                print(f"\n❌ Job {status.lower()}")
                print(f"Error: {status_data.get('error_data', {}).get('message', 'Unknown error')}")
                break
                
            print(".", end="", flush=True)
            time.sleep(5)
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {e.stderr}")
    finally:
        # Clean up temporary file
        if os.path.exists("circuit.json"):
            os.remove("circuit.json")

if __name__ == "__main__":
    run_azure_quantum_job()
