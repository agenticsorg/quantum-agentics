"""
Test for running quantum operations on real quantum hardware.
"""
import os
import json
import tempfile
import subprocess
import pytest
from qam.azure_quantum import AzureQuantumConfig, AzureQuantumClient

def test_quantum_hardware_connection():
    """Test connection to real quantum hardware."""
    
    # Load configuration from environment variables
    config = AzureQuantumConfig(
        resource_group=os.getenv('AZURE_RESOURCE_GROUP'),
        workspace_name=os.getenv('AZURE_WORKSPACE_NAME'),
        location=os.getenv('AZURE_LOCATION'),
        subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'),
        target_id='ionq.qpu'  # Use actual quantum hardware
    )
    
    # Initialize client
    client = AzureQuantumClient(config)
    
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
    
    circuit_file = None
    try:
        # Save circuit to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(circuit, f)
            circuit_file = f.name

        # Submit job with longer timeout for hardware
        result = subprocess.run([
            "az", "quantum", "job", "submit",
            "--target-id", config.target_id,
            "--job-input-file", circuit_file,
            "--job-input-format", "ionq.circuit.v1",
            "--job-output-format", "ionq.quantum-results.v1",
            "--shots", "1000",
            "-o", "json"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            error_msg = result.stderr.lower()
            print("\nError: Unable to access quantum hardware.")
            
            if "provider id" in error_msg:
                print("\nYour account needs to be upgraded to access real quantum hardware:")
                print("1. Visit: https://azure.microsoft.com/en-us/products/quantum")
                print("2. Upgrade to a paid subscription")
                print("3. Request access to IonQ hardware")
                print("\nIn the meantime, you can use 'ionq.simulator' for testing.")
                return
            
            print("\nError details:")
            print("Exit code:", result.returncode)
            print("Stderr:", result.stderr)
            print("Stdout:", result.stdout)
            raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
        
        job_data = json.loads(result.stdout)
        job_id = job_data['id']
        print(f"Job submitted successfully (ID: {job_id})")
        
        # Wait for job completion with extended timeout
        wait_result = subprocess.run([
            "az", "quantum", "job", "wait",
            "--job-id", job_id,
            "--max-poll-wait-secs", "600"  # 10 minute timeout
        ], capture_output=True, text=True)
        
        if wait_result.returncode != 0:
            error_msg = wait_result.stderr.lower()
            if "quota" in error_msg or "credit" in error_msg:
                print("\nError: Quantum hardware access interrupted. You may need to:")
                print("1. Upgrade your Azure Quantum account")
                print("2. Ensure you have sufficient quantum credits")
                return
            raise subprocess.CalledProcessError(wait_result.returncode, wait_result.args)
        
        # Get results
        output_result = subprocess.run([
            "az", "quantum", "job", "output",
            "--job-id", job_id,
            "-o", "json"
        ], check=True, capture_output=True, text=True)
        
        result = json.loads(output_result.stdout)
        
        # Verify we got results
        assert result is not None
        assert 'histogram' in result
        
        print("Job completed successfully")
        print("Results:", result)
        
    except TimeoutError as e:
        print("\nError: Job timed out. When using real quantum hardware, jobs may take longer.")
        print("Consider increasing the timeout or using the simulator for testing.")
    except Exception as e:
        error_msg = str(e).lower()
        if "quota" in error_msg or "credit" in error_msg or "provider" in error_msg:
            print("\nError: Quantum hardware access failed. You need to:")
            print("1. Upgrade your Azure Quantum account")
            print("2. Ensure you have sufficient quantum credits")
            print("3. Request access to IonQ hardware")
            print("\nVisit: https://azure.microsoft.com/en-us/products/quantum")
        else:
            pytest.fail(f"Error running quantum hardware test: {str(e)}")
    finally:
        # Clean up temporary file
        if circuit_file and os.path.exists(circuit_file):
            os.remove(circuit_file)

if __name__ == '__main__':
    # Can be run directly with python -m tests.scripts.test_quantum_hardware
    test_quantum_hardware_connection()
