import pytest
from pathlib import Path
import tempfile
import yaml
from ..config.training_config import (
    QuantumTrainingConfig,
    ModelConfig,
    QuantumConfig,
    TrainingConfig,
    DataConfig
)

@pytest.fixture
def sample_config_dict():
    return {
        'model': {
            'model_name': 'phi-4',
            'quantization': '4bit',
            'max_length': 2048,
            'device': 'cuda',
            'lora_r': 8,
            'lora_alpha': 32,
            'lora_dropout': 0.1,
            'target_modules': ['q_proj', 'v_proj'],
            'use_gradient_checkpointing': True,
            'torch_dtype': 'float16'
        },
        'quantum': {
            'solver_type': 'quantum_annealing',
            'optimization_frequency': 100,
            'qubo_size_limit': 1000,
            'azure_subscription_id': 'test-subscription',
            'azure_resource_group': 'test-resource-group',
            'azure_workspace_name': 'test-workspace',
            'timeout_seconds': 300,
            'max_iterations': 1000,
            'convergence_threshold': 1e-6
        },
        'training': {
            'batch_size': 32,
            'learning_rate': 2e-4,
            'num_epochs': 10,
            'warmup_steps': 100,
            'weight_decay': 0.01,
            'gradient_clip': 1.0,
            'eval_steps': 100,
            'save_steps': 500,
            'logging_steps': 10
        },
        'data': {
            'train_path': 'data/train',
            'eval_path': 'data/eval',
            'test_path': 'data/test',
            'max_samples': 1000,
            'validation_split': 0.1,
            'test_split': 0.1,
            'shuffle_seed': 42
        },
        'output_dir': 'test_outputs',
        'experiment_name': 'test_experiment'
    }

@pytest.fixture
def sample_config_file(sample_config_dict, tmp_path):
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config_dict, f)
    return config_file

def test_default_config_creation():
    """Test creation of config with default values"""
    config = QuantumTrainingConfig()
    assert config.model.model_name == "phi-4"
    assert config.quantum.solver_type == "quantum_annealing"
    assert config.training.batch_size == 32
    assert config.data.validation_split == 0.1

def test_config_from_dict(sample_config_dict):
    """Test creation of config from dictionary"""
    config = QuantumTrainingConfig(
        model=ModelConfig(**sample_config_dict['model']),
        quantum=QuantumConfig(**sample_config_dict['quantum']),
        training=TrainingConfig(**sample_config_dict['training']),
        data=DataConfig(**sample_config_dict['data']),
        output_dir=sample_config_dict['output_dir'],
        experiment_name=sample_config_dict['experiment_name']
    )
    
    assert config.model.model_name == "phi-4"
    assert config.quantum.azure_subscription_id == "test-subscription"
    assert config.training.batch_size == 32
    assert config.data.train_path == "data/train"
    assert config.output_dir == "test_outputs"

def test_config_from_yaml(sample_config_file):
    """Test loading config from YAML file"""
    config = QuantumTrainingConfig.from_yaml(sample_config_file)
    
    assert config.model.model_name == "phi-4"
    assert config.quantum.solver_type == "quantum_annealing"
    assert config.training.batch_size == 32
    assert config.data.train_path == "data/train"

def test_config_to_yaml(sample_config_dict, tmp_path):
    """Test saving config to YAML file"""
    config = QuantumTrainingConfig(
        model=ModelConfig(**sample_config_dict['model']),
        quantum=QuantumConfig(**sample_config_dict['quantum']),
        training=TrainingConfig(**sample_config_dict['training']),
        data=DataConfig(**sample_config_dict['data']),
        output_dir=sample_config_dict['output_dir'],
        experiment_name=sample_config_dict['experiment_name']
    )
    
    output_file = tmp_path / "output_config.yaml"
    config.to_yaml(output_file)
    
    # Load and verify
    loaded_config = QuantumTrainingConfig.from_yaml(output_file)
    assert loaded_config.model.model_name == config.model.model_name
    assert loaded_config.quantum.solver_type == config.quantum.solver_type
    assert loaded_config.training.batch_size == config.training.batch_size

def test_config_validation():
    """Test configuration validation"""
    invalid_config = QuantumTrainingConfig(
        training=TrainingConfig(batch_size=-1, learning_rate=-0.1),
        data=DataConfig(validation_split=0.6, test_split=0.5)
    )
    
    errors = invalid_config.validate()
    assert len(errors) >= 3  # Should have multiple validation errors
    assert any("Batch size must be positive" in error for error in errors)
    assert any("Learning rate must be positive" in error for error in errors)
    assert any("Validation and test split must sum to less than 1.0" in error for error in errors)

def test_optimizer_params():
    """Test optimizer parameters generation"""
    config = QuantumTrainingConfig()
    params = config.get_optimizer_params()
    
    assert params["lr"] == config.training.learning_rate
    assert params["weight_decay"] == config.training.weight_decay
    assert params["betas"] == (0.9, 0.999)
    assert params["eps"] == 1e-8

def test_scheduler_params():
    """Test scheduler parameters generation"""
    config = QuantumTrainingConfig()
    params = config.get_scheduler_params()
    
    assert params["num_warmup_steps"] == config.training.warmup_steps
    assert "num_training_steps" in params

@pytest.mark.skipif(not QuantumTrainingConfig._is_cuda_available(),
                   reason="CUDA not available")
def test_cuda_validation():
    """Test CUDA validation when available"""
    config = QuantumTrainingConfig(
        model=ModelConfig(device="cuda")
    )
    errors = config.validate()
    assert not any("CUDA device specified but not available" in error for error in errors)

def test_file_not_found():
    """Test handling of non-existent config file"""
    with pytest.raises(FileNotFoundError):
        QuantumTrainingConfig.from_yaml("nonexistent_config.yaml")

def test_invalid_yaml(tmp_path):
    """Test handling of invalid YAML file"""
    invalid_yaml = tmp_path / "invalid.yaml"
    with open(invalid_yaml, 'w') as f:
        f.write("invalid: yaml: content: [}")
    
    with pytest.raises(yaml.YAMLError):
        QuantumTrainingConfig.from_yaml(invalid_yaml)