import json
import random
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np

class SampleDataGenerator:
    """Generate sample data for testing the quantum training agent."""
    
    def __init__(self, seed: int = 42):
        """Initialize the data generator with a random seed for reproducibility.
        
        Args:
            seed: Random seed for reproducibility
            
        Raises:
            ValueError: If seed is negative
        """
        if seed < 0:
            raise ValueError("Seed must be non-negative")
            
        self.seed = seed
        # Set both seeds at initialization to ensure consistent state
        self._set_seeds(seed)
        
        # Sample prompts and responses for generating training data
        self.sample_prompts = [
            "Explain quantum computing in simple terms",
            "What is quantum entanglement?",
            "How does quantum tunneling work?",
            "Describe the quantum measurement problem",
            "What are quantum gates?",
            "Explain superposition in quantum mechanics",
            "What is quantum teleportation?",
            "How does quantum cryptography work?",
            "What is quantum supremacy?",
            "Explain quantum error correction"
        ]
        
        self.sample_responses = [
            "Quantum computing uses quantum mechanics to process information in new ways...",
            "Quantum entanglement occurs when particles become correlated in such a way...",
            "Quantum tunneling is a phenomenon where particles can pass through barriers...",
            "The quantum measurement problem deals with the nature of measurement...",
            "Quantum gates are the building blocks of quantum circuits...",
            "Superposition allows quantum systems to exist in multiple states simultaneously...",
            "Quantum teleportation is a process that transmits quantum information...",
            "Quantum cryptography uses principles of quantum mechanics for secure communication...",
            "Quantum supremacy refers to when quantum computers outperform classical ones...",
            "Quantum error correction protects quantum information from decoherence..."
        ]
    
    def _set_seeds(self, seed: int):
        """Set random seeds for both random and numpy."""
        random.seed(seed)
        np.random.seed(seed)
    
    def generate_text_samples(self, num_samples: int = 100) -> List[Dict[str, str]]:
        """Generate text samples for training.
        
        Args:
            num_samples: Number of samples to generate
            
        Returns:
            List of dictionaries containing prompt-response pairs
            
        Raises:
            ValueError: If num_samples is not positive
        """
        if num_samples <= 0:
            raise ValueError("Number of samples must be positive")
        
        # Reset seeds before generation to ensure reproducibility
        self._set_seeds(self.seed)
            
        samples = []
        for _ in range(num_samples):
            idx = random.randint(0, len(self.sample_prompts) - 1)
            sample = {
                "prompt": self.sample_prompts[idx],
                "response": self.sample_responses[idx]
            }
            samples.append(sample)
        return samples
    
    def generate_quantum_optimization_problems(self, 
                                            num_problems: int = 10, 
                                            max_size: int = 100) -> List[Dict]:
        """Generate sample QUBO problems for testing quantum optimization.
        
        Args:
            num_problems: Number of QUBO problems to generate
            max_size: Maximum size of the QUBO matrix
            
        Returns:
            List of dictionaries containing QUBO problems
            
        Raises:
            ValueError: If num_problems or max_size is not positive
        """
        if num_problems <= 0:
            raise ValueError("Number of problems must be positive")
        if max_size <= 0:
            raise ValueError("Maximum size must be positive")
        
        # Reset seeds before generation to ensure reproducibility
        self._set_seeds(self.seed)
            
        problems = []
        for i in range(num_problems):
            size = random.randint(10, max_size)
            # Generate random symmetric matrix for QUBO
            matrix = np.random.randn(size, size)
            matrix = (matrix + matrix.T) / 2  # Make symmetric
            
            problem = {
                "problem_id": f"qubo_{i}",
                "size": size,
                "matrix": matrix.tolist(),
                "description": f"Sample QUBO problem {i} of size {size}x{size}"
            }
            problems.append(problem)
        return problems
    
    def save_training_data(self, 
                          output_dir: str,
                          num_train: int = 1000,
                          num_eval: int = 100,
                          num_test: int = 100):
        """Save generated training, evaluation, and test data to files.
        
        Args:
            output_dir: Directory to save the data
            num_train: Number of training samples
            num_eval: Number of evaluation samples
            num_test: Number of test samples
            
        Raises:
            ValueError: If any sample count is not positive or output_dir is empty
        """
        if not output_dir:
            raise ValueError("Output directory must not be empty")
        if num_train <= 0 or num_eval <= 0 or num_test <= 0:
            raise ValueError("All sample counts must be positive")
            
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate and save text samples
        train_samples = self.generate_text_samples(num_train)
        eval_samples = self.generate_text_samples(num_eval)
        test_samples = self.generate_text_samples(num_test)
        
        # Save text samples
        with open(output_path / "train.json", "w") as f:
            json.dump(train_samples, f, indent=2)
        with open(output_path / "eval.json", "w") as f:
            json.dump(eval_samples, f, indent=2)
        with open(output_path / "test.json", "w") as f:
            json.dump(test_samples, f, indent=2)
        
        # Generate and save quantum optimization problems
        quantum_problems = self.generate_quantum_optimization_problems(
            num_problems=10,
            max_size=100
        )
        with open(output_path / "quantum_problems.json", "w") as f:
            json.dump(quantum_problems, f, indent=2)
            
    def generate_sample_dataset(self, output_dir: str = "sample_data"):
        """Generate a complete sample dataset with default sizes.
        
        Args:
            output_dir: Directory to save the sample dataset
            
        Raises:
            ValueError: If output_dir is empty
        """
        if not output_dir:
            raise ValueError("Output directory must not be empty")
            
        self.save_training_data(
            output_dir=output_dir,
            num_train=100,
            num_eval=20,
            num_test=20
        )
        print(f"Sample dataset generated in {output_dir}/")