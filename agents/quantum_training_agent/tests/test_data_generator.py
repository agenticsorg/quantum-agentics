import pytest
import json
from pathlib import Path
import numpy as np
from ..tools.data_generator import SampleDataGenerator

@pytest.fixture
def data_generator():
    return SampleDataGenerator(seed=42)

@pytest.fixture
def temp_output_dir(tmp_path):
    return tmp_path / "test_data"

def test_text_sample_generation(data_generator):
    """Test generation of text samples"""
    num_samples = 50
    samples = data_generator.generate_text_samples(num_samples)
    
    assert len(samples) == num_samples
    for sample in samples:
        assert "prompt" in sample
        assert "response" in sample
        assert isinstance(sample["prompt"], str)
        assert isinstance(sample["response"], str)
        assert len(sample["prompt"]) > 0
        assert len(sample["response"]) > 0

def test_quantum_optimization_problems(data_generator):
    """Test generation of quantum optimization problems"""
    num_problems = 5
    max_size = 50
    problems = data_generator.generate_quantum_optimization_problems(
        num_problems=num_problems,
        max_size=max_size
    )
    
    assert len(problems) == num_problems
    for problem in problems:
        assert "problem_id" in problem
        assert "size" in problem
        assert "matrix" in problem
        assert "description" in problem
        
        # Check matrix properties
        matrix = np.array(problem["matrix"])
        assert matrix.shape[0] == matrix.shape[1]  # Square matrix
        assert matrix.shape[0] <= max_size
        assert np.allclose(matrix, matrix.T)  # Symmetric matrix
        
def test_save_training_data(data_generator, temp_output_dir):
    """Test saving of training data to files"""
    num_train = 100
    num_eval = 20
    num_test = 20
    
    data_generator.save_training_data(
        output_dir=str(temp_output_dir),
        num_train=num_train,
        num_eval=num_eval,
        num_test=num_test
    )
    
    # Check if files were created
    assert (temp_output_dir / "train.json").exists()
    assert (temp_output_dir / "eval.json").exists()
    assert (temp_output_dir / "test.json").exists()
    assert (temp_output_dir / "quantum_problems.json").exists()
    
    # Verify file contents
    with open(temp_output_dir / "train.json", "r") as f:
        train_data = json.load(f)
        assert len(train_data) == num_train
        
    with open(temp_output_dir / "eval.json", "r") as f:
        eval_data = json.load(f)
        assert len(eval_data) == num_eval
        
    with open(temp_output_dir / "test.json", "r") as f:
        test_data = json.load(f)
        assert len(test_data) == num_test
        
    with open(temp_output_dir / "quantum_problems.json", "r") as f:
        quantum_data = json.load(f)
        assert len(quantum_data) == 10  # Default number of quantum problems

def test_generate_sample_dataset(data_generator, temp_output_dir):
    """Test generation of complete sample dataset"""
    data_generator.generate_sample_dataset(output_dir=str(temp_output_dir))
    
    # Verify directory structure and files
    assert temp_output_dir.exists()
    assert (temp_output_dir / "train.json").exists()
    assert (temp_output_dir / "eval.json").exists()
    assert (temp_output_dir / "test.json").exists()
    assert (temp_output_dir / "quantum_problems.json").exists()
    
    # Verify sample sizes
    with open(temp_output_dir / "train.json", "r") as f:
        train_data = json.load(f)
        assert len(train_data) == 100  # Default training size
        
    with open(temp_output_dir / "eval.json", "r") as f:
        eval_data = json.load(f)
        assert len(eval_data) == 20  # Default eval size

def test_reproducibility(temp_output_dir):
    """Test that data generation is reproducible with same seed"""
    generator1 = SampleDataGenerator(seed=42)
    generator2 = SampleDataGenerator(seed=42)
    
    samples1 = generator1.generate_text_samples(num_samples=50)
    samples2 = generator2.generate_text_samples(num_samples=50)
    
    assert samples1 == samples2
    
    problems1 = generator1.generate_quantum_optimization_problems(num_problems=5)
    problems2 = generator2.generate_quantum_optimization_problems(num_problems=5)
    
    # Compare problem matrices
    for p1, p2 in zip(problems1, problems2):
        assert np.array_equal(np.array(p1["matrix"]), np.array(p2["matrix"]))

def test_different_seeds():
    """Test that different seeds produce different data"""
    generator1 = SampleDataGenerator(seed=42)
    generator2 = SampleDataGenerator(seed=43)
    
    samples1 = generator1.generate_text_samples(num_samples=50)
    samples2 = generator2.generate_text_samples(num_samples=50)
    
    assert samples1 != samples2

def test_invalid_inputs():
    """Test handling of invalid inputs"""
    generator = SampleDataGenerator()
    
    # Test negative number of samples
    with pytest.raises(ValueError):
        generator.generate_text_samples(num_samples=-1)
    
    # Test invalid max_size
    with pytest.raises(ValueError):
        generator.generate_quantum_optimization_problems(max_size=0)
    
    # Test invalid output directory
    with pytest.raises(ValueError):
        generator.save_training_data("", num_train=-1)
        
    # Test negative seed
    with pytest.raises(ValueError):
        SampleDataGenerator(seed=-1)

if __name__ == "__main__":
    pytest.main([__file__])