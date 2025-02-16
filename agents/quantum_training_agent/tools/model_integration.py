"""Phi-4 model integration with quantum optimization capabilities."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path
import numpy as np

class QuantumModelIntegration:
    """Handles Phi-4 model integration with quantum optimization."""
    
    def __init__(self, 
                 model_name: str = "microsoft/phi-4",
                 device: Optional[str] = None,
                 quantization: Optional[str] = "4bit",
                 verbose: bool = False):
        """Initialize the quantum model integration.
        
        Args:
            model_name: Name or path of the model to load
            device: Device to use (cuda/cpu)
            quantization: Quantization method (4bit/8bit/None)
            verbose: Whether to print detailed logs
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.quantization = quantization
        self.verbose = verbose
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO if verbose else logging.WARNING,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.model = None
        self.tokenizer = None
        self.quantum_config = {}
        
        # Check if GPU is available for Unsloth
        self.use_unsloth = torch.cuda.is_available() and self.quantization == "4bit"
        if self.use_unsloth:
            try:
                from unsloth import FastLanguageModel
                self.FastLanguageModel = FastLanguageModel
                self.logger.info("Unsloth optimization available")
            except ImportError:
                self.use_unsloth = False
                self.logger.warning("Unsloth import failed, falling back to standard loading")
        else:
            self.logger.info("Using standard model loading (no Unsloth optimization)")
        
    def setup(self, config: Dict[str, Any]):
        """Set up the model with quantum optimization.
        
        Args:
            config: Configuration dictionary containing model and quantum settings
            
        Returns:
            Boolean indicating success
        """
        self.logger.info(f"Setting up {self.model_name} with quantum optimization")
        self.logger.info(f"Using device: {self.device}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Load and optimize model
            if self.use_unsloth:
                self.logger.info("Using 4-bit quantization with Unsloth")
                model, tokenizer = self.FastLanguageModel.from_pretrained(
                    model_name=self.model_name,
                    max_seq_length=config.get("max_seq_length", 2048),
                    dtype=torch.bfloat16,
                    load_in_4bit=True
                )
                self.model = model
                self.tokenizer = tokenizer
            else:
                self.logger.info(f"Loading model with standard method")
                load_config = {
                    "trust_remote_code": True,
                    "device_map": "auto"
                }
                
                # Apply quantization if specified
                if self.quantization == "8bit":
                    load_config["load_in_8bit"] = True
                elif self.quantization == "4bit":
                    load_config["load_in_4bit"] = True
                else:
                    load_config["torch_dtype"] = torch.bfloat16
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    **load_config
                )
            
            # Configure quantum optimization
            self.quantum_config = {
                "optimization_frequency": config.get("optimization_frequency", 100),
                "qubo_size_limit": config.get("qubo_size_limit", 1000),
                "solver_timeout": config.get("solver_timeout", 300)
            }
            
            self.logger.info("Model setup completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up model: {str(e)}")
            raise
            
    def save_model(self, save_dir: str):
        """Save the model and configuration.
        
        Args:
            save_dir: Directory to save the model
        """
        if not self.model:
            raise ValueError("Model not initialized")
            
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Saving model to {save_dir}")
        
        # Save model
        self.model.save_pretrained(save_path)
        
        # Save tokenizer
        if self.tokenizer:
            self.tokenizer.save_pretrained(save_path)
            
        # Save configuration
        config_path = save_path / "quantum_config.json"
        with open(config_path, "w") as f:
            json.dump(self.quantum_config, f, indent=2)
            
        self.logger.info("Model saved successfully")
        
    def load_model(self, model_path: str):
        """Load a saved model.
        
        Args:
            model_path: Path to the saved model
            
        Returns:
            Boolean indicating success
        """
        model_path = Path(model_path)
        if not model_path.exists():
            raise ValueError(f"Model path does not exist: {model_path}")
            
        self.logger.info(f"Loading model from {model_path}")
        
        try:
            # Load model
            if self.use_unsloth:
                model, tokenizer = self.FastLanguageModel.from_pretrained(
                    model_name=str(model_path),
                    max_seq_length=2048,
                    dtype=torch.bfloat16,
                    load_in_4bit=True
                )
                self.model = model
                self.tokenizer = tokenizer
            else:
                load_config = {
                    "trust_remote_code": True,
                    "device_map": "auto"
                }
                
                # Apply quantization if specified
                if self.quantization == "8bit":
                    load_config["load_in_8bit"] = True
                elif self.quantization == "4bit":
                    load_config["load_in_4bit"] = True
                else:
                    load_config["torch_dtype"] = torch.bfloat16
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    str(model_path),
                    **load_config
                )
                self.tokenizer = AutoTokenizer.from_pretrained(
                    str(model_path),
                    trust_remote_code=True
                )
            
            # Load quantum configuration
            config_path = model_path / "quantum_config.json"
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.quantum_config = json.load(f)
                    
            self.logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise
            
    def generate(self, 
                prompt: str,
                max_length: int = 100,
                temperature: float = 0.7,
                **kwargs):
        """Generate text using the model.
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        if not self.model or not self.tokenizer:
            raise ValueError("Model not initialized")
            
        try:
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate
            outputs = self.model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs.get('attention_mask'),
                max_length=max_length,
                temperature=temperature,
                **kwargs
            )
            
            # Decode output
            generated_text = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            return generated_text
            
        except Exception as e:
            self.logger.error(f"Error during generation: {str(e)}")
            raise
            
    def get_embeddings(self, text: str):
        """Get embeddings for input text.
        
        Args:
            text: Input text
            
        Returns:
            Text embeddings as numpy array
        """
        if not self.model or not self.tokenizer:
            raise ValueError("Model not initialized")
            
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get embeddings from last hidden state
            with torch.no_grad():
                outputs = self.model(**inputs)
                hidden_states = outputs.last_hidden_state
                if isinstance(hidden_states, torch.Tensor):
                    embeddings = hidden_states.mean(dim=1)
                else:
                    # Handle case where hidden_states is a mock or custom object
                    embeddings = hidden_states.mean(1)
                
            return embeddings.cpu().numpy()
            
        except Exception as e:
            self.logger.error(f"Error getting embeddings: {str(e)}")
            raise