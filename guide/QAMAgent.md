# QAM Agent Guide

## Overview
The QAM Agent is a quantum-enhanced scheduling system that combines ReACT methodology with quantum optimization techniques. It leverages crewai for reasoning and OpenRouter for LLM integration.

## Installation

```bash
cd agents/qam_agent
pip install -e .
```

## Basic Usage

### Command Line Interface
Run the agent with default settings:
```bash
python agent.py --mode test
```

Customize parameters:
```bash
python agent.py \
  --mode test \
  --qaoa_p_steps 3 \
  --qaoa_learning_rate 0.1 \
  --cluster_threshold 100 \
  --optimization_target 0.8
```

### Azure Quantum Integration
To use Azure Quantum backend:
```bash
python agent.py \
  --mode test \
  --azure_resource_group "your-resource-group" \
  --azure_workspace_name "your-workspace" \
  --azure_subscription_id "your-subscription-id" \
  --azure_location "westus"
```

## Configuration

### Task Definition
Tasks are defined as dictionaries with the following structure:
```python
task = {
    "id": "task0",
    "name": "Quantum Circuit Optimization",
    "duration": 3,
    "resources": ["quantum_processor", "memory"],
    "dependencies": []
}
```

### Resource Configuration
Resources are specified with capacity and cost:
```python
resources = {
    "quantum_processor": {
        "capacity": 2,
        "cost_per_unit": 10
    },
    "cpu": {
        "capacity": 4,
        "cost_per_unit": 1
    }
}
```

## Advanced Features

### ReACT Methodology
The agent uses ReACT (Reasoning and Acting) methodology with four components:
1. **Thought**: Analysis phase
2. **Action**: Implementation steps
3. **Observation**: Results tracking
4. **Reflection**: Evaluation phase

### Quantum Optimization
- QAOA parameter optimization
- Resource allocation optimization
- Quantum-classical hybrid scheduling
- Azure Quantum integration for large-scale problems

### Resource Management
- Dynamic resource tracking
- Capacity constraint validation
- Utilization optimization
- Multi-resource scheduling

## API Reference

### QAMAgent Class
```python
from agents.qam_agent.agent import QAMAgent

# Initialize agent
agent = QAMAgent(config={
    "mode": "test",
    "settings": {
        "qaoa_p_steps": 2,
        "qaoa_learning_rate": 0.1
    }
})

# Run agent
decisions = agent.run(
    prompt="Schedule quantum circuit optimization",
    task_type="both"
)
```

### QAMTools Class
```python
from agents.qam_agent.tools.qam_tools import QAMTools

# Initialize tools
tools = QAMTools(config)

# Analyze requirements
analysis = tools.analyze_quantum_requirements(tasks)

# Generate schedule
schedule = tools.optimize_quantum_schedule(tasks, resources)

# Validate solution
validation = tools.validate_quantum_solution(
    schedule['schedule'],
    tasks,
    resources
)
```

## Output Format

### Schedule Output
```json
{
    "schedule": {
        "task0": 0,
        "task1": 1,
        "task2": 2
    },
    "resource_allocation": {
        "quantum_processor": {
            "allocated": 1,
            "available": 1
        }
    },
    "metrics": {
        "objective_value": -3,
        "resource_utilization": {
            "quantum_processor": 0.5
        },
        "quantum_advantage": 1.5
    }
}
```

### Validation Results
```json
{
    "all_tasks_scheduled": true,
    "dependencies_satisfied": true,
    "resources_valid": true
}
```

## Error Handling
The agent provides comprehensive error handling:
- Resource capacity violations
- Dependency constraint violations
- Azure Quantum connection issues
- LLM integration errors

## Best Practices

1. **Resource Configuration**
   - Set realistic resource capacities
   - Consider cost-per-unit for optimization
   - Monitor utilization patterns

2. **Task Definition**
   - Clearly specify dependencies
   - Include all required resources
   - Use meaningful task names

3. **Performance Optimization**
   - Adjust QAOA parameters based on problem size
   - Use clustering for large task sets
   - Monitor quantum advantage metrics

4. **Integration**
   - Test Azure Quantum connectivity
   - Verify OpenRouter API access
   - Monitor LLM response quality

## Troubleshooting

### Common Issues
1. **Resource Conflicts**
   - Check resource capacity settings
   - Verify task resource requirements
   - Review scheduling timeline

2. **Dependency Violations**
   - Validate dependency chains
   - Check for circular dependencies
   - Review task ordering

3. **Performance Issues**
   - Adjust QAOA parameters
   - Enable clustering for large problems
   - Optimize resource allocation

### Debug Mode
Enable verbose output:
```bash
python agent.py --mode test --verbose
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License
MIT License - see LICENSE file for details