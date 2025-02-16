#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

import numpy as np
from qam.quantum_orchestration import QuantumOrchestrator

def test_quantum_orchestrator():
    print("\nTesting QuantumOrchestrator...")
    
    # Test 1: Create orchestrator
    print("\n1. Testing orchestrator creation")
    orchestrator = QuantumOrchestrator()
    print("Orchestrator created successfully")
    
    # Test 2: Add clusters
    print("\n2. Testing cluster addition")
    cluster1_data = {
        'size': 50,
        'resources': ['cpu', 'memory'],
        'capacity': 100
    }
    success = orchestrator.add_cluster("cluster1", cluster1_data)
    print(f"Cluster1 addition: {success}")
    
    cluster2_data = {
        'size': 120,  # Large cluster that should be split
        'resources': ['gpu', 'memory'],
        'capacity': 200
    }
    success = orchestrator.add_cluster("cluster2", cluster2_data)
    print(f"Cluster2 addition: {success}")
    assert len(orchestrator.agent_clusters) == 2
    
    # Test 3: Add resources
    print("\n3. Testing resource addition")
    resource1_data = {
        'type': 'cpu',
        'available': 10,
        'total': 10
    }
    success = orchestrator.add_resource("cpu1", resource1_data)
    print(f"Resource1 addition: {success}")
    
    resource2_data = {
        'type': 'gpu',
        'available': 5,
        'total': 5
    }
    success = orchestrator.add_resource("gpu1", resource2_data)
    print(f"Resource2 addition: {success}")
    assert len(orchestrator.resource_map) == 2
    
    # Test 4: Manage clusters
    print("\n4. Testing cluster management")
    organized_clusters = orchestrator.manage_agent_clusters()
    print(f"Organized clusters: {len(organized_clusters)}")
    # Should have split cluster2 due to size > 100
    assert len(organized_clusters) == 3
    
    # Test 5: Resource allocation
    print("\n5. Testing resource allocation")
    allocation = orchestrator.optimize_resource_allocation()
    print(f"Resource allocation: {allocation}")
    assert isinstance(allocation, dict)
    assert all('resources' in cluster_data for cluster_data in allocation.values())
    
    # Test 6: Matrix conversion
    print("\n6. Testing matrix conversion")
    # Create test matrix matching the current number of clusters and resources
    num_clusters = len(orchestrator.agent_clusters)
    num_resources = len(orchestrator.resource_map)
    test_matrix = np.zeros((num_clusters, num_resources))
    # Assign some resources
    for i in range(num_clusters):
        for j in range(num_resources):
            test_matrix[i, j] = 1 if i == j else 0
            
    allocation = orchestrator._convert_matrix_to_allocation(test_matrix)
    print(f"Matrix conversion result: {allocation}")
    assert isinstance(allocation, dict)
    assert len(allocation) == num_clusters
    
    # Test 7: Duplicate additions
    print("\n7. Testing duplicate handling")
    # Try to add duplicate cluster
    success = orchestrator.add_cluster("cluster1", cluster1_data)
    print(f"Duplicate cluster addition: {success}")
    assert not success
    
    # Try to add duplicate resource
    success = orchestrator.add_resource("cpu1", resource1_data)
    print(f"Duplicate resource addition: {success}")
    assert not success
    
    # Test 8: Empty state handling
    print("\n8. Testing empty state handling")
    empty_orchestrator = QuantumOrchestrator()
    empty_allocation = empty_orchestrator.optimize_resource_allocation()
    print(f"Empty allocation: {empty_allocation}")
    assert empty_allocation == {}
    
    empty_clusters = empty_orchestrator.manage_agent_clusters()
    print(f"Empty clusters: {empty_clusters}")
    assert empty_clusters == {}
    
    # Test 9: Large scale test
    print("\n9. Testing large scale orchestration")
    # Add multiple clusters and resources
    for i in range(5):
        orchestrator.add_cluster(f"test_cluster_{i}", {
            'size': 50 + i * 10,
            'resources': ['cpu', 'memory'],
            'capacity': 100
        })
        orchestrator.add_resource(f"test_resource_{i}", {
            'type': 'cpu',
            'available': 5,
            'total': 5
        })
    
    large_allocation = orchestrator.optimize_resource_allocation()
    print(f"Large scale allocation completed with {len(large_allocation)} clusters")
    assert len(large_allocation) == len(orchestrator.agent_clusters)

if __name__ == "__main__":
    try:
        test_quantum_orchestrator()
        print("\n✅ All quantum orchestration tests completed successfully")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")