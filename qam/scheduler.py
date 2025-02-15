from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from .quantum_reasoning import QuantumReasoningState

class QUBOTerm:
    """Represents a term in the QUBO formulation."""
    def __init__(self, i: int, j: int, weight: float):
        self.i = i
        self.j = j
        self.weight = weight

class QUBOScheduler:
    """Scheduler that uses QUBO formulation with quantum reasoning enhancement."""
    
    def __init__(self):
        self.base_weights: Dict[str, float] = {}
        self.reasoning_weights: Dict[str, float] = {}
        
    def build_qubo_with_reasoning(self, horizon: int, 
                                reasoning_state: QuantumReasoningState) -> List[QUBOTerm]:
        """Builds QUBO formulation incorporating quantum reasoning state."""
        terms: List[QUBOTerm] = []
        
        # Reset reasoning weights
        self.reasoning_weights.clear()
        
        # Get probabilities from reasoning state
        state_probs = reasoning_state.get_probabilities()
        
        # Convert decision path probabilities to task weights
        for path, prob in state_probs.items():
            for action in path.actions:
                if action.startswith('schedule_'):
                    pos = int(action.split('_')[1])
                    if 0 <= pos < horizon:
                        self.reasoning_weights[action] = self.reasoning_weights.get(action, 0.0) + prob
                
        # Normalize reasoning weights
        total_weight = sum(self.reasoning_weights.values())
        if total_weight > 0:
            self.reasoning_weights = {
                k: v/total_weight for k, v in self.reasoning_weights.items()
            }
        
        # Build basic QUBO terms
        for i in range(horizon):
            for j in range(i, horizon):
                # Base weight from standard scheduling constraints
                base_weight = self._calculate_base_weight(i, j)
                
                # Adjust weight using reasoning state
                reasoning_factor = self._calculate_reasoning_factor(i, j)
                
                # Combine weights with stronger influence from reasoning
                final_weight = base_weight * (1.0 + 2.0 * reasoning_factor)
                
                terms.append(QUBOTerm(i, j, final_weight))
        
        return terms
    
    def _calculate_base_weight(self, i: int, j: int) -> float:
        """Calculates base weight for QUBO term without reasoning."""
        # Example implementation - should be customized based on specific scheduling needs
        if i == j:
            return 1.0  # Diagonal terms
        return 0.5 * np.exp(-abs(i - j))  # Off-diagonal terms decay with distance
    
    def _calculate_reasoning_factor(self, i: int, j: int) -> float:
        """Calculates adjustment factor based on reasoning weights."""
        # Get relevant actions for these time slots
        action_i = f"schedule_{i}"
        action_j = f"schedule_{j}"
        
        # Get reasoning weights for these actions
        weight_i = self.reasoning_weights.get(action_i, 0.0)
        weight_j = self.reasoning_weights.get(action_j, 0.0)
        
        # Calculate adjustment factor
        if i == j:
            # Diagonal terms - boost based on individual action weight
            return weight_i
        else:
            # Off-diagonal terms - consider interaction between actions
            # Penalize scheduling tasks at positions with high individual weights together
            return -0.5 * weight_i * weight_j
    
    def _validate_dependencies(self, tasks: List[Dict], schedule: Dict[str, int]) -> bool:
        """Validates that schedule respects task dependencies."""
        for task in tasks:
            if 'dependencies' in task:
                task_time = schedule.get(task['id'])
                if task_time is not None:
                    for dep_id in task['dependencies']:
                        dep_time = schedule.get(dep_id)
                        if dep_time is not None and dep_time >= task_time:
                            return False
        return True
    
    def _validate_resources(self, tasks: List[Dict], schedule: Dict[str, int]) -> bool:
        """Validates that schedule respects resource constraints."""
        # Create time slot -> tasks mapping
        time_slots: Dict[int, List[Dict]] = {}
        for task in tasks:
            slot = schedule.get(task['id'])
            if slot is not None:
                if slot not in time_slots:
                    time_slots[slot] = []
                time_slots[slot].append(task)
        
        # Check resource conflicts
        for slot_tasks in time_slots.values():
            resources_used = set()
            for task in slot_tasks:
                if 'resources' in task:
                    task_resources = set(task['resources'])
                    if resources_used & task_resources:  # Intersection not empty
                        return False
                    resources_used.update(task_resources)
        return True
    
    def optimize_schedule_with_reasoning(self, tasks: List[Dict], 
                                      horizon: int,
                                      reasoning_state: QuantumReasoningState) -> Dict:
        """Optimizes schedule incorporating quantum reasoning feedback."""
        if not tasks:
            return {
                'schedule': {},
                'objective_value': 0.0,
                'reasoning_influence': 0.0
            }
            
        # Build QUBO with reasoning
        qubo_terms = self.build_qubo_with_reasoning(horizon, reasoning_state)
        
        # Convert QUBO to matrix form
        Q = np.zeros((horizon, horizon))
        for term in qubo_terms:
            Q[term.i, term.j] = term.weight
            if term.i != term.j:
                Q[term.j, term.i] = term.weight
        
        # Initialize best schedule
        best_schedule = {}
        best_energy = float('inf')
        max_attempts = 100  # Limit optimization attempts
        
        for attempt in range(max_attempts):
            # Generate candidate schedule
            schedule = np.zeros(min(len(tasks), horizon), dtype=int)
            available_slots = list(range(horizon))
            
            for i, task in enumerate(tasks[:horizon]):
                # Consider dependencies
                min_slot = 0
                if 'dependencies' in task:
                    for dep_id in task['dependencies']:
                        for j, dep_task in enumerate(tasks[:horizon]):
                            if dep_task['id'] == dep_id and j < i:
                                min_slot = max(min_slot, schedule[j] + 1)
                
                # Consider resources
                valid_slots = [
                    slot for slot in available_slots 
                    if slot >= min_slot and 
                    self._validate_resources(tasks[:i], {**{t['id']: schedule[j] for j, t in enumerate(tasks[:i])}, task['id']: slot})
                ]
                
                if valid_slots:
                    slot = np.random.choice(valid_slots)
                    schedule[i] = slot
                    available_slots.remove(slot)
                else:
                    # No valid slot found, try next attempt
                    break
            else:
                # Calculate energy for this schedule
                energy = float(schedule @ Q @ schedule)
                
                # Update best schedule if this is better
                if energy < best_energy:
                    best_energy = energy
                    best_schedule = {
                        tasks[i]['id']: int(pos) 
                        for i, pos in enumerate(schedule)
                    }
        
        if not best_schedule:
            # If no valid schedule found, assign sequential slots
            best_schedule = {
                task['id']: i 
                for i, task in enumerate(tasks[:horizon])
            }
            best_energy = float(np.array(list(best_schedule.values())) @ Q @ np.array(list(best_schedule.values())))
        
        return {
            'schedule': best_schedule,
            'objective_value': float(best_energy),
            'reasoning_influence': sum(self.reasoning_weights.values()) / len(self.reasoning_weights) if self.reasoning_weights else 0.0
        }