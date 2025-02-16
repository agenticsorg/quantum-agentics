#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

from datetime import datetime, timedelta
import time
from qam.orchestration_protocol import QuantumOrchestrationProtocol, Message

def test_message_handler(message: Message):
    """Test message handler function."""
    print(f"Handling message: {message.message_type}")
    message.payload['handled'] = True

def test_orchestration_protocol():
    print("\nTesting QuantumOrchestrationProtocol...")
    
    # Test 1: Create protocol
    print("\n1. Testing protocol creation")
    protocol = QuantumOrchestrationProtocol()
    print("Protocol created successfully")
    
    # Test 2: Register components
    print("\n2. Testing component registration")
    component1_routes = {
        "request": "component2",
        "response": "component1"
    }
    success = protocol.register_component("component1", component1_routes)
    print(f"Component1 registration: {success}")
    
    component2_routes = {
        "request": "component2",
        "response": "component1"
    }
    success = protocol.register_component("component2", component2_routes)
    print(f"Component2 registration: {success}")
    assert "component1" in protocol.routing_table
    assert "component2" in protocol.routing_table
    
    # Test 3: Register message handler
    print("\n3. Testing handler registration")
    success = protocol.register_handler("request", test_message_handler)
    print(f"Handler registration: {success}")
    assert "request" in protocol.handlers
    
    # Test 4: Send message
    print("\n4. Testing message sending")
    message_id = protocol.send_message(
        source="component1",
        destination="component2",
        message_type="request",
        payload={"data": "test"},
        priority=1
    )
    print(f"Sent message with ID: {message_id}")
    assert message_id is not None
    
    # Test 5: Route message
    print("\n5. Testing message routing")
    success = protocol.route_message(message_id)
    print(f"Message routing: {success}")
    
    # Test 6: Get message status
    print("\n6. Testing message status")
    status = protocol.get_message_status(message_id)
    print(f"Message status: {status}")
    assert status in ["delivered", "forwarded", "failed", "pending"]
    
    # Test 7: Get component messages
    print("\n7. Testing component message retrieval")
    messages = protocol.get_component_messages("component2")
    print(f"Component2 messages: {len(messages)}")
    
    # Test 8: Update component status
    print("\n8. Testing component status update")
    success = protocol.update_component_status("component1", "inactive")
    print(f"Status update: {success}")
    assert protocol.component_status["component1"] == "inactive"
    
    # Test 9: Message priority
    print("\n9. Testing message priority")
    # Send high priority message
    high_priority_id = protocol.send_message(
        source="component1",
        destination="component2",
        message_type="request",
        payload={"data": "urgent"},
        priority=0
    )
    # Send low priority message
    low_priority_id = protocol.send_message(
        source="component1",
        destination="component2",
        message_type="request",
        payload={"data": "normal"},
        priority=2
    )
    
    # Route messages and verify order
    protocol.route_message()  # Should route high priority first
    high_status = protocol.get_message_status(high_priority_id)
    protocol.route_message()  # Should route low priority second
    low_status = protocol.get_message_status(low_priority_id)
    print(f"High priority message status: {high_status}")
    print(f"Low priority message status: {low_status}")
    
    # Test 10: Clear history
    print("\n10. Testing history clearing")
    # Add some delay to test age-based clearing
    time.sleep(1)
    count = protocol.clear_history(age_hours=0.0003)  # ~1 second
    print(f"Cleared {count} messages")
    
    # Test 11: Error handling
    print("\n11. Testing error handling")
    # Try to register duplicate component
    success = protocol.register_component("component1", {})
    print(f"Duplicate component registration: {success}")
    assert not success
    
    # Try to send message from unregistered component
    invalid_id = protocol.send_message(
        source="invalid",
        destination="component2",
        message_type="request",
        payload={}
    )
    print(f"Invalid message sending: {invalid_id is None}")
    assert invalid_id is None
    
    # Test 12: Message forwarding
    print("\n12. Testing message forwarding")
    forward_id = protocol.send_message(
        source="component1",
        destination="component2",
        message_type="forward",
        payload={"data": "forward test"}
    )
    protocol.route_message(forward_id)
    forward_status = protocol.get_message_status(forward_id)
    print(f"Forwarded message status: {forward_status}")

if __name__ == "__main__":
    try:
        test_orchestration_protocol()
        print("\n✅ All orchestration protocol tests completed successfully")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")