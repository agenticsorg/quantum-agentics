import pytest
from pathlib import Path
import json
import torch
from ..tools.trainer import QuantumTrainer

@pytest.fixture
def trainer():
    return QuantumTrainer(verbose=True)

@pytest.fixture
def sample_data(tmp_path):
    """Create sample data for testing."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    
    # Create sample training data
    train_data = [
        {"prompt": "Test prompt 1", "response": "Test response 1"},
        {"prompt": "Test prompt 2", "response": "Test response 2"}
    ]
    with open(data_dir / "train.json", "w") as f:
        json.dump(train_data, f)
    
    # Create sample evaluation data
    eval_data = [
        {"prompt": "Eval prompt 1", "response": "Eval response 1"}
    ]
    with open(data_dir / "eval.json", "w") as f:
        json.dump(eval_data, f)
    
    # Create sample quantum problems
    quantum_problems = [
        {
            "problem_id": "test_qubo_1",
            "size": 2,
            "matrix": [[1.0, 0.5], [0.5, 1.0]],
            "description": "Test QUBO problem"
        }
    ]
    with open(data_dir / "quantum_problems.json", "w") as f:
        json.dump(quantum_problems, f)
    
    return data_dir

def test_trainer_initialization():
    """Test trainer initialization with different devices."""
    # Test CPU initialization
    trainer_cpu = QuantumTrainer(device="cpu")
    assert trainer_cpu.device == "cpu"
    
    # Test CUDA initialization if available
    if torch.cuda.is_available():
        trainer_cuda = QuantumTrainer(device="cuda")
        assert trainer_cuda.device == "cuda"
    else:
        trainer_auto = QuantumTrainer()  # Should default to CPU
        assert trainer_auto.device == "cpu"

def test_data_loading(trainer, sample_data):
    """Test loading of training data."""
    trainer.load_data(str(sample_data))
    
    # Verify training data was loaded
    assert hasattr(trainer, 'train_data')
    assert len(trainer.train_data) == 2
    assert trainer.train_data[0]["prompt"] == "Test prompt 1"
    
    # Verify evaluation data was loaded
    assert hasattr(trainer, 'eval_data')
    assert len(trainer.eval_data) == 1
    assert trainer.eval_data[0]["prompt"] == "Eval prompt 1"
    
    # Verify quantum problems were loaded
    assert hasattr(trainer, 'quantum_problems')
    assert len(trainer.quantum_problems) == 1
    assert trainer.quantum_problems[0]["problem_id"] == "test_qubo_1"

def test_setup_configuration(trainer):
    """Test training setup with configuration."""
    config = {
        "model_config": {
            "model_name": "phi-4",
            "quantization": "4bit"
        },
        "training_config": {
            "batch_size": 32,
            "learning_rate": 2e-4
        },
        "quantum_config": {
            "optimization_frequency": 100
        }
    }
    
    # Setup should not raise any errors
    trainer.setup(config)
    
    # Verify logging output
    assert trainer.model_name == "phi-4"

def test_save_and_load_model(trainer, tmp_path):
    """Test model saving and loading."""
    save_dir = tmp_path / "model_save"
    
    # Test save_model
    trainer.save_model(str(save_dir))
    assert save_dir.exists()
    
    # Test load_model
    trainer.load_model(str(save_dir))
    # Future: Add assertions for model state

def test_training_parameters(trainer):
    """Test training with different parameters."""
    # Training should not raise errors even though implementation is pending
    trainer.train(
        num_epochs=3,
        batch_size=16,
        learning_rate=1e-4,
        save_dir="test_save"
    )

def test_evaluation(trainer):
    """Test model evaluation."""
    # Evaluation should not raise errors
    trainer.evaluate()
    # Future: Add assertions for evaluation metrics

def test_error_handling(trainer):
    """Test error handling for invalid inputs."""
    # Test loading non-existent data
    with pytest.raises(FileNotFoundError):
        trainer.load_data("nonexistent_directory")
    
    # Test loading invalid model
    with pytest.raises(Exception):
        trainer.load_model("nonexistent_model")

if __name__ == "__main__":
    pytest.main([__file__])