import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import uuid

@dataclass
class DecisionPath:
    """Represents a possible decision path in the quantum reasoning space."""
    id: str
    probability: float
    actions: List[str]
    
    def __hash__(self):
        return hash(self.id)

@dataclass
class Decision:
    """Represents a concrete decision made by the quantum reasoning system."""
    id: str
    action: str
    confidence: float
    path: DecisionPath

@dataclass
class Outcome:
    """Represents the outcome of a decision."""
    decision_id: str
    success: bool
    feedback: Dict[str, Any]
    timestamp: float

class QuantumReasoningState:
    """Represents the quantum state of agent reasoning."""
    
    def __init__(self):
        self.amplitudes: Dict[DecisionPath, complex] = {}
        self.history: List[Tuple[Dict[DecisionPath, complex], float]] = []
        self._validate_state()
    
    def _validate_state(self) -> None:
        """Ensures the quantum state maintains proper normalization."""
        total_probability = sum(abs(amp) ** 2 for amp in self.amplitudes.values())
        if self.amplitudes and not np.isclose(total_probability, 1.0, atol=1e-10):
            # Normalize if needed
            normalization_factor = 1.0 / np.sqrt(total_probability)
            self.amplitudes = {
                path: amp * normalization_factor 
                for path, amp in self.amplitudes.items()
            }
    
    def add_decision_path(self, path: DecisionPath, amplitude: complex) -> None:
        """Adds a new decision path to the quantum state."""
        self.amplitudes[path] = amplitude
        self._validate_state()
    
    def evolve(self, hamiltonian: np.ndarray) -> None:
        """Evolves the quantum state according to the given Hamiltonian."""
        if not self.amplitudes:
            return
            
        # Convert state to vector form
        paths = sorted(self.amplitudes.keys(), key=lambda x: x.id)
        state_vector = np.array([self.amplitudes[p] for p in paths])
        
        # Validate hamiltonian dimensions
        if hamiltonian.size == 0:
            return
            
        if hamiltonian.shape != (len(paths), len(paths)):
            # Extend hamiltonian or state vector as needed
            n = max(len(paths), hamiltonian.shape[0])
            extended_hamiltonian = np.eye(n)
            if hamiltonian.size > 0:
                extended_hamiltonian[:hamiltonian.shape[0], :hamiltonian.shape[1]] = hamiltonian
            
            # Extend state vector if needed
            if len(state_vector) < n:
                extended_state = np.zeros(n, dtype=complex)
                extended_state[:len(state_vector)] = state_vector
                state_vector = extended_state
                
            hamiltonian = extended_hamiltonian
            
        # Evolve state
        new_state = hamiltonian @ state_vector
        
        # Update amplitudes
        self.amplitudes = {
            path: new_state[i] 
            for i, path in enumerate(paths)
        }
        
        # Save state to history with timestamp
        self.history.append((
            self.amplitudes.copy(),
            float(np.datetime64('now').astype('float64'))
        ))
        
        self._validate_state()
    
    def measure(self) -> DecisionPath:
        """Collapses the quantum state to a specific decision path."""
        if not self.amplitudes:
            raise ValueError("No decision paths in quantum state")
            
        # Calculate probabilities
        probabilities = {
            path: float(abs(amp) ** 2)
            for path, amp in self.amplitudes.items()
        }
        
        # Normalize probabilities
        total_prob = sum(probabilities.values())
        probabilities = {
            path: prob/total_prob 
            for path, prob in probabilities.items()
        }
        
        # Random selection based on probabilities
        paths = list(probabilities.keys())
        probs = [probabilities[p] for p in paths]
        selected_idx = np.random.choice(len(paths), p=probs)
        selected_path = paths[selected_idx]
        
        # Collapse state to selected path
        self.amplitudes = {selected_path: 1.0}
        self._validate_state()
        
        return selected_path
    
    def get_state_vector(self) -> np.ndarray:
        """Returns the current state as a numpy array."""
        return np.array([
            self.amplitudes[p] for p in sorted(self.amplitudes.keys(), key=lambda x: x.id)
        ])
    
    def get_probabilities(self) -> Dict[DecisionPath, float]:
        """Returns the probability distribution over decision paths."""
        return {
            path: float(abs(amp) ** 2)
            for path, amp in self.amplitudes.items()
        }

class QuantumReACT:
    """Core reasoning engine using quantum-inspired algorithms."""
    
    def __init__(self):
        self.outcomes: List[Outcome] = []
        self.decision_weights: Dict[str, float] = {}  # Action -> weight mapping
        self.learning_rate = 0.2  # Controls how quickly weights are adjusted
    
    def _generate_decision_paths(self, context: Dict) -> List[DecisionPath]:
        """Generates possible decision paths based on context."""
        paths = []
        available_actions = context.get('available_actions', [])
        
        if not available_actions:
            return paths
            
        # Initialize weights for new actions
        for action in available_actions:
            if action not in self.decision_weights:
                self.decision_weights[action] = 1.0
        
        total_weight = sum(self.decision_weights[a] for a in available_actions)
        
        for action in available_actions:
            # Generate probability based on historical performance
            adjusted_prob = self.decision_weights[action] / total_weight
            
            path = DecisionPath(
                id=str(uuid.uuid4()),
                probability=adjusted_prob,
                actions=[action]
            )
            paths.append(path)
            
        return paths
    
    def _create_evolution_hamiltonian(self, context: Dict) -> np.ndarray:
        """Creates a Hamiltonian operator for state evolution."""
        n_paths = len(context.get('available_actions', []))
        if n_paths == 0:
            return np.array([])
            
        # Create a rotation-based Hamiltonian
        # The angle of rotation is influenced by context factors
        theta = np.pi * context.get('uncertainty', 0.5)
        
        if n_paths == 1:
            return np.array([[1.0]])
            
        # Base 2x2 rotation matrix
        base_hamiltonian = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)]
        ])
        
        # Extend to full state space if needed
        if n_paths > 2:
            extended = np.eye(n_paths)
            extended[:2, :2] = base_hamiltonian
            return extended
            
        return base_hamiltonian
    
    def make_decision(self, context: Dict, state: QuantumReasoningState) -> Decision:
        """Generates and evolves possible decisions to make a choice."""
        # Generate possible decision paths
        paths = self._generate_decision_paths(context)
        
        if not paths:
            raise ValueError("No available actions in context")
            
        # Initialize quantum state with paths
        for path in paths:
            state.add_decision_path(path, np.sqrt(path.probability))
            
        # Evolve state based on context
        hamiltonian = self._create_evolution_hamiltonian(context)
        if hamiltonian.size > 0:  # Only evolve if we have a valid hamiltonian
            state.evolve(hamiltonian)
        
        # Measure to get concrete decision
        selected_path = state.measure()
        
        # Create decision with confidence based on probability
        probabilities = state.get_probabilities()
        confidence = probabilities.get(selected_path, 0.0)
        
        return Decision(
            id=str(uuid.uuid4()),
            action=selected_path.actions[0],
            confidence=confidence,
            path=selected_path
        )
    
    def reflect_and_adjust(self, outcome: Outcome, state: QuantumReasoningState) -> None:
        """Updates reasoning based on decision outcomes."""
        self.outcomes.append(outcome)
        
        # Update weights based on success/failure
        action = outcome.feedback.get('action')
        if action:
            current_weight = self.decision_weights.get(action, 1.0)
            
            # Calculate adjustment factor based on outcome
            adjustment = 1.0 + (self.learning_rate if outcome.success else -self.learning_rate)
            new_weight = current_weight * adjustment
            
            # Ensure weight stays above minimum threshold
            self.decision_weights[action] = max(new_weight, 0.1)
            
            # Normalize weights to maintain relative scale
            total_weight = sum(self.decision_weights.values())
            if total_weight > 0:
                scale_factor = len(self.decision_weights) / total_weight
                self.decision_weights = {
                    k: v * scale_factor 
                    for k, v in self.decision_weights.items()
                }