from dataclasses import dataclass, field
from typing import Dict, Optional, List, Union
import yaml
from pathlib import Path

@dataclass
class ModelConfig:
    model_name: str = "phi-4"
    quantization: str = "4bit"  # 4bit, 8bit, or None
    max_length: int = 2048
    device: str = "cuda"  # cuda or cpu
    lora_r: int = 8
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    use_gradient_checkpointing: bool = True
    torch_dtype: str = "float16"

@dataclass
class QuantumConfig:
    solver_type: str = "quantum_annealing"  # quantum_annealing, qaoa, or hybrid
    optimization_frequency: int = 100  # Steps between quantum optimizations
    qubo_size_limit: int = 1000
    azure_subscription_id: Optional[str] = None
    azure_resource_group: Optional[str] = None
    azure_workspace_name: Optional[str] = None
    timeout_seconds: int = 300
    max_iterations: int = 1000
    convergence_threshold: float = 1e-6

@dataclass
class TrainingConfig:
    batch_size: int = 32
    learning_rate: float = 2e-4
    num_epochs: int = 10
    warmup_steps: int = 100
    weight_decay: float = 0.01
    gradient_clip: float = 1.0
    eval_steps: int = 100
    save_steps: int = 500
    logging_steps: int = 10

@dataclass
class DataConfig:
    train_path: Optional[str] = None
    eval_path: Optional[str] = None
    test_path: Optional[str] = None
    max_samples: Optional[int] = None
    validation_split: float = 0.1
    test_split: float = 0.1
    shuffle_seed: int = 42

@dataclass
class QuantumTrainingConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    quantum: QuantumConfig = field(default_factory=QuantumConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    output_dir: str = "outputs"
    experiment_name: str = "quantum_training"
    
    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> "QuantumTrainingConfig":
        """Load configuration from a YAML file."""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
            
        return cls(
            model=ModelConfig(**config_dict.get('model', {})),
            quantum=QuantumConfig(**config_dict.get('quantum', {})),
            training=TrainingConfig(**config_dict.get('training', {})),
            data=DataConfig(**config_dict.get('data', {})),
            output_dir=config_dict.get('output_dir', 'outputs'),
            experiment_name=config_dict.get('experiment_name', 'quantum_training')
        )
    
    def to_yaml(self, config_path: Union[str, Path]) -> None:
        """Save configuration to a YAML file."""
        config_path = Path(config_path)
        config_dict = {
            'model': {k: v for k, v in self.model.__dict__.items()},
            'quantum': {k: v for k, v in self.quantum.__dict__.items()},
            'training': {k: v for k, v in self.training.__dict__.items()},
            'data': {k: v for k, v in self.data.__dict__.items()},
            'output_dir': self.output_dir,
            'experiment_name': self.experiment_name
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
    
    def validate(self) -> List[str]:
        """Validate the configuration and return a list of validation errors."""
        errors = []
        
        # Model validation
        if self.model.device == "cuda" and not self._is_cuda_available():
            errors.append("CUDA device specified but not available")
            
        # Quantum validation
        if not self.quantum.azure_subscription_id:
            errors.append("Azure subscription ID is required for quantum optimization")
            
        # Training validation
        if self.training.batch_size <= 0:
            errors.append("Batch size must be positive")
        if self.training.learning_rate <= 0:
            errors.append("Learning rate must be positive")
            
        # Data validation
        if not self.data.train_path:
            errors.append("Training data path is required")
        if self.data.validation_split + self.data.test_split >= 1.0:
            errors.append("Validation and test split must sum to less than 1.0")
            
        return errors
    
    @staticmethod
    def _is_cuda_available() -> bool:
        """Check if CUDA is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def get_optimizer_params(self) -> Dict:
        """Get optimizer parameters for training."""
        return {
            "lr": self.training.learning_rate,
            "weight_decay": self.training.weight_decay,
            "betas": (0.9, 0.999),
            "eps": 1e-8
        }
    
    def get_scheduler_params(self) -> Dict:
        """Get learning rate scheduler parameters."""
        return {
            "num_warmup_steps": self.training.warmup_steps,
            "num_training_steps": self.training.num_epochs * 1000  # Placeholder for actual steps
        }