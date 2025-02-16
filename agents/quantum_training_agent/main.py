import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import argparse
from crew import QuantumTrainingCrew
from tools.trainer import QuantumTrainer

# ANSI color codes
MAGENTA = '\033[0;35m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

def display_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           QUANTUM TRAINING ORCHESTRATION SYSTEM                  ║
║              [ QUANTUM ReACT PROTOCOL v1.0 ]                    ║
╚══════════════════════════════════════════════════════════════════╝
    """)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Quantum Training Agent with ReACT Methodology',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python main.py
    
  Autonomous mode:
    python main.py --auto --task train
    
  Test mode:
    python main.py --test
    
Tasks:
  - research: Analyze training requirements
  - train: Execute model training
  - optimize: Run quantum optimization
  - evaluate: Evaluate results
  - analyze: Analyze process
  - both: Run complete pipeline (default)
        """
    )
    
    parser.add_argument('--auto', action='store_true', 
                       help='Run in autonomous mode')
    parser.add_argument('--test', action='store_true',
                       help='Run tests with sample data')
    parser.add_argument('--task', type=str, 
                       choices=['research', 'train', 'optimize', 'evaluate', 'analyze', 'both'],
                       default='both',
                       help='Task to perform')
    parser.add_argument('--model', type=str,
                       default='phi-4',
                       help='Model to use for training')
    parser.add_argument('--data_dir', type=str,
                       help='Directory containing training data')
    parser.add_argument('--output_dir', type=str,
                       default='outputs',
                       help='Directory for outputs')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    # Training parameters
    parser.add_argument('--batch_size', type=int, default=32,
                       help='Training batch size')
    parser.add_argument('--learning_rate', type=float, default=2e-4,
                       help='Learning rate')
    parser.add_argument('--num_epochs', type=int, default=10,
                       help='Number of training epochs')
    
    # Quantum parameters
    parser.add_argument('--optimization_frequency', type=int, default=100,
                       help='Steps between quantum optimizations')
    parser.add_argument('--qubo_size_limit', type=int, default=1000,
                       help='Maximum QUBO problem size')
    
    # Azure Quantum parameters
    parser.add_argument('--azure_subscription_id', type=str,
                       help='Azure subscription ID')
    parser.add_argument('--azure_resource_group', type=str,
                       help='Azure resource group')
    parser.add_argument('--azure_workspace', type=str,
                       help='Azure Quantum workspace')
    
    return parser.parse_args()

def run_interactive_mode(args):
    """Run in interactive mode with user input."""
    print(f"{MAGENTA}🤖 Initializing Interactive Mode...{NC}")
    
    crew = QuantumTrainingCrew()
    trainer = QuantumTrainer(model_name=args.model, verbose=args.verbose)
    
    while True:
        print("\n📋 Available commands:")
        print("  1. research - Analyze training requirements")
        print("  2. train   - Execute model training")
        print("  3. optimize - Run quantum optimization")
        print("  4. evaluate - Evaluate results")
        print("  5. analyze  - Analyze process")
        print("  6. auto    - Run complete pipeline")
        print("  7. exit    - Exit program")
        
        command = input("\n👤 Enter command: ").strip().lower()
        
        if command == 'exit':
            print(f"{MAGENTA}👋 Shutting down...{NC}")
            break
            
        elif command in ['research', 'train', 'optimize', 'evaluate', 'analyze', 'auto']:
            prompt = input("👤 Enter specific instructions (or press Enter for default): ").strip()
            if not prompt:
                prompt = "Initialize quantum training process"
                
            task_type = 'both' if command == 'auto' else command
            crew.run(prompt=prompt, task_type=task_type)
            
        else:
            print(f"{RED}❌ Unknown command. Please try again.{NC}")

def run_autonomous_mode(args):
    """Run in autonomous mode without user input."""
    print(f"{MAGENTA}🤖 Initializing Autonomous Mode...{NC}")
    
    crew = QuantumTrainingCrew()
    trainer = QuantumTrainer(model_name=args.model, verbose=args.verbose)
    
    # Configure training parameters
    config = {
        "model_config": {
            "model_name": args.model,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "num_epochs": args.num_epochs
        },
        "quantum_config": {
            "optimization_frequency": args.optimization_frequency,
            "qubo_size_limit": args.qubo_size_limit
        },
        "azure_config": {
            "subscription_id": args.azure_subscription_id,
            "resource_group": args.azure_resource_group,
            "workspace": args.azure_workspace
        }
    }
    
    # Run the complete pipeline
    result = crew.run(
        prompt=f"Execute quantum training with configuration: {config}",
        task_type=args.task
    )
    
    if result:
        print(f"{MAGENTA}✨ Autonomous execution completed successfully!{NC}")
    else:
        print(f"{RED}❌ Autonomous execution failed. Check logs for details.{NC}")

def run_test_mode(args):
    """Run tests with sample data."""
    print(f"{MAGENTA}🧪 Initializing Test Mode...{NC}")
    
    crew = QuantumTrainingCrew()
    trainer = QuantumTrainer(model_name=args.model, verbose=True)
    
    # Run tests with sample data
    test_prompt = """
    Test quantum training pipeline with sample data:
    1. Analyze training requirements
    2. Execute training with quantum optimization
    3. Evaluate results
    4. Generate report
    """
    
    result = crew.run(prompt=test_prompt, task_type='both')
    
    if result:
        print(f"{MAGENTA}✅ Test execution completed successfully!{NC}")
    else:
        print(f"{RED}❌ Test execution failed. Check logs for details.{NC}")

def main():
    args = parse_args()
    display_banner()
    
    try:
        if args.test:
            run_test_mode(args)
        elif args.auto:
            run_autonomous_mode(args)
        else:
            run_interactive_mode(args)
            
    except KeyboardInterrupt:
        print(f"""
{RED}
╔══════════════════════════════════════════════════════════════════╗
║                   EMERGENCY SHUTDOWN INITIATED                   ║
╚══════════════════════════════════════════════════════════════════╝
{NC}""")
    except Exception as e:
        print(f"""
{RED}
╔══════════════════════════════════════════════════════════════════╗
║                     ERROR DETECTED: {str(e)}
╚══════════════════════════════════════════════════════════════════╝
{NC}""")

if __name__ == "__main__":
    main()
