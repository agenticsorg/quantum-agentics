import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import argparse
from crew import HelloWorldCrew

# ANSI color codes
MAGENTA = '\033[0;35m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

def display_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              NEURAL NETWORK ORCHESTRATION SYSTEM                 ║
║                     [ CODENAME: CREWAI ]                        ║
╚══════════════════════════════════════════════════════════════════╝
    """)

def parse_args():
    parser = argparse.ArgumentParser(description='Neural Network Orchestration System')
    parser.add_argument('--prompt', type=str, help='Prompt for the AI system', default="Tell me about yourself")
    parser.add_argument('--task', type=str, choices=['research', 'execute', 'analyze', 'both'], 
                       help='Task to perform: research, execute, analyze, or both', default='both')
    return parser.parse_args()

def run():
    args = parse_args()
    display_banner()
    crew = HelloWorldCrew()
    result = crew.run(prompt=args.prompt, task_type=args.task)
    if result:
        print("""
╔══════════════════════════════════════════════════════════════════╗
║             🌟 NEURAL PROCESSING COMPLETE 🌟                     ║
╚══════════════════════════════════════════════════════════════════╝

""" + MAGENTA + """▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
        ✨ ALL OBJECTIVES ACHIEVED
        📊 PERFORMANCE METRICS OPTIMAL
        🔒 SYSTEM INTEGRITY MAINTAINED
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀""" + NC + """
        """)
    else:
        print("""
╔══════════════════════════════════════════════════════════════════╗
║             ⚠️ NEURAL PROCESSING INTERRUPTED ⚠️                 ║
╚══════════════════════════════════════════════════════════════════╝

""" + RED + """▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
        🔍 DIAGNOSTIC SCAN INITIATED
        💫 QUANTUM STATE PRESERVED
        🔄 READY FOR REACTIVATION
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀""" + NC + """
        """)

if __name__ == "__main__":
    run()
