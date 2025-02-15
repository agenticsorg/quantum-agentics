import unittest
from datetime import datetime, timedelta
from qam.orchestration_protocol import QuantumOrchestrationProtocol, Message

class TestQuantumOrchestrationProtocol(unittest.TestCase):
    def setUp(self):
        self.protocol = QuantumOrchestrationProtocol()
        
        # Register test components
        self.protocol.register_component('component1', {
            'test_message': 'component2'
        })
        self.protocol.register_component('component2', {})  # End destination
        self.protocol.register_component('component3', {})
        
    def test_get_component_messages(self):
        # Send first message
        msg1_id = self.protocol.send_message(
            source='component1',
            destination='component2',
            message_type='test_message',
            payload={'data': 'test1'}
        )
        
        # Send second message
        msg2_id = self.protocol.send_message(
            source='component1',
            destination='component2',
            message_type='test_message',
            payload={'data': 'test2'}
        )
        
        # Route both messages
        self.protocol.route_message()
        self.protocol.route_message()
        
        # Get messages for component2
        received_messages = self.protocol.get_component_messages('component2')
        
        # Print debug information
        print(f"\nDelivery history: {self.protocol.delivery_history}")
        print(f"Received messages: {received_messages}")
        
        # Verify message count
        self.assertEqual(len(received_messages), 2)
        
        # Verify message content
        received_data = [m.payload['data'] for m in received_messages]
        self.assertIn('test1', received_data)
        self.assertIn('test2', received_data)
        
    def test_register_component(self):
        # Test registering new component
        success = self.protocol.register_component('new_component', {})
        self.assertTrue(success)
        self.assertIn('new_component', self.protocol.routing_table)
        
        # Test registering duplicate component
        success = self.protocol.register_component('component1', {})
        self.assertFalse(success)
        
    def test_register_handler(self):
        def test_handler(message):
            pass
            
        # Test registering new handler
        success = self.protocol.register_handler('test_type', test_handler)
        self.assertTrue(success)
        self.assertIn('test_type', self.protocol.handlers)
        
        # Test registering duplicate handler
        success = self.protocol.register_handler('test_type', test_handler)
        self.assertFalse(success)
        
    def test_send_message(self):
        # Test sending valid message
        message_id = self.protocol.send_message(
            source='component1',
            destination='component2',
            message_type='test_message',
            payload={'data': 'test'}
        )
        self.assertIsNotNone(message_id)
        
        # Test sending from invalid source
        message_id = self.protocol.send_message(
            source='invalid_component',
            destination='component2',
            message_type='test_message',
            payload={'data': 'test'}
        )
        self.assertIsNone(message_id)
        
    def test_route_message(self):
        # Send test message
        message_id = self.protocol.send_message(
            source='component1',
            destination='component2',
            message_type='test_message',
            payload={'data': 'test'}
        )
        
        # Test routing
        success = self.protocol.route_message()
        self.assertTrue(success)
        
        # Verify message was delivered
        message_status = self.protocol.get_message_status(message_id)
        self.assertEqual(message_status, 'delivered')
        
    def test_message_handler(self):
        # Setup test handler
        handled_messages = []
        def test_handler(message):
            handled_messages.append(message)
            
        self.protocol.register_handler('test_type', test_handler)
        
        # Send message with registered type
        self.protocol.send_message(
            source='component1',
            destination='component2',
            message_type='test_type',
            payload={'data': 'test'}
        )
        
        # Route message
        self.protocol.route_message()
        
        # Verify handler was called
        self.assertEqual(len(handled_messages), 1)
        self.assertEqual(handled_messages[0].message_type, 'test_type')
        
    def test_message_priority(self):
        # Send messages with different priorities
        self.protocol.send_message(
            source='component1',
            destination='component2',
            message_type='test_message',
            payload={'data': 'low_priority'},
            priority=2
        )
        
        high_priority_id = self.protocol.send_message(
            source='component1',
            destination='component2',
            message_type='test_message',
            payload={'data': 'high_priority'},
            priority=1
        )
        
        # Route first message
        self.protocol.route_message()
        
        # Verify high priority message was routed first
        message_status = self.protocol.get_message_status(high_priority_id)
        self.assertEqual(message_status, 'delivered')
        
    def test_component_status(self):
        # Test updating status
        success = self.protocol.update_component_status('component1', 'inactive')
        self.assertTrue(success)
        
        # Send message to inactive component
        message_id = self.protocol.send_message(
            source='component2',
            destination='component1',
            message_type='test_message',
            payload={'data': 'test'}
        )
        
        # Route message
        self.protocol.route_message()
        
        # Verify message failed
        message_status = self.protocol.get_message_status(message_id)
        self.assertEqual(message_status, 'failed')
        
    def test_clear_history(self):
        # Send and route a message
        self.protocol.send_message(
            source='component1',
            destination='component2',
            message_type='test_message',
            payload={'data': 'test'}
        )
        self.protocol.route_message()
        
        # Clear history
        cleared_count = self.protocol.clear_history()
        self.assertEqual(cleared_count, 1)
        self.assertEqual(len(self.protocol.delivery_history), 0)
        
    def test_clear_history_with_age(self):
        # Create old message
        old_message = Message(
            id='old',
            source='component1',
            destination='component2',
            message_type='test',
            payload={'data': 'old'},
            timestamp=datetime.now() - timedelta(hours=2)
        )
        self.protocol.delivery_history.append(old_message)
        
        # Create new message
        self.protocol.send_message(
            source='component1',
            destination='component2',
            message_type='test_message',
            payload={'data': 'new'}
        )
        self.protocol.route_message()
        
        # Clear messages older than 1 hour
        cleared_count = self.protocol.clear_history(age_hours=1)
        self.assertEqual(cleared_count, 1)
        self.assertEqual(len(self.protocol.delivery_history), 1)

if __name__ == '__main__':
    unittest.main()