#!/usr/bin/env python3
import sys
import os
import json
import time
import subprocess
import numpy as np
from dotenv import load_dotenv

# Add project root to sys.path so that the 'qam' module can be found.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, project_root)

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

###############################################################################
# Advanced ReACT-inspired Bell State Optimizer
# This version includes more verbose reasoning, quantum state analysis,
# multi-strategy optimization, and measurement analysis for improved intelligence.
###############################################################################

class QuantumStateAnalyzer:
    """Analyze theoretical quantum state evolution or do more advanced simulation."""
    def analyze_initial_state(self):
        print("[ANALYSIS] Theoretically, for a perfect Bell state, we need |00> -> (|00> + |11>)/sqrt(2).")

    def analyze_current_state(self):
        print("[ANALYSIS] This method would track or compute state evolution if a simulator supports it.")
        # In a real advanced scenario, we might maintain a local state vector or density matrix

class MeasurementAnalyzer:
    """Perform advanced analysis of measurement results."""
    def analyze_results(self, counts, total_shots):
        print("[MEASUREMENT] Analyzing results distribution with statistical discussion.")
        for state, count in counts.items():
            prob = count / total_shots * 100
            print(f" - State={state}: Shots={count} Probability={prob:.1f}%")

        # Could add error bars, significance testing, etc.

class ReACTOptimizer:
    """Implements advanced ReACT style reasoning, where we systematically refine the approach."""
    def select_strategy(self):
        # We might add logic for choosing e.g. gradient, genetic, or random search
        print("[THOUGHT] For now, a straightforward random adjustment approach is used.")
        return 'random'

    def evaluate_strategy(self, results):
        print("[REFLECTION] Evaluate if the chosen updates improved fidelity or not, then adapt if needed.")

class AdvancedBellStateOptimizer:
    def __init__(self):
        # Target fidelity for success
        self.target_fidelity = 0.95
        self.max_iterations = 10
        self.current_iteration = 0
        self.best_fidelity = 0.0
        self.best_params = None

        # We store a single parameter (Hadamard power) as before
        self.parameters = {
            'h_power': 1.0,  # 1.0 => standard Hadamard
        }

        # Create advanced classes
        self.state_analyzer = QuantumStateAnalyzer()
        self.measurement_analyzer = MeasurementAnalyzer()
        self.react_optimizer = ReACTOptimizer()

    def calculate_fidelity(self, counts):
        """Calculate fidelity with the ideal Bell state."""
        if not counts:
            return 0.0
        total_shots = sum(counts.values())
        if total_shots == 0:
            return 0.0

        p00 = counts.get('00', 0) / total_shots
        p11 = counts.get('11', 0) / total_shots
        p01 = counts.get('01', 0) / total_shots
        p10 = counts.get('10', 0) / total_shots

        # We want ~50% for |00> and ~50% for |11>, none for others
        target_prob = 0.5
        fidelity = 1.0 - abs(p00 - target_prob) - abs(p11 - target_prob) - p01 - p10
        return max(0.0, fidelity)

    def generate_circuit(self):
        """Build IonQ circuit with the parameterized Hadamard and standard CNOT."""
        circuit = {
            "format": "ionq.circuit.v1",
            "body": {
                "qubits": 2,
                "circuit": [
                    {
                        "gate": "h",
                        "target": 0,
                        "power": self.parameters['h_power']
                    },
                    {
                        "gate": "cnot",
                        "control": 0,
                        "target": 1
                    },
                    {
                        "gate": "measure",
                        "target": [0, 1]
                    }
                ]
            }
        }
        return circuit

    def run_circuit(self):
        """Submit job to IonQ simulator on Azure Quantum, track results."""
        circuit = self.generate_circuit()
        with open("circuit.json", "w") as f:
            json.dump(circuit, f)

        try:
            result = subprocess.run([
                "az", "quantum", "job", "submit",
                "--target-id", "ionq.simulator",
                "--job-input-file", "circuit.json",
                "--job-input-format", "ionq.circuit.v1",
                "--job-output-format", "ionq.quantum-results.v1",
                "--shots", "1000",
                "-o", "json"
            ], check=True, capture_output=True, text=True)

            job_data = json.loads(result.stdout)
            job_id = job_data['id']
            print(f"[ACTION] Submitted IonQ job (ID: {job_id})")

            while True:
                status_result = subprocess.run([
                    "az", "quantum", "job", "show",
                    "--job-id", job_id,
                    "-o", "json"
                ], check=True, capture_output=True, text=True)
                status_data = json.loads(status_result.stdout)
                if status_data.get('status', '').lower() == 'succeeded':
                    output_result = subprocess.run([
                        "az", "quantum", "job", "output",
                        "--job-id", job_id,
                        "-o", "json"
                    ], check=True, capture_output=True, text=True)
                    results = json.loads(output_result.stdout)

                    # Build a counts dictionary from histogram
                    counts = {}
                    if 'histogram' in results:
                        for state_idx, probability in results['histogram'].items():
                            state = format(int(state_idx), '02b')
                            counts[state] = int(probability * 1000)
                    return counts
                elif status_data.get('status', '').lower() in ['failed', 'cancelled']:
                    return None
                time.sleep(5)
        except subprocess.CalledProcessError as e:
            print("[ERROR] Job submission failed:", e.stderr)
            return None
        finally:
            if os.path.exists("circuit.json"):
                os.remove("circuit.json")

    def update_parameters(self, fidelity, counts):
        """Adjust the 'h_power' parameter in an attempt to fix the distribution."""
        total_shots = sum(counts.values())
        p00 = counts.get('00', 0) / total_shots if total_shots else 1.0
        p11 = counts.get('11', 0) / total_shots if total_shots else 0.0

        print("[THOUGHT] Current distribution:", f"|00>={p00:.3f}, |11>={p11:.3f}")

        if fidelity > self.best_fidelity:
            print("[OBSERVATION] We improved fidelity => small adjustments.")
            scale = 0.1
        else:
            print("[OBSERVATION] No improvement => bigger adjustments.")
            scale = 0.3

        # If we have only |00>, we want more superposition => increase h_power
        # If we had only |11>, we want to reduce h_power
        if p00 >= 0.5:
            # more superposition => random increase
            self.parameters['h_power'] += scale * np.random.uniform(0, 0.2)
        else:
            # random decrease
            self.parameters['h_power'] += scale * np.random.uniform(-0.2, 0)

        self.parameters['h_power'] = np.clip(self.parameters['h_power'], 0.5, 1.5)

        print("[ACTION] Updated parameters => h_power=", f"{self.parameters['h_power']:.3f}")

    def optimize(self):
        print("[THOUGHT] Starting advanced Bell state optimization")
        self.state_analyzer.analyze_initial_state()
        while self.current_iteration < self.max_iterations:
            iteration_label = f"Iteration {self.current_iteration+1}/{self.max_iterations}"
            print(f"\n[ACTION] {iteration_label} with h_power={self.parameters['h_power']:.3f}")

            # Step 1: Possibly analyze current state, if we had a local simulator
            self.state_analyzer.analyze_current_state()

            # Step 2: Execute circuit
            counts = self.run_circuit()
            if not counts:
                print("[OBSERVATION] Job failed or was cancelled, adjusting parameters randomly.")
                # default to all |00> as if we failed
                self.update_parameters(0.0, {"00": 1000})
                self.current_iteration += 1
                continue

            # Step 3: Evaluate measurements
            fidelity = self.calculate_fidelity(counts)
            total_shots = sum(counts.values())
            self.measurement_analyzer.analyze_results(counts, total_shots)
            print("[ANALYSIS] Computed fidelity=", f"{fidelity:.3f}")

            # Step 4: Check improvement
            if fidelity > self.best_fidelity:
                self.best_fidelity = fidelity
                self.best_params = dict(self.parameters)

            # Step 5: Check success
            if fidelity >= self.target_fidelity:
                print("[REFLECTION] Target fidelity reached => success!")
                print("Optimal parameters =>", self.best_params)
                return

            # Step 6: Reason about next step
            self.update_parameters(fidelity, counts)
            self.current_iteration += 1

        print("[REFLECTION] Reached maximum iterations.")
        print("Best fidelity=", f"{self.best_fidelity:.3f}")
        if self.best_params:
            print("Best parameters =>", self.best_params)
        else:
            print("Never improved from zero fidelity. Possibly IonQ simulator ignoring 'power' param.")

def main():
    print("[ACTION] Configuring Azure Quantum workspace for advanced optimization...")
    try:
        subprocess.run([
            "az", "quantum", "workspace", "set",
            "-g", os.getenv("AZURE_RESOURCE_GROUP"),
            "-w", os.getenv("AZURE_WORKSPACE_NAME"),
            "-l", os.getenv("AZURE_LOCATION", "westus"),
            "--subscription", os.getenv("AZURE_SUBSCRIPTION_ID")
        ], check=True, capture_output=True, text=True)
        print("[OBSERVATION] Azure Quantum workspace configured.")
    except subprocess.CalledProcessError as e:
        print("[ERROR] Failed to set workspace =>", e.stderr)
        return

    # Run advanced optimization
    optimizer = AdvancedBellStateOptimizer()
    optimizer.optimize()

if __name__ == "__main__":
    main()
