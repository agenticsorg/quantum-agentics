"""
Core scheduling module for QAM.

This module handles QUBO formulation for the task scheduling problem.
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np

@dataclass
class Task:
    """Represents a task to be scheduled."""
    id: str
    duration: int
    release_time: int = 0
    deadline: Optional[int] = None
    
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
        self._variable_map: Dict[Tuple[str, str, int], int] = {}
        self._reverse_map: Dict[int, Tuple[str, str, int]] = {}
        self._next_var_index: int = 0
        self._horizon: Optional[int] = None
    
    def add_task(self, task: Task) -> None:
        """Add a task to be scheduled."""
        self.tasks.append(task)
    
    def add_agent(self, agent: Agent) -> None:
        """Add an agent available for task execution."""
        self.agents.append(agent)
    
    def _create_variable_mapping(self, horizon: int) -> None:
        """Create binary variable mapping for QUBO formulation."""
        self._variable_map.clear()
        self._reverse_map.clear()
        self._next_var_index = 0
        self._horizon = horizon
        
        for task in self.tasks:
            for agent in self.agents:
                start_time = max(0, task.release_time)
                end_time = min(horizon, task.deadline or horizon)
                
                for t in range(start_time, end_time - task.duration + 1):
                    key = (task.id, agent.id, t)
                    self._variable_map[key] = self._next_var_index
                    self._reverse_map[self._next_var_index] = key
                    self._next_var_index += 1
    
    def get_variable_index(self, task_id: str, agent_id: str, time: int) -> Optional[int]:
        """Get the variable index for a task-agent-time assignment."""
        key = (task_id, agent_id, time)
        return self._variable_map.get(key)
    
    def decode_variable_index(self, index: int) -> Optional[Tuple[str, str, int]]:
        """Decode a variable index back to task-agent-time assignment."""
        return self._reverse_map.get(index)
    
    def _build_task_assignment_constraints(self) -> List[QUBOTerm]:
        """Build QUBO terms for task assignment constraints.
        
        Ensures each task is assigned exactly once.
        """
        terms = []
        for task in self.tasks:
            # Collect all variables for this task
            task_vars = []
            for agent in self.agents:
                for _, key in self._reverse_map.items():
                    if key[0] == task.id and key[1] == agent.id:
                        var_idx = self._variable_map[key]
                        task_vars.append(var_idx)
            
            if task_vars:
                # Add quadratic terms to enforce exactly one assignment
                for i in task_vars:
                    for j in task_vars:
                        if i == j:
                            terms.append(QUBOTerm(indices=(i,), coefficient=-1.0))  # Linear term
                        else:
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
            # For each time slot, collect all tasks that could be active
            for t in range(self._horizon):
                active_vars = set()  # Use set to avoid duplicates
                for task in self.tasks:
                    # Check all start times that would make task active at time t
                    earliest_start = max(0, t - task.duration + 1)
                    latest_start = t
                    
                    for start_t in range(earliest_start, latest_start + 1):
                        var_idx = self.get_variable_index(task.id, agent.id, start_t)
                        if var_idx is not None:
                            active_vars.add(var_idx)
                
                # Add penalty terms for any pair of overlapping tasks
                active_vars = sorted(list(active_vars))  # Sort for consistent ordering
                for i in range(len(active_vars)):
                    for j in range(i + 1, len(active_vars)):
                        terms.append(QUBOTerm(indices=(active_vars[i], active_vars[j]), 
                                            coefficient=2.0))
        
        return terms
    
    def _build_makespan_objective(self, weight: float = 1.0) -> List[QUBOTerm]:
        """Build QUBO terms for makespan minimization objective."""
        terms = []
        for task in self.tasks:
            for agent in self.agents:
                for t, _ in self._reverse_map.items():
                    var_idx = self.get_variable_index(task.id, agent.id, t)
                    if var_idx is not None:
                        # Add term proportional to completion time
                        completion_time = t + task.duration
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