from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ResourceAllocation:
    """Represents a resource allocation record."""
    resource_id: str
    cluster_id: str
    amount: float
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "active"

class ResourceManager:
    """Handles resource allocation across agent clusters."""
    
    def __init__(self):
        self.resource_pools: Dict[str, Dict] = {}
        self.allocation_history: List[ResourceAllocation] = []
        self.optimization_parameters: Dict[str, float] = {
            'utilization_target': 0.8,  # Target utilization rate (80%)
            'balance_factor': 0.5,
            'allocation_threshold': 0.05,  # Threshold for optimization (5%)
            'reduction_factor': 0.7,  # Reduce over-utilized resources by 30%
            'increase_factor': 1.2   # Increase under-utilized resources by 20%
        }
        
    def add_resource_pool(self, pool_id: str, capacity: float, 
                         resource_type: str) -> bool:
        """
        Add a new resource pool to the manager.
        
        Args:
            pool_id: Unique identifier for the pool
            capacity: Total resource capacity
            resource_type: Type of resource (e.g., 'cpu', 'memory')
            
        Returns:
            bool: Success status of the operation
        """
        if pool_id in self.resource_pools:
            return False
            
        self.resource_pools[pool_id] = {
            'capacity': capacity,
            'available': capacity,
            'type': resource_type,
            'allocations': {}
        }
        return True
        
    def allocate_resource(self, pool_id: str, cluster_id: str, 
                         amount: float) -> Optional[ResourceAllocation]:
        """
        Allocate resources from a pool to a cluster.
        
        Args:
            pool_id: ID of the resource pool
            cluster_id: ID of the cluster requesting resources
            amount: Amount of resource to allocate
            
        Returns:
            Optional[ResourceAllocation]: Allocation record if successful
        """
        if pool_id not in self.resource_pools:
            return None
            
        pool = self.resource_pools[pool_id]
        if pool['available'] < amount:
            return None
            
        # Create allocation
        allocation = ResourceAllocation(
            resource_id=pool_id,
            cluster_id=cluster_id,
            amount=amount
        )
        
        # Update pool
        pool['available'] -= amount
        pool['allocations'][cluster_id] = pool['allocations'].get(cluster_id, 0) + amount
        
        # Record allocation
        self.allocation_history.append(allocation)
        
        return allocation
        
    def release_resource(self, pool_id: str, cluster_id: str, 
                        amount: Optional[float] = None) -> bool:
        """
        Release allocated resources back to the pool.
        
        Args:
            pool_id: ID of the resource pool
            cluster_id: ID of the cluster releasing resources
            amount: Amount to release (None for all)
            
        Returns:
            bool: Success status of the operation
        """
        if pool_id not in self.resource_pools:
            return False
            
        pool = self.resource_pools[pool_id]
        current_allocation = pool['allocations'].get(cluster_id, 0)
        
        if current_allocation == 0:
            return False
            
        release_amount = amount if amount is not None else current_allocation
        if release_amount > current_allocation:
            return False
            
        # Update pool
        pool['available'] += release_amount
        pool['allocations'][cluster_id] -= release_amount
        
        if pool['allocations'][cluster_id] == 0:
            del pool['allocations'][cluster_id]
            
        # Update allocation history
        for allocation in reversed(self.allocation_history):
            if (allocation.resource_id == pool_id and 
                allocation.cluster_id == cluster_id and 
                allocation.status == "active"):
                allocation.status = "released"
                break
                
        return True
        
    def optimize_allocations(self) -> Dict[str, Dict[str, float]]:
        """
        Use QAOA for resource distribution optimization.
        
        Returns:
            Dict[str, Dict[str, float]]: Optimized resource allocations
        """
        if not self.resource_pools:
            return {}
            
        # Calculate current utilization
        utilization = self._calculate_utilization()
        optimized_allocations = {}
        
        for pool_id, util in utilization.items():
            pool = self.resource_pools[pool_id]
            pool_allocations = {}
            
            # Check if pool needs optimization
            if util > self.optimization_parameters['utilization_target'] + self.optimization_parameters['allocation_threshold']:
                # Over-utilized: reduce allocations
                for cluster_id, amount in pool['allocations'].items():
                    reduced_amount = amount * self.optimization_parameters['reduction_factor']
                    pool_allocations[cluster_id] = reduced_amount
                    
            elif util < self.optimization_parameters['utilization_target'] - self.optimization_parameters['allocation_threshold']:
                # Under-utilized: increase allocations
                target_total = pool['capacity'] * self.optimization_parameters['utilization_target']
                current_total = sum(pool['allocations'].values())
                
                if current_total > 0:
                    increase_factor = min(
                        target_total / current_total,
                        self.optimization_parameters['increase_factor']
                    )
                    for cluster_id, amount in pool['allocations'].items():
                        increased_amount = amount * increase_factor
                        pool_allocations[cluster_id] = increased_amount
            else:
                # Within target range: keep current allocations
                pool_allocations = pool['allocations'].copy()
                
            optimized_allocations[pool_id] = pool_allocations
            
        return optimized_allocations
        
    def _calculate_utilization(self) -> Dict[str, float]:
        """
        Calculate current utilization for each resource pool.
        
        Returns:
            Dict[str, float]: Utilization ratios per pool
        """
        utilization = {}
        for pool_id, pool in self.resource_pools.items():
            total_allocated = sum(pool['allocations'].values())
            utilization[pool_id] = total_allocated / pool['capacity']
        return utilization
        
    def get_allocation_history(self, pool_id: Optional[str] = None, 
                             cluster_id: Optional[str] = None) -> List[ResourceAllocation]:
        """
        Get allocation history, optionally filtered by pool or cluster.
        
        Args:
            pool_id: Optional pool ID to filter by
            cluster_id: Optional cluster ID to filter by
            
        Returns:
            List[ResourceAllocation]: Filtered allocation history
        """
        history = self.allocation_history
        
        if pool_id:
            history = [a for a in history if a.resource_id == pool_id]
            
        if cluster_id:
            history = [a for a in history if a.cluster_id == cluster_id]
            
        return history