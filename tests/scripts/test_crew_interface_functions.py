#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

from unittest.mock import Mock, patch
from qam.crew_interface import DecisionPoint, EnhancedAgent
from qam.quantum_reasoning import Decision, Outcome, DecisionPath

# Mock classes and functions
class MockQuantumReasoningState:
    def __init__(self):
        self.state = {}

class MockQuantumReACT:
    def make_decision(self, context, state):
        path = DecisionPath(
            id="test-path-1",
            probability=0.8,
            actions=["test-action"]
        )
        return Decision(
            id="test-decision-1",
            action="test-action",
            confidence=0.8,
            path=path
        )
        
    def reflect_and_adjust(self, outcome, state):
        pass

def test_enhanced_agent():
    print("\nTesting EnhancedAgent...")
    
    with patch('qam.crew_interface.QuantumReasoningState', MockQuantumReasoningState), \
         patch('qam.crew_interface.QuantumReACT', MockQuantumReACT):
        
        # Test 1: Create agent
        print("\n1. Testing agent creation")
        agent = EnhancedAgent("test-agent", "test-role")
        print(f"Agent created: {agent.name}, Role: {agent.role}")
        
        # Test 2: Make decision
        print("\n2. Testing decision making")
        context = {
            "timestamp": 1234567890.0,
            "task": "test-task",
            "parameters": {"param1": "value1"}
        }
        decision = agent.make_decision(context)
        print(f"Decision made: {decision.action} with confidence {decision.confidence}")
        assert len(agent.decision_history) == 1
        
        # Test 3: Reflect on outcome
        print("\n3. Testing outcome reflection")
        outcome = Outcome(
            decision_id=decision.id,
            success=True,
            feedback={"action": "test-action"},
            timestamp=1234567890.0
        )
        agent.reflect_on_outcome(outcome)
        assert agent.decision_history[0].outcome == outcome
        print("Outcome reflected successfully")
        
        # Test 4: Get decision confidence
        print("\n4. Testing decision confidence")
        # First with no similar contexts
        new_context = {"task": "different-task"}
        confidence = agent.get_decision_confidence(new_context)
        print(f"Confidence for new context: {confidence}")
        assert confidence == 0.5  # Default confidence
        
        # Then with similar context
        similar_context = context.copy()
        similar_confidence = agent.get_decision_confidence(similar_context)
        print(f"Confidence for similar context: {similar_confidence}")
        
        # Test 5: Context similarity
        print("\n5. Testing context similarity")
        context1 = {"a": [1, 2, 3], "b": "test"}
        context2 = {"a": [2, 3, 4], "b": "test"}
        similarity = agent._context_similarity(context1, context2)
        print(f"Context similarity: {similarity}")
        assert 0 <= similarity <= 1
        
        # Test 6: Performance metrics
        print("\n6. Testing performance metrics")
        metrics = agent.get_performance_metrics()
        print("Performance metrics:", metrics)
        assert "success_rate" in metrics
        assert "average_confidence" in metrics
        assert "decision_count" in metrics
        
        # Test 7: Multiple decisions and outcomes
        print("\n7. Testing multiple decisions")
        for i in range(3):
            decision = agent.make_decision({"task": f"task-{i}"})
            outcome = Outcome(
                decision_id=decision.id,
                success=i % 2 == 0,  # Alternate success/failure
                feedback={"action": f"test-action-{i}"},
                timestamp=1234567890.0 + i
            )
            agent.reflect_on_outcome(outcome)
        
        final_metrics = agent.get_performance_metrics()
        print("Final metrics after multiple decisions:", final_metrics)
        assert final_metrics["decision_count"] == 4  # 1 from earlier + 3 new ones

if __name__ == "__main__":
    try:
        test_enhanced_agent()
        print("\n✅ All crew interface tests completed successfully")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")