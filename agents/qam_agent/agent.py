#!/usr/bin/env python3
import sys
import os
import argparse
import json

# Insert project root into system path for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Import QAM modules from the qam package
from qam import cluster_management, scheduler, quantum_reasoning, azure_quantum, orchestration_protocol, ui
# Import OpenRouter streaming function from hello_world crew module for crewai integration
from agents.hello_world.crew import stream_openrouter_response
import asyncio

class QAMAgent:
    def __init__(self, config: dict):
        self.config = config
        self.agent_name = config.get("agent_name", "QAMAgent")
        self.mode = config.get("mode", "default")
        # Initialize scheduler from qam.scheduler for demonstration purposes
        self.scheduler = scheduler.QUBOScheduler()
        # Additional settings can be configured
        self.settings = config.get("settings", {})
    
    async def run_with_openrouter(self, prompt, task_type):
        # Construct messages based on task type
        if task_type in ["research", "both"]:
            messages = [{
                "role": "system",
                "content": f"ReACT Reasoning: Analyze task requirements and propose actions for prompt: {prompt}"
            }, {
                "role": "user",
                "content": prompt
            }]
        else:
            messages = [{
                "role": "system",
                "content": f"ReACT Execution: Optimize scheduling decisions for prompt: {prompt}"
            }, {
                "role": "user",
                "content": prompt
            }]
        # Determine LLM model from configuration or use default
        model = self.config.get("llm", "anthropic/claude-3-sonnet-20240229")
        print("📡 Sending request to OpenRouter LLM for ReACT reasoning...")
        await stream_openrouter_response(messages, model)
    
    async def run_with_streaming(self, prompt="Tell me about yourself", task_type="both"):
        mode = self.mode.lower()
        if mode in ["test", "demo"]:
            print("╔══════════════════════════════════════════════════════════════════╗")
            print("║  QAM Agent ReACT Execution with crewai & OpenRouter Integration    ║")
            print("╚══════════════════════════════════════════════════════════════════╝")
            print(f"⏱ Initializing agent: {self.agent_name}")
        else:
            print(f"Running {self.agent_name} in {self.mode} mode with settings: {self.settings}")
        
        # Use crewai reasoning via OpenRouter integration
        await self.run_with_openrouter(prompt, task_type)
        
        # Simulate tool selection and optimization based on ReACT logic
        if mode in ["test", "demo"]:
            print("🔧 Selecting optimal tools based on ReACT reasoning...")
            print("⚙️ Optimizing scheduling decisions using crewai integration...")
        
        # Simulate scheduling decisions
        decisions = []
        for i in range(3):
            decision = f"Task_{i} scheduled at slot {i}"
            decisions.append(decision)
        
        if mode in ["test", "demo"]:
            print("✅ ReACT Execution Complete!")
            print("📊 Final Scheduling Decisions:")
            for dec in decisions:
                print("   ➤", dec)
        else:
            print("Decisions:", decisions)
        return decisions

    def run(self, prompt="Tell me about yourself", task_type="both"):
        try:
            return asyncio.run(self.run_with_streaming(prompt=prompt, task_type=task_type))
        except KeyboardInterrupt:
            print("""
╔══════════════════════════════════════════════════════════════════╗
║  🛑 EMERGENCY SHUTDOWN SEQUENCE INITIATED                        ║
╚══════════════════════════════════════════════════════════════════╝
⚠️ Saving neural state...
💾 Preserving memory banks...
🔌 Powering down cores...
""")
            return None
        except Exception as e:
            print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  ⚠️ SYSTEM MALFUNCTION DETECTED                                 ║
╚══════════════════════════════════════════════════════════════════╝
🔍 Error Analysis:
{str(e)}
🔧 Initiating recovery protocols...
""")
            return None

def parse_args():
    parser = argparse.ArgumentParser(description="QAM Agent Implementation Phase Agent with extended QAM options")
    parser.add_argument("--config", type=str, help="Path to configuration JSON file", default="")
    parser.add_argument("--agent_name", type=str, default="QAMAgentSample", help="Name of the agent")
    parser.add_argument("--mode", type=str, default="test", help="Operating mode (test, demo, unittest, etc.)")
    parser.add_argument("--argument1", type=str, default="value1", help="Sample argument 1")
    parser.add_argument("--argument2", type=int, default=10, help="Sample argument 2")
    parser.add_argument("--evaluation_options", type=str, default="option1,option2", help="Comma-separated evaluation options")
    parser.add_argument("--azure_resource_group", type=str, default="", help="Azure resource group")
    parser.add_argument("--azure_workspace_name", type=str, default="", help="Azure workspace name")
    parser.add_argument("--azure_location", type=str, default="", help="Azure location")
    parser.add_argument("--azure_subscription_id", type=str, default="", help="Azure subscription ID")
    parser.add_argument("--azure_target_id", type=str, default="", help="Azure target ID (default: microsoft.paralleltempering.cpu)")
    # Additional QAM options from qam/ modules
    parser.add_argument("--qaoa_p_steps", type=int, default=2, help="Number of QAOA steps")
    parser.add_argument("--qaoa_learning_rate", type=float, default=0.1, help="Learning rate for QAOA optimizer")
    parser.add_argument("--cluster_threshold", type=int, default=100, help="Threshold for splitting a cluster")
    parser.add_argument("--optimization_target", type=float, default=0.8, help="Target utilization for resource optimization")
    return parser.parse_args()

def main():
    args = parse_args()
    if args.config and os.path.exists(args.config):
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        config = {}
    config["agent_name"] = args.agent_name
    config["mode"] = args.mode
    if "settings" not in config:
        config["settings"] = {}
    config["settings"]["argument1"] = args.argument1
    config["settings"]["argument2"] = args.argument2
    config["settings"]["evaluation_options"] = args.evaluation_options.split(",")
    config["settings"]["qaoa_p_steps"] = args.qaoa_p_steps
    config["settings"]["qaoa_learning_rate"] = args.qaoa_learning_rate
    config["settings"]["cluster_threshold"] = args.cluster_threshold
    config["settings"]["optimization_target"] = args.optimization_target
    config["azure"] = {
         "resource_group": args.azure_resource_group,
         "workspace_name": args.azure_workspace_name,
         "location": args.azure_location,
         "subscription_id": args.azure_subscription_id,
         "target_id": args.azure_target_id if args.azure_target_id else "microsoft.paralleltempering.cpu"
    }
    agent = QAMAgent(config)
    decisions = agent.run()
    output_file = "qam_agent_output.json"
    with open(output_file, "w") as f:
        json.dump({"decisions": decisions}, f, indent=2)
    print(f"Decisions saved to {output_file}")

if __name__ == "__main__":
    main()