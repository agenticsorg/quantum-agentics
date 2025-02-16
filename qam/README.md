# Quantum Agent Manager (QAM)

## Overview
QAM is a cutting-edge quantum-inspired task scheduling and agent orchestration system that leverages Azure Quantum's capabilities for optimizing multi-agent operations. By utilizing quantum computing principles, QAM can efficiently solve complex scheduling problems that would be computationally intensive for classical approaches.

## Features

### Core Capabilities
- **Quantum-Optimized Scheduling**: Utilizes Azure Quantum for solving QUBO-based scheduling problems
- **Hierarchical Cluster Management**: Organizes agents into optimized clusters for efficient task distribution
- **Resource-Aware Optimization**: Considers resource requirements and constraints in optimization decisions
- **Quantum ReACT Integration**: Quantum-enhanced reasoning for agent decision making
- **Automatic Fallback Mechanisms**: Graceful degradation to classical methods when quantum resources are unavailable

### Advanced Features
- **Parallel Quantum Job Processing**: Submit multiple optimization jobs simultaneously
- **Dynamic Resource Balancing**: Automatically adjusts cluster sizes based on workload
- **Quantum Circuit Execution**: Direct quantum circuit implementation for specific optimization tasks
- **Hybrid Optimization**: Combines classical and quantum approaches for optimal performance

## Benefits
- **Superior Task Distribution**: Quantum optimization finds better solutions than classical methods
- **Scalable Architecture**: Handles growing agent populations efficiently
- **Resource Efficiency**: Optimizes resource utilization across agent clusters
- **Future-Proof Design**: Ready for next-generation quantum hardware
- **Robust Error Handling**: Comprehensive fallback mechanisms ensure system reliability

## Installation

### Prerequisites
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verify installation
az --version

# Add quantum extension
az extension add -n quantum

# Login to Azure
az login --use-device-code
```

### Package Installation
```bash
pip install -r requirements.txt
```

### Azure Quantum Setup
```python
from qam.azure_quantum import AzureQuantumConfig, AzureQuantumClient

# Configure workspace
config = AzureQuantumConfig(
    resource_group="your-resource-group",
    workspace_name="your-workspace",
    location="your-location",
    subscription_id="your-subscription-id"  # Optional
)

# Initialize client
client = AzureQuantumClient(config)
```

## Basic Usage

### Creating and Managing Clusters
```python
from qam.cluster_management import ClusterManager

# Initialize manager
manager = ClusterManager()

# Create clusters
cluster1 = manager.create_cluster()
cluster2 = manager.create_cluster()

# Add agents
cluster1.add_agent("agent1")
cluster1.add_agent("agent2")

# Update resource requirements
cluster1.update_resource_requirements({
    "cpu": 2.0,
    "memory": 4.0
})

# Optimize cluster structure
assignments = manager.optimize_cluster_structure()
```

### Quantum-Enhanced Scheduling
```python
from qam.scheduler import QUBOScheduler
from qam.quantum_reasoning import QuantumReasoningState

# Initialize scheduler
scheduler = QUBOScheduler()

# Create quantum reasoning state
state = QuantumReasoningState()

# Define scheduling problem
horizon = 10
result = scheduler.optimize_schedule_with_reasoning(
    tasks=[...],  # Your tasks here
    horizon=horizon,
    reasoning_state=state
)
```

## Advanced Usage

### Custom Optimization Parameters
```python
# Configure QUBO parameters
scheduler.base_weights = {
    "time_penalty": 1.0,
    "resource_penalty": 2.0,
    "dependency_penalty": 3.0
}

# Set quantum circuit parameters
scheduler.quantum_parameters = {
    "shots": 1000,
    "optimization_level": 2
}
```

### Parallel Optimization
```python
from qam.enhanced_scheduler import EnhancedQUBOScheduler

# Initialize enhanced scheduler
scheduler = EnhancedQUBOScheduler()

# Configure parallel jobs
scheduler.max_parallel_jobs = 4

# Run hierarchical optimization
levels = scheduler.build_hierarchical_qubo(
    tasks=[...],
    clusters={...},
    max_cluster_size=100
)
```

### Custom Quantum Circuits
```python
# Define custom quantum circuit
circuit = {
    "input_qubits": 2,
    "operations": [
        {"gate": "h", "targets": [0]},
        {"gate": "cnot", "controls": [0], "targets": [1]}
    ]
}

# Submit custom circuit
job_id = client.submit_qubo(circuit)
result = client.wait_for_job(job_id)
```

## Configuration

### Environment Variables
```bash
# Azure Quantum Configuration
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_QUANTUM_WORKSPACE="your-workspace-name"
export AZURE_QUANTUM_LOCATION="your-location"
```

### Optimization Parameters
```python
# Cluster optimization
manager.optimization_parameters = {
    "target_cluster_size": 50,
    "split_threshold": 100,
    "merge_threshold": 20
}

# QUBO parameters
scheduler.optimization_parameters = {
    "timeout": 100,
    "beta_start": 0.1,
    "beta_stop": 1.0,
    "sweeps": 1000
}
```

## Performance Tuning

### Resource Optimization
- Set appropriate cluster size thresholds based on workload
- Adjust penalty weights for different optimization criteria
- Configure parallel job limits based on available quantum resources

### Quantum Circuit Optimization
- Use appropriate number of qubits for problem size
- Adjust circuit depth based on quantum hardware capabilities
- Balance between quantum and classical processing

## Error Handling

### Quantum Resource Unavailability
```python
try:
    result = scheduler.optimize_schedule_with_reasoning(...)
except Exception as e:
    # Fallback to classical optimization
    result = scheduler._classical_optimization()
```

### Circuit Execution Errors
```python
try:
    job_id = client.submit_qubo(problem)
    result = client.wait_for_job(job_id)
except Exception as e:
    print(f"Quantum job failed: {e}")
    # Implement fallback strategy
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License - see LICENSE file for details