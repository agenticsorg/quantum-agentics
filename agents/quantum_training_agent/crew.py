from tools.custom_tool import CustomTool
import yaml
from dotenv import load_dotenv
import os
import httpx
import json
import asyncio
from config.react_validation import ReACTValidator

load_dotenv()  # Load environment variables from .env file

async def stream_openrouter_response(messages, model, progress_callback=None):
    """Stream responses directly from OpenRouter with progress tracking"""
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Quantum Training Agent"
            },
            json={
                "model": model,
                "messages": messages,
                "stream": True,
                "temperature": 0.7
            },
            timeout=None
        ) as response:
            async for chunk in response.aiter_bytes():
                if chunk:
                    try:
                        chunk_str = chunk.decode()
                        if chunk_str.startswith('data: '):
                            chunk_data = json.loads(chunk_str[6:])
                            if chunk_data != '[DONE]':
                                if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                    delta = chunk_data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        print(content, end='', flush=True)
                                        if progress_callback:
                                            await progress_callback(content)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue

class QuantumTrainingCrew:
    """Crew for quantum-enhanced model training using ReACT methodology."""
    
    def __init__(self):
        """Initialize the quantum training crew."""
        with open('config/agents.yaml', 'r') as f:
            self.agents_config = yaml.safe_load(f)
        with open('config/tasks.yaml', 'r') as f:
            self.tasks_config = yaml.safe_load(f)
        with open('config/analysis.yaml', 'r') as f:
            self.analysis_config = yaml.safe_load(f)
            
        self.validator = ReACTValidator()
        self.validation_status = {"reasoning": [], "actions": []}
        self.progress_tracker = {"current_step": 0, "total_steps": 0, "status": ""}
    
    def track_progress(self, step_type, status):
        """Track progress of methodology execution"""
        self.progress_tracker["current_step"] += 1
        self.progress_tracker["status"] = status
        
        progress = f"""
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
📊 Progress Update:
➤ Step {self.progress_tracker["current_step"]}: {step_type}
➤ Status: {status}
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
"""
        print(progress)
    
    async def run_with_streaming(self, prompt="Initialize training", task_type="both"):
        """Run crew with streaming responses"""
        self.progress_tracker["total_steps"] = 5  # Research + Training + Optimization + Evaluation + Analysis
        
        if task_type in ["research", "both"]:
            await self._run_researcher(prompt)
            
        if task_type in ["train", "both"]:
            await self._run_trainer(prompt)
            
        if task_type in ["optimize", "both"]:
            await self._run_optimizer(prompt)
            
        if task_type in ["evaluate", "both"]:
            await self._run_evaluator(prompt)
            
        if task_type in ["analyze", "both"]:
            await self._run_analyzer(prompt)
            
        return True
    
    async def _run_researcher(self, prompt):
        """Run the researcher agent"""
        researcher_messages = [{
            "role": "system",
            "content": f"""You are a {self.agents_config['researcher']['role']} with the goal: {self.agents_config['researcher']['goal']}.
Use ReACT methodology to analyze quantum training requirements:

[THOUGHT] Analyze the training requirements and quantum optimization opportunities
[ACTION] Research and evaluate potential strategies
[OBSERVATION] Document findings and insights
[REFLECTION] Evaluate approaches and recommend next steps

Task: {prompt}"""
        }, {
            "role": "user",
            "content": f"{self.tasks_config['research_task']['description']}\n\nUser Prompt: {prompt}"
        }]
        
        self.track_progress("Research Phase", "Analyzing quantum training requirements")
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  🔬 QUANTUM TRAINING RESEARCHER - INITIALIZING ANALYSIS         ║
╚══════════════════════════════════════════════════════════════════╝

▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
🧠 LOADING RESEARCH PROTOCOLS...
📚 ACCESSING QUANTUM KNOWLEDGE BASE...
🔍 INITIALIZING ANALYSIS ENGINE...
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

[SYS]: Beginning Research Analysis...
""")
        await stream_openrouter_response(researcher_messages, self.agents_config['researcher']['llm'])
    
    async def _run_trainer(self, prompt):
        """Run the trainer agent"""
        trainer_messages = [{
            "role": "system",
            "content": f"""You are a {self.agents_config['trainer']['role']} with the goal: {self.agents_config['trainer']['goal']}.
Use ReACT methodology to implement quantum-enhanced training:

[THOUGHT] Analyze implementation requirements
[ACTION] Execute training steps
[OBSERVATION] Monitor progress and results
[REFLECTION] Evaluate training effectiveness

Task: {prompt}"""
        }, {
            "role": "user",
            "content": f"{self.tasks_config['training_task']['description']}\n\nUser Prompt: {prompt}"
        }]
        
        self.track_progress("Training Phase", "Executing quantum-enhanced training")
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  🚀 QUANTUM MODEL TRAINER - INITIATING TRAINING SEQUENCE        ║
╚══════════════════════════════════════════════════════════════════╝

▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
⚡ QUANTUM CIRCUITS ACTIVE
🔄 TRAINING LOOP INITIALIZED
📊 METRICS TRACKING ONLINE
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

[SYS]: Beginning Training Sequence...
""")
        await stream_openrouter_response(trainer_messages, self.agents_config['trainer']['llm'])
    
    async def _run_optimizer(self, prompt):
        """Run the optimizer agent"""
        optimizer_messages = [{
            "role": "system",
            "content": f"""You are a {self.agents_config['optimizer']['role']} with the goal: {self.agents_config['optimizer']['goal']}.
Use ReACT methodology to optimize quantum training:

[THOUGHT] Analyze optimization opportunities
[ACTION] Implement quantum optimization
[OBSERVATION] Monitor optimization results
[REFLECTION] Evaluate effectiveness

Task: {prompt}"""
        }, {
            "role": "user",
            "content": f"{self.tasks_config['optimization_task']['description']}\n\nUser Prompt: {prompt}"
        }]
        
        self.track_progress("Optimization Phase", "Running quantum optimization")
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  ⚛️ QUANTUM OPTIMIZER - ENGAGING OPTIMIZATION PROTOCOLS         ║
╚══════════════════════════════════════════════════════════════════╝

▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
🔮 QUANTUM SOLVER READY
🎯 OPTIMIZATION TARGET SET
🔄 ITERATION LOOP PRIMED
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

[SYS]: Beginning Optimization Sequence...
""")
        await stream_openrouter_response(optimizer_messages, self.agents_config['optimizer']['llm'])
    
    async def _run_evaluator(self, prompt):
        """Run the evaluator agent"""
        evaluator_messages = [{
            "role": "system",
            "content": f"""You are a {self.agents_config['evaluator']['role']} with the goal: {self.agents_config['evaluator']['goal']}.
Use ReACT methodology to evaluate training results:

[THOUGHT] Analyze evaluation requirements
[ACTION] Compute performance metrics
[OBSERVATION] Document findings
[REFLECTION] Provide recommendations

Task: {prompt}"""
        }, {
            "role": "user",
            "content": f"{self.tasks_config['evaluation_task']['description']}\n\nUser Prompt: {prompt}"
        }]
        
        self.track_progress("Evaluation Phase", "Evaluating training results")
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  📊 PERFORMANCE EVALUATOR - INITIATING ASSESSMENT              ║
╚══════════════════════════════════════════════════════════════════╝

▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
📈 METRICS COMPUTATION ACTIVE
🎯 BENCHMARKS LOADED
📋 VALIDATION SUITE READY
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

[SYS]: Beginning Evaluation Sequence...
""")
        await stream_openrouter_response(evaluator_messages, self.agents_config['evaluator']['llm'])
    
    async def _run_analyzer(self, prompt):
        """Run the analyzer agent"""
        analyzer_messages = [{
            "role": "system",
            "content": f"""You are analyzing the quantum training process with the following metrics configuration:

{yaml.dump(self.analysis_config, default_flow_style=False)}

Use ReACT methodology to analyze the process:

[THOUGHT] Review metrics and performance data
[ACTION] Analyze against thresholds
[OBSERVATION] Document findings
[REFLECTION] Recommend improvements

Task: {prompt}"""
        }, {
            "role": "user",
            "content": f"{self.tasks_config['analysis_task']['description']}\n\nUser Prompt: {prompt}"
        }]
        
        self.track_progress("Analysis Phase", "Analyzing overall process")
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  🔍 PROCESS ANALYZER - BEGINNING COMPREHENSIVE ANALYSIS         ║
╚══════════════════════════════════════════════════════════════════╝

▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
📊 LOADING PERFORMANCE DATA
🎯 CHECKING THRESHOLDS
📈 ANALYZING TRENDS
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

[SYS]: Beginning Process Analysis...
""")
        await stream_openrouter_response(analyzer_messages, self.agents_config['analyzer']['llm'])
    
    def run(self, prompt="Initialize training", task_type="both"):
        """Run crew synchronously"""
        try:
            return asyncio.run(self.run_with_streaming(prompt=prompt, task_type=task_type))
        except KeyboardInterrupt:
            print("""
╔══════════════════════════════════════════════════════════════════╗
║  🛑 EMERGENCY SHUTDOWN SEQUENCE INITIATED                        ║
╚══════════════════════════════════════════════════════════════════╝
⚠️ Saving training state...
💾 Preserving model checkpoints...
🔌 Powering down quantum systems...
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
