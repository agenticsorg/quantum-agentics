#!/usr/bin/env python3
from agent import QAMAgent

def run_example():
    sample_config = {
        "agent_name": "ExampleQAMAgent",
        "mode": "demo",
        "settings": {
            "argument1": "demo_value",
            "argument2": 5,
            "evaluation_options": ["accuracy", "speed"]
        }
    }
    agent = QAMAgent(sample_config)
    decisions = agent.run()
    print("Example run decisions:", decisions)

if __name__ == "__main__":
    run_example()