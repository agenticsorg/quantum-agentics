"""
CrewAI integration module for QAM.

This module handles the integration with CrewAI framework for agent management.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from .scheduler import Task as SchedulerTask, Agent as SchedulerAgent, QUBOScheduler
from .azure_quantum import AzureQuantumClient, AzureQuantumConfig

class Process(Enum):
    """Process types for crew execution."""
    sequential = "sequential"
    parallel = "parallel"

@dataclass
class Agent:
    """CrewAI agent representation."""
    name: str
    role: str
    goal: str
    backstory: str
    allow_delegation: bool = False
    tasks: List['Task'] = None

    def __post_init__(self):
        self.tasks = self.tasks or []

@dataclass
class Task:
    """CrewAI task representation."""
    description: str
    expected_output: str
    context: Dict[str, Any]
    agent: Optional[Agent] = None

@dataclass
class Crew:
    """CrewAI crew representation."""
    agents: List[Agent]
    tasks: List[Task]
    process: Process

    def reset(self):
        """Reset task assignments."""
        for agent in self.agents:
            agent.tasks = []
        for task in self.tasks:
            task.agent = None

    def assign_task(self, agent: Agent, task: Task):
        """Assign a task to an agent."""
        task.agent = agent
        agent.tasks.append(task)

    def run(self):
        """Execute the crew's tasks."""
        if self.process == Process.sequential:
            for agent in self.agents:
                for task in agent.tasks:
                    # In real CrewAI this would execute the task
                    pass
        else:  # parallel
            for agent in self.agents:
                # In real CrewAI this would spawn parallel executions
                for task in agent.tasks:
                    pass

@dataclass
class AgentConfig:
    """Configuration for a worker agent."""
    id: str
    name: str
    role: str
    goal: str
    backstory: str
    capabilities: List[str] = None

@dataclass
class TaskConfig:
    """Configuration for a task to be executed."""
    id: str
    name: str
    description: str
    duration: int
    release_time: int = 0
    deadline: Optional[int] = None
    requirements: List[str] = None

class QAMManagerAgent:
    """Manager agent that coordinates task scheduling and execution."""
    
    def __init__(
        self,
        azure_config: AzureQuantumConfig,
        scheduler: Optional[QUBOScheduler] = None
    ):
        """Initialize the manager agent.
        
        Args:
            azure_config: Azure Quantum configuration
            scheduler: Optional QUBOScheduler instance (creates new one if None)
        """
        self.azure_client = AzureQuantumClient(azure_config)
        self.scheduler = scheduler or QUBOScheduler()
        self.crew = None
        self._agent_map = {}
        self._task_map = {}
    
    def create_agent(self, config: AgentConfig) -> Agent:
        """Create a CrewAI agent from configuration.
        
        Args:
            config: Agent configuration
            
        Returns:
            Created CrewAI agent
        """
        agent = Agent(
            name=config.name,
            role=config.role,
            goal=config.goal,
            backstory=config.backstory,
            allow_delegation=False  # Disable delegation for now
        )
        
        # Create scheduler agent
        scheduler_agent = SchedulerAgent(
            id=config.id,
            capabilities=config.capabilities
        )
        
        # Store mapping
        self._agent_map[config.id] = {
            'crew_agent': agent,
            'scheduler_agent': scheduler_agent
        }
        
        # Add to scheduler
        self.scheduler.add_agent(scheduler_agent)
        
        return agent
    
    def create_task(self, config: TaskConfig) -> Task:
        """Create a CrewAI task from configuration.
        
        Args:
            config: Task configuration
            
        Returns:
            Created CrewAI task
        """
        task = Task(
            description=config.description,
            expected_output=f"Completed task: {config.name}",
            context={
                'task_id': config.id,
                'requirements': config.requirements
            }
        )
        
        # Create scheduler task
        scheduler_task = SchedulerTask(
            id=config.id,
            duration=config.duration,
            release_time=config.release_time,
            deadline=config.deadline
        )
        
        # Store mapping
        self._task_map[config.id] = {
            'crew_task': task,
            'scheduler_task': scheduler_task
        }
        
        # Add to scheduler
        self.scheduler.add_task(scheduler_task)
        
        return task
    
    def optimize_schedule(self, horizon: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """Optimize task schedule using quantum solver.
        
        Args:
            horizon: Maximum time horizon for scheduling
            
        Returns:
            Dictionary mapping agent IDs to their task schedules
        """
        # Build QUBO problem
        terms = self.scheduler.build_qubo(horizon)
        
        # Convert to Azure Quantum format
        problem = self.scheduler.format_qubo_for_azure(terms)
        
        # Submit and wait for result
        job_id = self.azure_client.submit_qubo(problem)
        result = self.azure_client.wait_for_job(job_id)
        
        # Parse solution into schedule
        schedule = {}
        solution = result.get('solution', [])
        
        # For each variable that's 1 in the solution, decode its meaning
        for i, value in enumerate(solution):
            if value == 1:
                task_id, agent_id, start_time = self.scheduler.decode_variable_index(i)
                if agent_id not in schedule:
                    schedule[agent_id] = []
                
                task_config = next(
                    cfg for cfg in self._task_map.values()
                    if cfg['scheduler_task'].id == task_id
                )
                
                schedule[agent_id].append({
                    'task_id': task_id,
                    'start_time': start_time,
                    'duration': task_config['scheduler_task'].duration,
                    'crew_task': task_config['crew_task']
                })
        
        # Sort each agent's tasks by start time
        for agent_id in schedule:
            schedule[agent_id].sort(key=lambda x: x['start_time'])
        
        return schedule
    
    def setup_crew(self, agents: List[AgentConfig], tasks: List[TaskConfig]) -> None:
        """Set up CrewAI crew with agents and tasks.
        
        Args:
            agents: List of agent configurations
            tasks: List of task configurations
        """
        # Create agents and tasks
        crew_agents = [self.create_agent(cfg) for cfg in agents]
        crew_tasks = [self.create_task(cfg) for cfg in tasks]
        
        # Create crew
        self.crew = Crew(
            agents=crew_agents,
            tasks=crew_tasks,
            process=Process.sequential  # Start with sequential for simplicity
        )
    
    def assign_tasks(self, schedule: Dict[str, List[Dict[str, Any]]]) -> None:
        """Assign tasks to agents according to schedule.
        
        Args:
            schedule: Schedule returned by optimize_schedule
        """
        if not self.crew:
            raise RuntimeError("Crew not set up. Call setup_crew first.")
        
        # Clear any existing assignments
        self.crew.reset()
        
        # For each agent
        for agent_id, tasks in schedule.items():
            agent_config = self._agent_map[agent_id]
            crew_agent = agent_config['crew_agent']
            
            # Assign tasks in order
            for task_info in tasks:
                crew_task = task_info['crew_task']
                # Add start time to task context
                crew_task.context['start_time'] = task_info['start_time']
                self.crew.assign_task(crew_agent, crew_task)
    
    def execute(self) -> None:
        """Execute the optimized schedule with CrewAI."""
        if not self.crew:
            raise RuntimeError("Crew not set up. Call setup_crew first.")
        
        # Optimize schedule
        schedule = self.optimize_schedule()
        
        # Assign tasks according to schedule
        self.assign_tasks(schedule)
        
        # Run the crew
        self.crew.run()