import pytest
import numpy as np
from qam.crew_interface import EnhancedAgent, DecisionPoint
from qam.quantum_reasoning import Decision, DecisionPath, Outcome

def test_enhanced_agent_initialization():
    agent = EnhancedAgent("test_agent", "test_role")
    assert agent.name == "test_agent"
    assert agent.role == "test_role"
    assert len(agent.decision_history) == 0
    assert agent.reasoning_state is not None
    assert agent.react_engine is not None

def test_agent_decision_making():
    agent = EnhancedAgent("test_agent", "test_role")
    
    context = {
        'available_actions': ['action1', 'action2'],
        'uncertainty': 0.5,
        'timestamp': float(np.datetime64('now').astype('float64'))
    }
    
    decision = agent.make_decision(context)
    
    assert isinstance(decision, Decision)
    assert decision.action in context['available_actions']
    assert len(agent.decision_history) == 1
    assert agent.decision_history[0].decision == decision

def test_agent_reflection():
    agent = EnhancedAgent("test_agent", "test_role")
    
    # Make a decision
    context = {
        'available_actions': ['action1', 'action2'],
        'uncertainty': 0.5,
        'timestamp': float(np.datetime64('now').astype('float64'))
    }
    
    decision = agent.make_decision(context)
    initial_weight = agent.react_engine.decision_weights.get(decision.action, 1.0)
    
    # Create successful outcome
    outcome = Outcome(
        decision_id=decision.id,
        success=True,
        feedback={'action': decision.action},
        timestamp=float(np.datetime64('now').astype('float64'))
    )
    
    # Reflect on outcome
    agent.reflect_on_outcome(outcome)
    
    # Verify reflection
    assert agent.decision_history[0].outcome == outcome
    assert agent.react_engine.decision_weights[decision.action] > initial_weight

def test_context_similarity():
    agent = EnhancedAgent("test_agent", "test_role")
    
    context1 = {
        'available_actions': ['action1', 'action2'],
        'uncertainty': 0.5,
        'environment': 'test'
    }
    
    context2 = {
        'available_actions': ['action1', 'action3'],
        'uncertainty': 0.5,
        'environment': 'test'
    }
    
    # Should be similar but not identical
    similarity = agent._context_similarity(context1, context2)
    assert 0 < similarity < 1
    
    # Same context should have similarity 1
    assert agent._context_similarity(context1, context1) == 1.0
    
    # Different contexts should have low similarity
    different_context = {
        'available_actions': ['action4', 'action5'],
        'uncertainty': 0.1,
        'environment': 'prod'
    }
    assert agent._context_similarity(context1, different_context) < 0.5

def test_decision_confidence():
    agent = EnhancedAgent("test_agent", "test_role")
    
    context = {
        'available_actions': ['action1', 'action2'],
        'uncertainty': 0.5,
        'environment': 'test',
        'timestamp': float(np.datetime64('now').astype('float64'))
    }
    
    # Initial confidence should be default
    initial_confidence = agent.get_decision_confidence(context)
    assert initial_confidence == 0.5
    
    # Make some decisions and provide outcomes
    for _ in range(3):
        decision = agent.make_decision(context)
        outcome = Outcome(
            decision_id=decision.id,
            success=True,  # All successful
            feedback={'action': decision.action},
            timestamp=float(np.datetime64('now').astype('float64'))
        )
        agent.reflect_on_outcome(outcome)
    
    # Confidence should be higher now
    new_confidence = agent.get_decision_confidence(context)
    assert new_confidence > initial_confidence

def test_performance_metrics():
    agent = EnhancedAgent("test_agent", "test_role")
    
    # Initial metrics should be zeros
    initial_metrics = agent.get_performance_metrics()
    assert initial_metrics['success_rate'] == 0.0
    assert initial_metrics['decision_count'] == 0
    
    context = {
        'available_actions': ['action1', 'action2'],
        'uncertainty': 0.5,
        'timestamp': float(np.datetime64('now').astype('float64'))
    }
    
    # Make some decisions with mixed outcomes
    for i in range(4):
        decision = agent.make_decision(context)
        outcome = Outcome(
            decision_id=decision.id,
            success=(i % 2 == 0),  # Alternate between success and failure
            feedback={'action': decision.action},
            timestamp=float(np.datetime64('now').astype('float64'))
        )
        agent.reflect_on_outcome(outcome)
    
    metrics = agent.get_performance_metrics()
    assert metrics['decision_count'] == 4
    assert metrics['success_rate'] == 0.5  # Half successful
    assert 0 <= metrics['average_confidence'] <= 1.0

def test_agent_learning():
    agent = EnhancedAgent("test_agent", "test_role")
    np.random.seed(42)  # For reproducibility
    
    context = {
        'available_actions': ['action1', 'action2'],
        'uncertainty': 0.5,
        'timestamp': float(np.datetime64('now').astype('float64'))
    }
    
    # Track action selection frequencies
    action_counts = {'action1': 0, 'action2': 0}
    
    # Initial phase - record baseline action selection
    for _ in range(5):
        decision = agent.make_decision(context)
        action_counts[decision.action] += 1
    
    initial_ratio = action_counts['action1'] / (action_counts['action2'] + 1e-10)
    
    # Learning phase - make action1 always successful, action2 always fail
    action_counts = {'action1': 0, 'action2': 0}
    
    for _ in range(10):
        decision = agent.make_decision(context)
        action_counts[decision.action] += 1
        
        outcome = Outcome(
            decision_id=decision.id,
            success=(decision.action == 'action1'),  # action1 always succeeds
            feedback={'action': decision.action},
            timestamp=float(np.datetime64('now').astype('float64'))
        )
        agent.reflect_on_outcome(outcome)
    
    final_ratio = action_counts['action1'] / (action_counts['action2'] + 1e-10)
    
    # Agent should learn to prefer action1
    assert final_ratio > initial_ratio