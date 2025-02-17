# Quick Start Tutorial

This tutorial will get you started with the Quantum Training Agent, demonstrating basic usage and key features.

## Prerequisites

Ensure you have:
- Completed the [Installation Guide](installation.md)
- Set up Azure Quantum access
- Configured environment variables

## Basic Usage

### 1. Interactive Mode

The simplest way to start is with interactive mode:

```bash
python main.py
```

This launches the CLI interface where you can:
- Analyze training requirements
- Execute model training
- Run quantum optimization
- Evaluate results
- Analyze process

### 2. Automated Training

For automated training with default settings:

```bash
python main.py --auto --task train --model phi-4 --output_dir outputs
```

This will:
1. Load the Phi-4 model
2. Initialize quantum-enhanced training
3. Execute the training pipeline
4. Save results to the outputs directory

### 3. Test Mode

To verify everything is working:

```bash
python main.py --test --verbose
```

This runs a test pipeline with sample data.

## Configuration

### Basic Configuration

Minimal configuration in YAML:

```yaml
model:
  name: phi-4
  quantization: 4bit
  lora_config:
    r: 8
    alpha: 32
    dropout: 0.1

training:
  batch_size: 32
  learning_rate: 2e-4
  num_epochs: 10
  optimization_frequency: 100

quantum:
  workspace: azure-quantum
  solver: parallel-tempering
  qubo_size_limit: 1000
```

### Command Line Options

Common parameters:

```bash
# Training parameters
--batch_size 32
--learning_rate 2e-4
--num_epochs 10

# Quantum parameters
--optimization_frequency 100
--qubo_size_limit 1000

# Azure parameters
--azure_subscription_id <id>
--azure_resource_group <group>
--azure_workspace <workspace>
```

## Example Workflow

### 1. Prepare Training Data

Place your training data in a directory:

```
quantum_data/
├── train.json
├── eval.json
└── test.json
```

### 2. Start Training

```bash
python main.py --auto \
  --task train \
  --model phi-4 \
  --data_dir quantum_data \
  --output_dir outputs \
  --batch_size 32 \
  --learning_rate 2e-4 \
  --num_epochs 10
```

### 3. Monitor Progress

The system will display:
- Training progress
- Quantum optimization steps
- Evaluation metrics
- Resource utilization

### 4. View Results

Results are saved to the output directory:
- Model checkpoints
- Training logs
- Evaluation metrics
- Visualization data

## Next Steps

1. Explore [Basic Concepts](basic-concepts.md)
2. Learn about [Training Infrastructure](training-infrastructure.md)
3. Study [Quantum Optimization Methods](quantum-optimization.md)
4. Review [Advanced Training Techniques](training-advanced.md)

## Common Operations

### Fine-tune a Model

```bash
python main.py --auto \
  --task train \
  --model phi-4 \
  --data_dir custom_data \
  --output_dir outputs \
  --learning_rate 1e-5 \
  --num_epochs 5
```

### Evaluate Results

```bash
python main.py --task evaluate \
  --model outputs/final_model \
  --test_data quantum_data/test.json
```

### Run Optimization

```bash
python main.py --task optimize \
  --model outputs/checkpoint \
  --optimization_frequency 50
```

## Troubleshooting

### Common Issues

1. Memory Errors
   - Reduce batch size
   - Enable quantization
   - Use LoRA/QLoRA

2. Quantum Solver Errors
   - Verify Azure Quantum access
   - Check QUBO size limits
   - Review solver compatibility

3. Training Instability
   - Adjust learning rate
   - Modify optimization frequency
   - Check gradient clipping

### Getting Help

If you encounter issues:
1. Check logs in outputs directory
2. Review [Troubleshooting Guide](troubleshooting.md)
3. Open a GitHub issue

## Tips & Best Practices

1. Start Small
   - Use test mode first
   - Experiment with small datasets
   - Gradually increase complexity

2. Monitor Resources
   - Watch GPU memory usage
   - Track quantum solver quotas
   - Monitor training metrics

3. Save Checkpoints
   - Enable regular checkpointing
   - Keep best performing models
   - Maintain evaluation logs

## What's Next

After completing this quick start:
1. Explore advanced features
2. Read the architecture documentation
3. Try different quantum solvers
4. Experiment with hyperparameters

For more detailed information, refer to:
- [Training Guide](training-basic.md)
- [Quantum Integration](quantum-solver.md)
- [Advanced Topics](phd-analysis.md)