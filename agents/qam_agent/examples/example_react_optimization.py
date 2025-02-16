#!/usr/bin/env python3
import sys
import os
import time

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, project_root)

from agents.qam_agent.agent import QAMAgent

def run_react_optimization():
    # Configuration with optimization settings
    sample_config = {
        "agent_name": "ReACTOptimizationAgent",
        "mode": "test",  # Use test mode for verbose output
        "settings": {
            "qaoa_p_steps": 3,
            "qaoa_learning_rate": 0.05,
            "optimization_target": 0.95,  # Target solution quality
            "max_iterations": 5  # Maximum optimization attempts
        }
    }
    
    # Create agent instance
    agent = QAMAgent(sample_config)
    
    # Define optimization task with ReACT prompts
    optimization_task = """
    Optimize a QUBO problem for quantum circuit scheduling with the following objectives:
    1. Minimize total execution time
    2. Maximize resource utilization
    3. Respect task dependencies
    4. Achieve solution quality above 0.95
    
    Use ReACT methodology to:
    1. Analyze the problem structure
    2. Formulate QUBO representation
    3. Optimize using QAOA
    4. Evaluate results and adjust parameters
    5. Repeat until target quality is reached
    """
    
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                 ReACT Quantum Optimization Agent                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
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
    run_react_optimization()
