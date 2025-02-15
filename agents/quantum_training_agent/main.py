import argparse
import sys
from typing import Optional
from pathlib import Path

from tools.data_generator import SampleDataGenerator

class QuantumTrainingAgent:
    """Interactive quantum training agent with user-guided and automated modes."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the quantum training agent.
        
        Args:
            verbose: Whether to print detailed thought process
        """
        self.verbose = verbose
        self.data_generator = SampleDataGenerator()
    
    def think(self, message: str):
        """Print thought process if verbose mode is enabled."""
        if self.verbose:
            print(f"\n🤔 Thinking: {message}")
    
    def respond(self, message: str):
        """Print agent response."""
        print(f"\n🤖 Agent: {message}")
    
    def get_user_input(self, prompt: str) -> str:
        """Get input from user with prompt."""
        return input(f"\n👤 {prompt}: ").strip()
    
    def interactive_mode(self):
        """Run in interactive mode with user input."""
        self.respond("Welcome to the Quantum Training Agent! I'll help you train quantum-enhanced language models.")
        self.respond("You can type 'exit' at any time to quit.")
        
        while True:
            command = self.get_user_input("What would you like to do? (generate/train/evaluate/exit)")
            
            if command.lower() == 'exit':
                self.respond("Goodbye!")
                break
                
            elif command.lower() == 'generate':
                self.think("User wants to generate training data")
                output_dir = self.get_user_input("Where should I save the generated data?")
                
                try:
                    self.think(f"Generating sample dataset in {output_dir}")
                    self.data_generator.generate_sample_dataset(output_dir)
                    self.respond(f"Successfully generated sample dataset in {output_dir}/")
                except Exception as e:
                    self.respond(f"Error generating data: {str(e)}")
                    
            elif command.lower() == 'train':
                self.think("User wants to train a model")
                self.respond("Training functionality will be implemented in the next phase")
                
            elif command.lower() == 'evaluate':
                self.think("User wants to evaluate a model")
                self.respond("Evaluation functionality will be implemented in the next phase")
                
            else:
                self.respond("Unknown command. Available commands: generate, train, evaluate, exit")
    
    def automated_mode(self, output_dir: Optional[str] = None):
        """Run in automated mode without user input.
        
        Args:
            output_dir: Optional directory for generated data
        """
        self.think("Starting automated training process")
        
        # Generate data
        data_dir = output_dir or "quantum_training_data"
        self.think(f"Generating training data in {data_dir}")
        try:
            self.data_generator.generate_sample_dataset(data_dir)
            self.respond(f"Successfully generated training data in {data_dir}/")
        except Exception as e:
            self.respond(f"Error generating data: {str(e)}")
            return
            
        # Training will be implemented in next phase
        self.think("Would proceed with automated training here")
        self.respond("Automated training will be implemented in the next phase")
    
    def run_tests(self):
        """Run tests with sample data."""
        self.think("Running tests with sample data")
        
        # Test data generation
        test_dir = Path("test_output")
        try:
            self.data_generator.generate_sample_dataset(str(test_dir))
            self.respond("✓ Data generation test passed")
            
            # Verify files exist
            expected_files = ["train.json", "eval.json", "test.json", "quantum_problems.json"]
            for file in expected_files:
                assert (test_dir / file).exists(), f"Missing file: {file}"
            self.respond("✓ File creation test passed")
            
            # Clean up test files
            import shutil
            shutil.rmtree(test_dir)
            self.respond("✓ Test cleanup completed")
            
        except Exception as e:
            self.respond(f"✗ Test failed: {str(e)}")
            return False
            
        self.respond("All tests passed successfully!")
        return True

def main():
    parser = argparse.ArgumentParser(description="Quantum Training Agent")
    parser.add_argument("--auto", action="store_true", help="Run in automated mode")
    parser.add_argument("--test", action="store_true", help="Run tests with sample data")
    parser.add_argument("--verbose", action="store_true", help="Print detailed thought process")
    parser.add_argument("--output", type=str, help="Output directory for generated data")
    
    args = parser.parse_args()
    agent = QuantumTrainingAgent(verbose=args.verbose)
    
    if args.test:
        success = agent.run_tests()
        sys.exit(0 if success else 1)
    elif args.auto:
        agent.automated_mode(args.output)
    else:
        agent.interactive_mode()

if __name__ == "__main__":
    main()
