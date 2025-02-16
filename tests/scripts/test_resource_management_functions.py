#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

from datetime import datetime
from qam.resource_management import ResourceManager, ResourceAllocation

def test_resource_management():
    print("\nTesting Resource Management...")
    
    # Test 1: Create manager
    print("\n1. Testing manager creation")
    manager = ResourceManager()
    print("Manager created successfully")
    
    # Test 2: Add resource pools
    print("\n2. Testing resource pool addition")
    success = manager.add_resource_pool("pool1", capacity=100.0, resource_type="cpu")
    print(f"Pool1 addition: {success}")
    
    success = manager.add_resource_pool("pool2", capacity=200.0, resource_type="memory")
    print(f"Pool2 addition: {success}")
    assert len(manager.resource_pools) == 2
    
    # Test duplicate pool
    success = manager.add_resource_pool("pool1", capacity=50.0, resource_type="cpu")
    print(f"Duplicate pool addition: {success}")
    assert not success
    
    # Test 3: Resource allocation
    print("\n3. Testing resource allocation")
    allocation = manager.allocate_resource("pool1", "cluster1", 50.0)
    print(f"Allocation created: {allocation}")
    assert allocation is not None
    assert allocation.amount == 50.0
    
    # Test over-allocation
    over_allocation = manager.allocate_resource("pool1", "cluster1", 60.0)
    print(f"Over-allocation attempt: {over_allocation is None}")
    assert over_allocation is None
    
    # Test 4: Resource release
    print("\n4. Testing resource release")
    success = manager.release_resource("pool1", "cluster1", 20.0)
    print(f"Partial release: {success}")
    assert success
    
    # Verify remaining allocation
    pool = manager.resource_pools["pool1"]
    assert pool['allocations']['cluster1'] == 30.0
    
    # Test full release
    success = manager.release_resource("pool1", "cluster1")
    print(f"Full release: {success}")
    assert success
    assert 'cluster1' not in pool['allocations']
    
    # Test 5: Multiple allocations
    print("\n5. Testing multiple allocations")
    allocations = []
    for i in range(3):
        allocation = manager.allocate_resource("pool2", f"cluster{i}", 50.0)
        allocations.append(allocation)
    print(f"Created {len(allocations)} allocations")
    assert len(allocations) == 3
    
    # Test 6: Optimization
    print("\n6. Testing allocation optimization")
    optimized = manager.optimize_allocations()
    print(f"Optimized allocations: {optimized}")
    assert isinstance(optimized, dict)
    
    # Test 7: Utilization calculation
    print("\n7. Testing utilization calculation")
    utilization = manager._calculate_utilization()
    print(f"Resource utilization: {utilization}")
    assert all(0 <= util <= 1 for util in utilization.values())
    
    # Test 8: Allocation history
    print("\n8. Testing allocation history")
    history = manager.get_allocation_history()
    print(f"Total history entries: {len(history)}")
    assert len(history) > 0
    
    # Test filtered history
    cluster_history = manager.get_allocation_history(cluster_id="cluster0")
    print(f"Cluster0 history entries: {len(cluster_history)}")
    assert all(h.cluster_id == "cluster0" for h in cluster_history)
    
    # Test 9: Resource pool cleanup
    print("\n9. Testing resource cleanup")
    # Release all resources from pool2
    for i in range(3):
        success = manager.release_resource("pool2", f"cluster{i}")
        assert success
    
    pool2 = manager.resource_pools["pool2"]
    assert len(pool2['allocations']) == 0
    assert pool2['available'] == pool2['capacity']
    
    # Test 10: Edge cases
    print("\n10. Testing edge cases")
    # Try to release from non-existent pool
    success = manager.release_resource("nonexistent", "cluster1")
    print(f"Release from non-existent pool: {success}")
    assert not success
    
    # Try to allocate from non-existent pool
    allocation = manager.allocate_resource("nonexistent", "cluster1", 50.0)
    print(f"Allocation from non-existent pool: {allocation is None}")
    assert allocation is None
    
    # Try to release more than allocated
    manager.allocate_resource("pool1", "cluster1", 30.0)
    success = manager.release_resource("pool1", "cluster1", 50.0)
    print(f"Release more than allocated: {success}")
    assert not success

if __name__ == "__main__":
    try:
        test_resource_management()
        print("\n✅ All resource management tests completed successfully")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")