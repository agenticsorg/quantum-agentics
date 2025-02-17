# Installation Guide

This guide walks you through the process of setting up the Quantum Training Agent and its dependencies.

## Prerequisites

### System Requirements

- Python ≥ 3.9
- CUDA-capable GPU (recommended for training)
- 16GB RAM minimum (32GB recommended)
- 100GB disk space for model storage

### Cloud Requirements

- Azure account with Quantum workspace access
- OpenRouter API key for LLM integration
- Sufficient quota for GPU instances (if using cloud training)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/username/quantum_training_agent.git
cd quantum_training_agent
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -e .  # Install package in editable mode
# or
pip install -r requirements.txt  # Install just the requirements
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
OPENROUTER_API_KEY=your_api_key_here
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_RESOURCE_GROUP=your_resource_group
AZURE_WORKSPACE_NAME=your_workspace_name
```

### 5. Azure Quantum Setup

1. Create an Azure Quantum workspace in the Azure portal
2. Note down the workspace details:
   - Subscription ID
   - Resource group
   - Workspace name
   - Location

3. Configure Azure CLI (if using):
```bash
az login
az quantum workspace set -g your-resource-group -w your-workspace-name -l your-location -s your-subscription-id
```

## Verification

Run the test suite to verify the installation:

```bash
pytest tests/
```

Run a simple test job:

```bash
python main.py --test
```

## Package Dependencies

Key dependencies installed automatically:

```plaintext
torch>=2.1.0
transformers>=4.36.0
unsloth>=0.3.0
azure-quantum>=1.0.0
peft>=0.7.0
accelerate>=0.25.0
bitsandbytes>=0.41.0
```

## Common Issues

### CUDA Installation

If you encounter CUDA-related issues:
1. Ensure NVIDIA drivers are up to date
2. Verify CUDA toolkit version matches PyTorch requirements
3. Run `nvidia-smi` to confirm GPU is recognized

### Azure Quantum Access

If you can't access Azure Quantum:
1. Verify subscription status
2. Check resource provider registration
3. Ensure proper role assignments (Contributor or Owner)

### Memory Issues

If you encounter memory errors:
1. Reduce batch size
2. Enable gradient checkpointing
3. Use parameter-efficient fine-tuning (LoRA/QLoRA)

## Next Steps

After installation:
1. Complete the [Quick Start Tutorial](quickstart.md)
2. Review the [Basic Concepts](basic-concepts.md)
3. Set up your first training job

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade quantum_training_agent
```

Or for development version:

```bash
git pull origin main
pip install -e .
```

## Uninstallation

To remove the package:

```bash
pip uninstall quantum_training_agent
```

For complete removal, including virtual environment:
```bash
deactivate  # Exit virtual environment
rm -rf venv/  # Remove virtual environment
```

## Support

For installation support:
1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Review GitHub Issues
3. Open a new issue with:
   - System information
   - Error messages
   - Steps to reproduce