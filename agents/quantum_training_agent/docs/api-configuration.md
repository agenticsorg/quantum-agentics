# Configuration API

This document details the configuration API for the Quantum Training Agent, including all available settings and their usage.

## Configuration Classes

### 1. Training Configuration

```python
class TrainingConfig:
    """Configuration for training parameters and settings."""
    
    def __init__(
        self,
        model_name: str = "phi-4",
        batch_size: int = 32,
        learning_rate: float = 2e-4,
        num_epochs: int = 10,
        optimization_frequency: int = 100,
        **kwargs
    ):
        """
        Args:
            model_name: Name of the model to train
            batch_size: Training batch size
            learning_rate: Learning rate for optimization
            num_epochs: Number of training epochs
            optimization_frequency: Steps between quantum optimizations
        """
        self.validate_params()
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "model_name": self.model_name,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "num_epochs": self.num_epochs,
            "optimization_frequency": self.optimization_frequency
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'TrainingConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
```

### 2. Model Configuration

```python
class ModelConfig:
    """Configuration for model architecture and parameters."""
    
    def __init__(
        self,
        model_type: str = "language_model",
        quantization: str = "4bit",
        lora_config: dict = None,
        **kwargs
    ):
        """
        Args:
            model_type: Type of model architecture
            quantization: Quantization strategy
            lora_config: LoRA adapter configuration
        """
        self.lora_config = lora_config or {
            "r": 8,
            "alpha": 32,
            "dropout": 0.1
        }
        self.validate_config()
    
    def get_model_args(self) -> dict:
        """Get model initialization arguments."""
        return {
            "model_type": self.model_type,
            "quantization": self.quantization,
            "lora_config": self.lora_config
        }
```

### 3. Quantum Configuration

```python
class QuantumConfig:
    """Configuration for quantum optimization settings."""
    
    def __init__(
        self,
        workspace: str = "azure-quantum",
        solver: str = "parallel-tempering",
        qubo_size_limit: int = 1000,
        **kwargs
    ):
        """
        Args:
            workspace: Quantum workspace identifier
            solver: Quantum solver type
            qubo_size_limit: Maximum QUBO problem size
        """
        self.validate_quantum_settings()
    
    def get_solver_config(self) -> dict:
        """Get quantum solver configuration."""
        return {
            "workspace": self.workspace,
            "solver": self.solver,
            "parameters": {
                "qubo_size_limit": self.qubo_size_limit
            }
        }
```

## Configuration Management

### 1. Configuration Loading

```python
class ConfigLoader:
    """Load and validate configuration from various sources."""
    
    @staticmethod
    def from_yaml(path: str) -> dict:
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    
    @staticmethod
    def from_json(path: str) -> dict:
        """Load configuration from JSON file."""
        with open(path, 'r') as f:
            config = json.load(f)
        return config
    
    @classmethod
    def load_config(cls, path: str) -> dict:
        """Load configuration from file based on extension."""
        if path.endswith('.yaml') or path.endswith('.yml'):
            return cls.from_yaml(path)
        elif path.endswith('.json'):
            return cls.from_json(path)
        else:
            raise ValueError("Unsupported configuration format")
```

### 2. Configuration Validation

```python
class ConfigValidator:
    """Validate configuration settings and parameters."""
    
    @staticmethod
    def validate_training_config(config: dict) -> bool:
        """
        Validate training configuration.
        
        Checks:
        1. Required fields present
        2. Parameter types correct
        3. Value ranges valid
        """
        required_fields = [
            "model_name",
            "batch_size",
            "learning_rate",
            "num_epochs"
        ]
        return all(field in config for field in required_fields)
    
    @staticmethod
    def validate_model_config(config: dict) -> bool:
        """
        Validate model configuration.
        
        Checks:
        1. Model type supported
        2. Quantization valid
        3. LoRA parameters valid
        """
        valid_model_types = ["language_model", "classifier"]
        valid_quantization = ["4bit", "8bit", "none"]
        return (
            config["model_type"] in valid_model_types and
            config["quantization"] in valid_quantization
        )
```

## Configuration Examples

### 1. Basic Configuration

```yaml
training:
  model_name: phi-4
  batch_size: 32
  learning_rate: 2e-4
  num_epochs: 10
  optimization_frequency: 100

model:
  model_type: language_model
  quantization: 4bit
  lora_config:
    r: 8
    alpha: 32
    dropout: 0.1

quantum:
  workspace: azure-quantum
  solver: parallel-tempering
  qubo_size_limit: 1000
```

### 2. Advanced Configuration

```yaml
training:
  model_name: phi-4
  batch_size: 32
  learning_rate: 2e-4
  num_epochs: 10
  optimization_frequency: 100
  gradient_checkpointing: true
  mixed_precision: true
  warmup_steps: 100

model:
  model_type: language_model
  quantization: 4bit
  lora_config:
    r: 8
    alpha: 32
    dropout: 0.1
  model_parallel: false
  attention_config:
    head_dim: 64
    num_heads: 12

quantum:
  workspace: azure-quantum
  solver: parallel-tempering
  qubo_size_limit: 1000
  optimization_params:
    timeout: 300
    max_iterations: 1000
    tolerance: 1e-6
  fallback_solver: quantum-inspired
```

## Usage Examples

### 1. Loading Configuration

```python
# Load from file
config = ConfigLoader.load_config("config.yaml")
training_config = TrainingConfig.from_dict(config["training"])
model_config = ModelConfig.from_dict(config["model"])
quantum_config = QuantumConfig.from_dict(config["quantum"])

# Create programmatically
training_config = TrainingConfig(
    model_name="phi-4",
    batch_size=32,
    learning_rate=2e-4,
    num_epochs=10
)
```

### 2. Validating Configuration

```python
# Validate configuration
validator = ConfigValidator()
if validator.validate_training_config(config["training"]):
    print("Training configuration valid")
if validator.validate_model_config(config["model"]):
    print("Model configuration valid")
```

## Related Documentation
- [Training Infrastructure](training-infrastructure.md)
- [Quantum Optimization](quantum-optimization.md)
- [System Architecture](architecture.md)
