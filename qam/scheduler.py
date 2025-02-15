"""
Core scheduling module for QAM.

This module handles QUBO formulation for the task scheduling problem.
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np

@dataclass(frozen=True)  # Make it immutable for hashing
class TimeWindow:
    """Represents a time window for scheduling."""
    start: int
    end: int
    
    def __contains__(self, time: int) -> bool:
        """Check if a time point is within this window."""
        return self.start <= time < self.end
    
    def overlaps(self, other: 'TimeWindow') -> bool:
        """Check if this window overlaps with another."""
        return not (self.end <= other.start or other.end <= self.start)
    
    def duration(self) -> int:
        """Get the duration of this window."""
        return self.end - self.start
    
    def __hash__(self) -> int:
        """Make TimeWindow hashable for use as dictionary key."""
        return hash((self.start, self.end))

@dataclass
class Task:
    """Represents a task to be scheduled."""
    id: str
    duration: int
    release_time: int = 0
    deadline: Optional[int] = None
    
    def get_time_windows(self, horizon: int, window_size: Optional[int] = None) -> List[TimeWindow]:
        """Get possible time windows for this task."""
        start_time = max(0, self.release_time)
        end_time = min(horizon, self.deadline or horizon)
        
        windows = []
        if window_size is None:
            # Default case: create window at every possible start time
            for t in range(start_time, end_time - self.duration + 1):
                windows.append(TimeWindow(t, t + self.duration))
        else:
            # Custom window size: strictly align to window size grid
            t = (start_time // window_size) * window_size  # Align to grid
            while t + self.duration <= end_time:
                if t >= start_time:  # Only create window if start time is valid
                    windows.append(TimeWindow(t, t + self.duration))
                t += window_size  # Move to next grid point
        return windows

@dataclass
class Agent:
    """Represents an agent that can execute tasks."""
    id: str
    capabilities: List[str] = None

@dataclass
class QUBOTerm:
    """Represents a term in the QUBO formulation."""
    indices: Tuple[int, ...]  # Variable indices
    coefficient: float        # Term coefficient

class QUBOScheduler:
    """Handles QUBO formulation for task scheduling."""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.agents: List[Agent] = []
        self._variable_map: Dict[Tuple[str, str, TimeWindow], int] = {}
        self._reverse_map: Dict[int, Tuple[str, str, TimeWindow]] = {}
        self._next_var_index: int = 0
        self._horizon: Optional[int] = None
        self._window_size: Optional[int] = None
    
    def add_task(self, task: Task) -> None:
        """Add a task to be scheduled."""
        self.tasks.append(task)
    
    def add_agent(self, agent: Agent) -> None:
        """Add an agent available for task execution."""
        self.agents.append(agent)
    
    def _optimize_window_size(self) -> int:
        """Determine optimal window size based on task durations."""
        if not self.tasks:
            return 1
            
        # Use GCD of task durations as window size to minimize variables
        durations = [task.duration for task in self.tasks]
        window_size = durations[0]
        for d in durations[1:]:
            window_size = np.gcd(window_size, d)
        return max(1, window_size)
    
    def _create_variable_mapping(self, horizon: int) -> None:
        """Create binary variable mapping for QUBO formulation using time windows."""
        self._variable_map.clear()
        self._reverse_map.clear()
        self._next_var_index = 0
        self._horizon = horizon
        
        # Set window size based on task durations
        self._window_size = self._optimize_window_size()
        
        # Create variables for each task-agent-window combination
        for task in self.tasks:
            for agent in self.agents:
                # Use optimized window size for all tasks
                windows = task.get_time_windows(horizon, window_size=self._window_size)
                for window in windows:
                    key = (task.id, agent.id, window)
                    self._variable_map[key] = self._next_var_index
                    self._reverse_map[self._next_var_index] = key
                    self._next_var_index += 1
    
    def get_variable_index(self, task_id: str, agent_id: str, time: int) -> Optional[int]:
        """Get the variable index for a task-agent-time assignment."""
        # Find the task to get its duration
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task is None:
            return None
            
        # Check if time point is valid for this task
        if time + task.duration > self._horizon:
            return None
            
        # Find a window that could contain this time point
        for key, idx in self._variable_map.items():
            if (key[0] == task_id and 
                key[1] == agent_id and 
                key[2].start <= time < key[2].end):
                return idx
        return None
    
    def decode_variable_index(self, index: int) -> Optional[Tuple[str, str, int]]:
        """Decode a variable index back to task-agent-time assignment."""
        if index not in self._reverse_map:
            return None
        task_id, agent_id, window = self._reverse_map[index]
        return (task_id, agent_id, window.start)
    
    def _build_task_assignment_constraints(self) -> List[QUBOTerm]:
        """Build QUBO terms for task assignment constraints.
        
        Ensures each task is assigned exactly once.
        """
        terms = []
        for task in self.tasks:
            # Collect all variables for this task
            task_vars = []
            for agent in self.agents:
                for key, idx in self._variable_map.items():
                    if key[0] == task.id and key[1] == agent.id:
                        task_vars.append(idx)
            
            if task_vars:
                # Add quadratic terms to enforce exactly one assignment
                for i in task_vars:
                    terms.append(QUBOTerm(indices=(i,), coefficient=-1.0))  # Linear term
                    for j in task_vars:
                        if i < j:  # Only add each pair once
                            terms.append(QUBOTerm(indices=(i, j), coefficient=2.0))  # Quadratic term
        
        return terms
    
    def _build_agent_overlap_constraints(self) -> List[QUBOTerm]:
        """Build QUBO terms for agent overlap constraints.
        
        Ensures no agent is assigned overlapping tasks.
        """
        if not self._horizon:
            raise ValueError("Variable mapping must be created before building constraints")
            
        terms = []
        for agent in self.agents:
            # Get all variables for this agent
            agent_vars = [(key, idx) for key, idx in self._variable_map.items() 
                         if key[1] == agent.id]
            
            # Add penalty terms for overlapping windows
            for i, (key1, idx1) in enumerate(agent_vars):
                for j, (key2, idx2) in enumerate(agent_vars[i+1:], i+1):
                    if key1[2].overlaps(key2[2]):
                        terms.append(QUBOTerm(indices=(idx1, idx2), coefficient=2.0))
        
        return terms
    
    def _build_makespan_objective(self, weight: float = 1.0) -> List[QUBOTerm]:
        """Build QUBO terms for makespan minimization objective."""
        terms = []
        for task in self.tasks:
            for agent in self.agents:
                for key, var_idx in self._variable_map.items():
                    if key[0] == task.id and key[1] == agent.id:
                        window = key[2]
                        # Add term proportional to completion time
                        completion_time = window.end
                        terms.append(QUBOTerm(indices=(var_idx,), 
                                            coefficient=weight * completion_time))
        return terms
    
    def build_qubo(self, horizon: int, makespan_weight: float = 1.0) -> List[QUBOTerm]:
        """Build complete QUBO formulation for the scheduling problem.
        
        Args:
            horizon: Maximum time horizon for scheduling
            makespan_weight: Weight for makespan minimization objective
            
        Returns:
            List of QUBOTerm objects representing the complete QUBO formulation
        """
        # First create variable mapping
        self._create_variable_mapping(horizon)
        
        # Collect all terms
        terms = []
        terms.extend(self._build_task_assignment_constraints())
        terms.extend(self._build_agent_overlap_constraints())
        terms.extend(self._build_makespan_objective(makespan_weight))
        
        return terms
    
    def format_qubo_for_azure(self, terms: List[QUBOTerm]) -> Dict:
        """Format QUBO terms for Azure Quantum submission.
        
        Args:
            terms: List of QUBOTerm objects
            
        Returns:
            Dictionary in Azure Quantum QUBO format
        """
        azure_terms = []
        
        for term in terms:
            if len(term.indices) == 1:
                # Linear term
                azure_terms.append({
                    "c": float(term.coefficient),
                    "ids": [int(term.indices[0])]
                })
            elif len(term.indices) == 2:
                # Quadratic term
                azure_terms.append({
                    "c": float(term.coefficient),
                    "ids": [int(term.indices[0]), int(term.indices[1])]
                })
        
        return {
            "problem_type": "qubo",
            "terms": azure_terms,
            "version": "1.0"
        }