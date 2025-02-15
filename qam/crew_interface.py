from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .quantum_reasoning import (
    QuantumReasoningState,
    QuantumReACT,
    Decision,
    DecisionPath,
    Outcome
)

@dataclass
class DecisionPoint:
    """Represents a point where a decision was made."""
    timestamp: float
    context: Dict[str, Any]
    decision: Decision
    outcome: Optional[Outcome] = None

class EnhancedAgent:
    """Agent with quantum reasoning capabilities."""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.reasoning_state = QuantumReasoningState()
        self.decision_history: List[DecisionPoint] = []
        self.react_engine = QuantumReACT()
        
    def make_decision(self, context: Dict[str, Any]) -> Decision:
        """Makes a decision using quantum reasoning."""
        decision = self.react_engine.make_decision(context, self.reasoning_state)
        
        # Record decision point
        self.decision_history.append(DecisionPoint(
            timestamp=float(context.get('timestamp', 0)),
            context=context,
            decision=decision
        ))
        
        return decision
    
    def reflect_on_outcome(self, outcome: Outcome) -> None:
        """Processes the outcome of a decision and updates reasoning."""
        # Find corresponding decision point
        for point in self.decision_history:
            if point.decision.id == outcome.decision_id:
                point.outcome = outcome
                break
                
        # Update reasoning based on outcome
        self.react_engine.reflect_and_adjust(outcome, self.reasoning_state)
    
    def get_decision_confidence(self, context: Dict[str, Any]) -> float:
        """Estimates confidence for a potential decision in the given context."""
        similar_decisions = [
            point for point in self.decision_history
            if self._context_similarity(point.context, context) > 0.7
        ]
        
        if not similar_decisions:
            return 0.5  # Default confidence when no similar decisions
            
        # Calculate confidence based on similar decision outcomes
        success_rate = sum(
            1 for d in similar_decisions
            if d.outcome and d.outcome.success
        ) / len(similar_decisions)
        
        return success_rate
    
    def _context_similarity(self, context1: Dict[str, Any], 
                          context2: Dict[str, Any]) -> float:
        """Calculates similarity between two contexts."""
        # Get common keys
        common_keys = set(context1.keys()) & set(context2.keys())
        if not common_keys:
            return 0.0
            
        # Calculate similarity for each common key
        similarities = []
        for key in common_keys:
            if isinstance(context1[key], (list, tuple)) and \
               isinstance(context2[key], (list, tuple)):
                # Compare lists/tuples
                common_items = set(context1[key]) & set(context2[key])
                total_items = set(context1[key]) | set(context2[key])
                if total_items:
                    similarities.append(len(common_items) / len(total_items))
            elif context1[key] == context2[key]:
                similarities.append(1.0)
            else:
                similarities.append(0.0)
                
        # Return average similarity
        return sum(similarities) / len(similarities)
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Calculates agent performance metrics."""
        if not self.decision_history:
            return {
                'success_rate': 0.0,
                'average_confidence': 0.0,
                'decision_count': 0
            }
            
        # Calculate metrics
        decisions_with_outcomes = [
            d for d in self.decision_history if d.outcome is not None
        ]
        
        if not decisions_with_outcomes:
            return {
                'success_rate': 0.0,
                'average_confidence': sum(d.decision.confidence for d in self.decision_history) / len(self.decision_history),
                'decision_count': len(self.decision_history)
            }
            
        success_rate = sum(
            1 for d in decisions_with_outcomes if d.outcome.success
        ) / len(decisions_with_outcomes)
        
        return {
            'success_rate': success_rate,
            'average_confidence': sum(d.decision.confidence for d in self.decision_history) / len(self.decision_history),
            'decision_count': len(self.decision_history)
        }