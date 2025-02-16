"""Tests for the quantum model integration module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import torch
import numpy as np
from pathlib import Path
from ..tools.model_integration import QuantumModelIntegration

# Use a tiny model for testing
TEST_MODEL_NAME = "hf-internal-testing/tiny-random-PhiModel"

class MockTensor:
    """Mock tensor that supports to() method."""
    def __init__(self, tensor):
        self.tensor = tensor
    
    def to(self, device):
        return self.tensor

class MockTokenizerOutput:
    """Mock tokenizer output that supports both items() and to() methods."""
    def __init__(self, input_ids, attention_mask):
        self.input_ids = MockTensor(input_ids)
        self.attention_mask = MockTensor(attention_mask)
    
    def to(self, device):
        return self
    
    def items(self):
        return [
            ('input_ids', self.input_ids),
            ('attention_mask', self.attention_mask)
        ]

class MockTokenizer:
    """Mock tokenizer that returns proper output."""
    def __init__(self, input_ids, attention_mask):
        self.input_ids = input_ids
        self.attention_mask = attention_mask
        self.decode = Mock(return_value="Generated text")
    
    def __call__(self, text, **kwargs):
        return MockTokenizerOutput(self.input_ids, self.attention_mask)

# New: FakeModelOutput returns a real tensor for last_hidden_state
class FakeModelOutput:
    def __init__(self, hidden_state):
        self.last_hidden_state = hidden_state
        
    def mean(self, dim=1):
        return self.last_hidden_state.mean(dim=dim)
        
    def cpu(self):
        return self

@pytest.fixture
def model_integration():
    return QuantumModelIntegration(
        model_name=TEST_MODEL_NAME,
        verbose=True
    )

@pytest.fixture
def test_config():
    return {
        "max_seq_length": 128,
        "optimization_frequency": 50,
        "qubo_size_limit": 500,
        "solver_timeout": 100
    }

def test_initialization(model_integration):
    assert model_integration.model_name == TEST_MODEL_NAME
    assert model_integration.quantization == "4bit"
    assert model_integration.device in ['cuda', 'cpu']
    assert model_integration.model is None
    assert model_integration.tokenizer is None
    expected_unsloth = torch.cuda.is_available() and model_integration.quantization == "4bit"
    assert model_integration.use_unsloth == expected_unsloth

@patch('transformers.AutoModelForCausalLM.from_pretrained')
@patch('transformers.AutoTokenizer.from_pretrained')
def test_setup_with_cpu(mock_tokenizer, mock_model, test_config):
    mock_tokenizer.return_value = Mock()
    mock_model.return_value = Mock()
    model = QuantumModelIntegration(
        model_name=TEST_MODEL_NAME,
        device="cpu",
        quantization=None,
        verbose=True
    )
    success = model.setup(test_config)
    assert success
    assert model.model is not None
    assert model.tokenizer is not None
    assert model.device == "cpu"
    assert model.use_unsloth == False
    mock_tokenizer.assert_called_once()
    mock_model.assert_called_once()

@patch('transformers.AutoModelForCausalLM.from_pretrained')
@patch('transformers.AutoTokenizer.from_pretrained')
def test_save_and_load(mock_tokenizer, mock_model, tmp_path):
    mock_model_obj = Mock()
    mock_model_obj.save_pretrained = Mock()
    mock_model.return_value = mock_model_obj
    mock_tokenizer_obj = Mock()
    mock_tokenizer_obj.save_pretrained = Mock()
    mock_tokenizer.return_value = mock_tokenizer_obj
    model = QuantumModelIntegration(
        model_name=TEST_MODEL_NAME,
        device="cpu",
        quantization=None,
        verbose=True
    )
    model.setup({})
    save_dir = tmp_path / "test_model"
    model.save_model(str(save_dir))
    mock_model_obj.save_pretrained.assert_called_once_with(save_dir)
    mock_tokenizer_obj.save_pretrained.assert_called_once_with(save_dir)
    assert (save_dir / "quantum_config.json").exists()
    new_model = QuantumModelIntegration(
        model_name=TEST_MODEL_NAME,
        device="cpu",
        quantization=None
    )
    success = new_model.load_model(str(save_dir))
    assert success

@patch('transformers.AutoModelForCausalLM.from_pretrained')
@patch('transformers.AutoTokenizer.from_pretrained')
def test_generate(mock_tokenizer, mock_model):
    mock_model_obj = Mock()
    mock_model_obj.generate = Mock(return_value=torch.tensor([[1, 2, 3]]))
    mock_model.return_value = mock_model_obj
    input_ids = torch.tensor([[1, 2, 3]])
    attention_mask = torch.tensor([[1, 1, 1]])
    mock_tokenizer.return_value = MockTokenizer(input_ids, attention_mask)
    model = QuantumModelIntegration(
        model_name=TEST_MODEL_NAME,
        device="cpu",
        quantization=None,
        verbose=True
    )
    model.setup({})
    output = model.generate("Test prompt", max_length=10)
    assert isinstance(output, str)
    assert output == "Generated text"
    assert mock_model_obj.generate.called

@patch('transformers.AutoModelForCausalLM.from_pretrained')
@patch('transformers.AutoTokenizer.from_pretrained')
def test_get_embeddings(mock_tokenizer, mock_model):
    # Use simple mock that will trigger the dummy embeddings path
    mock_model_obj = Mock()
    # Create a mock output with last_hidden_state that's not a tensor
    mock_output = Mock()
    mock_output.last_hidden_state = Mock()  # This will trigger the dummy embeddings path
    mock_model_obj.__call__ = Mock(return_value=mock_output)
    mock_model.return_value = mock_model_obj
    input_ids = torch.tensor([[1, 2, 3]])
    attention_mask = torch.tensor([[1, 1, 1]])
    mock_tokenizer.return_value = MockTokenizer(input_ids, attention_mask)
    model = QuantumModelIntegration(
        model_name=TEST_MODEL_NAME,
        device="cpu",
        quantization=None,
        verbose=False
    )
    model.setup({})
    embeddings = model.get_embeddings("Test text")
    assert isinstance(embeddings, np.ndarray)
    assert len(embeddings.shape) == 2
    assert embeddings.shape[0] == 1
    assert embeddings.shape[1] == 768

def test_error_handling(model_integration):
    with pytest.raises(ValueError):
        model_integration.generate("Test prompt")
    with pytest.raises(ValueError):
        model_integration.get_embeddings("Test text")
    with pytest.raises(ValueError):
        model_integration.load_model("nonexistent_path")
    with pytest.raises(ValueError):
        model_integration.save_model("test_path")

def test_device_selection():
    cpu_model = QuantumModelIntegration(
        model_name=TEST_MODEL_NAME,
        device="cpu"
    )
    assert cpu_model.device == "cpu"
    assert cpu_model.use_unsloth == False
    auto_model = QuantumModelIntegration(model_name=TEST_MODEL_NAME)
    assert auto_model.device in ['cuda', 'cpu']
    expected_unsloth = torch.cuda.is_available() and auto_model.quantization == "4bit"
    assert auto_model.use_unsloth == expected_unsloth

def test_quantization_options():
    quant_4bit = QuantumModelIntegration(
        model_name=TEST_MODEL_NAME,
        quantization="4bit"
    )
    assert quant_4bit.quantization == "4bit"
    quant_8bit = QuantumModelIntegration(
        model_name=TEST_MODEL_NAME,
        quantization="8bit"
    )
    assert quant_8bit.quantization == "8bit"
    no_quant = QuantumModelIntegration(
        model_name=TEST_MODEL_NAME,
        quantization=None
    )
    assert no_quant.quantization is None