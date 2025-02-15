# QAM Quick Start Guide

## Overview
The Quantum Agent Manager (QAM) is a powerful framework for quantum-inspired task scheduling and agent orchestration. It leverages quantum optimization techniques through Azure Quantum's services to solve complex scheduling problems efficiently.

## Key Features
- Quantum-inspired task scheduling
- Multi-agent cluster management
- Resource optimization using QUBO/QAOA
- Quantum reasoning for decision making
- Hierarchical optimization for large-scale problems

## Installation

### Prerequisites
- Python 3.8+
- Azure Quantum subscription
- Azure CLI with quantum extension

```bash
# Clone the repository
git clone https://github.com/example/qam
cd qam

# Install dependencies
pip install -r requirements.txt

# Verify Azure CLI installation
az --version
az extension add -n quantum
```

## Basic Configuration

### Setting up Azure Quantum
The first step is configuring your Azure Quantum workspace. This provides access to quantum optimization solvers.

```python
from qam.azure_quantum import AzureQuantumConfig, AzureQuantumClient

# Configure Azure Quantum workspace
config = AzureQuantumConfig(
    resource_group="quantum-resources",
    workspace_name="qam-production",
    location="eastus"
)

# Initialize client
client = AzureQuantumClient(config)
```

### Environment Variables
Set up required environment variables for authentication:
```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_QUANTUM_WORKSPACE="your-workspace-name"
```

## Your First Quantum-Optimized Schedule

### 1. Define a Simple Scheduling Problem
```python
from qam.scheduler import QUBOScheduler

# Create a simple scheduling problem
qubo = {
    "problem": "ising",
    "terms": [
        {"c": 1, "ids": [0]},      # Weight for task 0
        {"c": -0.5, "ids": [0, 1]}  # Interaction between tasks 0 and 1
    ]
}
```

### 2. Submit and Monitor Job
```python
# Submit to Azure Quantum
job_id = client.submit_qubo(qubo)

# Monitor progress
status = client.get_job_status(job_id)
print(f"Job Status: {status}")

# Wait for results
result = client.wait_for_job(job_id)
print(f"Optimal schedule: {result['solutions'][0]['configuration']}")
```

### Understanding the Results
The result contains:
- `configuration`: Binary array representing task assignments
- `cost`: Energy value of the solution (lower is better)
- `parameters`: Solver parameters used

## Next Steps
- Explore [Basic Usage](BasicUsage.md) for core functionality
- Try the [Tutorials](Tutorials.md) for practical examples
- Learn about [Advanced Features](AdvancedTopics.md)

## Common Issues and Solutions

### Authentication Errors
If you encounter authentication issues:
1. Verify Azure CLI installation
2. Check environment variables
3. Ensure quantum workspace exists

### Job Submission Failures
Common causes:
- Invalid QUBO format
- Workspace quota exceeded
- Network connectivity issues

### Performance Optimization
Tips for better results:
- Start with small problem sizes
- Use appropriate solver types
- Monitor quantum credits usage

[Next: Basic Usage →](BasicUsage.md)
