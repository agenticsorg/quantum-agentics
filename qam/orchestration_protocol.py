from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import queue
import uuid
import copy

@dataclass
class Message:
    """Represents a message in the orchestration system."""
    id: str
    source: str
    destination: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = datetime.now()
    priority: int = 0
    status: str = "pending"
    
    def __lt__(self, other: 'Message') -> bool:
        """Enable comparison for priority queue ordering."""
        return False  # Messages with same priority maintain FIFO order

class QuantumOrchestrationProtocol:
    """Manages communication between system components."""
    
    def __init__(self):
        self.message_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.routing_table: Dict[str, Dict[str, str]] = {}
        self.handlers: Dict[str, callable] = {}
        self.delivery_history: List[Message] = []
        self.component_status: Dict[str, str] = {}
        
    def register_component(self, component_id: str, 
                         routes: Dict[str, str]) -> bool:
        """
        Register a component with its routing information.
        
        Args:
            component_id: Unique identifier for the component
            routes: Dictionary mapping message types to destinations
            
        Returns:
            bool: Success status of registration
        """
        if component_id in self.routing_table:
            return False
            
        self.routing_table[component_id] = routes
        self.component_status[component_id] = "active"
        return True
        
    def register_handler(self, message_type: str, 
                        handler: callable) -> bool:
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Callback function to handle messages
            
        Returns:
            bool: Success status of registration
        """
        if message_type in self.handlers:
            return False
            
        self.handlers[message_type] = handler
        return True
        
    def send_message(self, source: str, destination: str,
                    message_type: str, payload: Dict[str, Any],
                    priority: int = 0) -> Optional[str]:
        """
        Send a message through the system.
        
        Args:
            source: Component sending the message
            destination: Target component
            message_type: Type of message
            payload: Message content
            priority: Message priority (lower is higher priority)
            
        Returns:
            Optional[str]: Message ID if successful
        """
        if source not in self.routing_table:
            return None
            
        if destination not in self.routing_table:
            return None
            
        message = Message(
            id=str(uuid.uuid4()),
            source=source,
            destination=destination,
            message_type=message_type,
            payload=payload,
            priority=priority
        )
        
        # Add to priority queue as tuple (priority, timestamp, message)
        # This ensures stable ordering within same priority level
        self.message_queue.put((priority, datetime.now(), message))
        return message.id
        
    def route_message(self, message_id: Optional[str] = None) -> bool:
        """
        Route messages between system components.
        
        Args:
            message_id: Optional specific message to route
            
        Returns:
            bool: Success status of routing
        """
        if self.message_queue.empty():
            return False
            
        # Get next message
        _, _, message = self.message_queue.get()
        
        if message_id is not None and message.id != message_id:
            # Put message back if it's not the requested one
            self.message_queue.put((message.priority, message.timestamp, message))
            return False
            
        # Check if destination is active
        if self.component_status.get(message.destination) != "active":
            message.status = "failed"
            self.delivery_history.append(message)
            return False
            
        # Handle message
        if message.message_type in self.handlers:
            try:
                self.handlers[message.message_type](message)
                message.status = "delivered"
                self.delivery_history.append(message)
            except Exception as e:
                message.status = "failed"
                message.payload['error'] = str(e)
                self.delivery_history.append(message)
        else:
            # Forward message based on routing table
            routes = self.routing_table[message.destination]
            if message.message_type in routes:
                # Keep record of current delivery
                current_delivery = copy.deepcopy(message)
                current_delivery.status = "forwarded"
                self.delivery_history.append(current_delivery)
                
                # Forward to next destination
                next_destination = routes[message.message_type]
                if next_destination in self.routing_table:
                    message.destination = next_destination
                    message.status = "pending"
                    self.message_queue.put((message.priority, message.timestamp, message))
                else:
                    message.status = "unroutable"
                    self.delivery_history.append(message)
            else:
                message.status = "delivered"  # Message reached final destination
                self.delivery_history.append(message)
                
        return True
        
    def get_message_status(self, message_id: str) -> Optional[str]:
        """
        Get the status of a specific message.
        
        Args:
            message_id: ID of the message to check
            
        Returns:
            Optional[str]: Message status if found
        """
        for message in self.delivery_history:
            if message.id == message_id:
                return message.status
        return None
        
    def get_component_messages(self, component_id: str,
                             status: Optional[str] = None) -> List[Message]:
        """
        Get messages for a specific component.
        
        Args:
            component_id: ID of the component
            status: Optional status to filter by
            
        Returns:
            List[Message]: List of matching messages
        """
        messages = []
        for message in self.delivery_history:
            if message.destination == component_id:
                if status is None or message.status == status:
                    messages.append(message)
        return messages
        
    def update_component_status(self, component_id: str,
                              status: str) -> bool:
        """
        Update the status of a component.
        
        Args:
            component_id: ID of the component
            status: New status
            
        Returns:
            bool: Success status of update
        """
        if component_id not in self.component_status:
            return False
            
        self.component_status[component_id] = status
        return True
        
    def clear_history(self, age_hours: Optional[float] = None) -> int:
        """
        Clear message delivery history.
        
        Args:
            age_hours: Optional age in hours to clear
            
        Returns:
            int: Number of messages cleared
        """
        if age_hours is None:
            count = len(self.delivery_history)
            self.delivery_history.clear()
            return count
            
        current_time = datetime.now()
        new_history = []
        cleared_count = 0
        
        for message in self.delivery_history:
            age = (current_time - message.timestamp).total_seconds() / 3600
            if age <= age_hours:
                new_history.append(message)
            else:
                cleared_count += 1
                
        self.delivery_history = new_history
        return cleared_count