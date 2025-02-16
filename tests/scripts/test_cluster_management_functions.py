#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

from unittest.mock import patch, MagicMock
from qam.cluster_management import AgentCluster, ClusterManager

def test_agent_cluster():
    print("\nTesting AgentCluster...")
    
    # Test 1: Create and add agents
    print("\n1. Testing agent addition")
    cluster = AgentCluster()
    assert cluster.add_agent("agent1") == True
    assert cluster.add_agent("agent2") == True
    assert cluster.add_agent("agent1") == False  # Duplicate
    print(f"Agents in cluster: {cluster.agents}")
    
    # Test 2: Add sub-clusters
    print("\n2. Testing sub-cluster addition")
    sub_cluster = AgentCluster()
    sub_cluster.add_agent("agent3")
    assert cluster.add_sub_cluster(sub_cluster) == True
    assert cluster.add_sub_cluster(sub_cluster) == False  # Duplicate
    print(f"Number of sub-clusters: {len(cluster.sub_clusters)}")
    
    # Test 3: Update resource requirements
    print("\n3. Testing resource requirements")
    requirements = {"cpu": 2.0, "memory": 4.0}
    cluster.update_resource_requirements(requirements)
    print(f"Resource requirements: {cluster.resource_requirements}")
    
    # Test 4: Get total agents
    print("\n4. Testing total agents count")
    total = cluster.get_total_agents()
    print(f"Total agents: {total}")
    assert total == 3  # 2 in main cluster + 1 in sub-cluster
    
    # Test 5: Get total resource requirements
    print("\n5. Testing total resource requirements")
    sub_cluster.update_resource_requirements({"cpu": 1.0, "memory": 2.0})
    total_req = cluster.get_total_resource_requirements()
    print(f"Total resource requirements: {total_req}")
    assert total_req["cpu"] == 3.0  # 2.0 + 1.0
    assert total_req["memory"] == 6.0  # 4.0 + 2.0

def test_cluster_manager():
    print("\nTesting ClusterManager...")
    
    # Mock Azure Quantum client
    mock_quantum_client = MagicMock()
    mock_quantum_client.submit_qubo.return_value = "test-job-id"
    mock_quantum_client.wait_for_job.return_value = {
        "solutions": [{
            "configuration": {"0": 1.0, "1": 0.0}
        }]
    }
    
    with patch('qam.cluster_management.AzureQuantumClient', return_value=mock_quantum_client):
        # Test 1: Create manager and cluster
        print("\n1. Testing cluster creation")
        manager = ClusterManager()
        cluster1 = manager.create_cluster()
        cluster2 = manager.create_cluster()
        
        # Add agents and resources
        cluster1.add_agent("agent1")
        cluster1.add_agent("agent2")
        cluster1.update_resource_requirements({"cpu": 2.0, "memory": 4.0})
        
        cluster2.add_agent("agent3")
        cluster2.update_resource_requirements({"cpu": 1.0, "memory": 2.0})
        
        print(f"Number of root clusters: {len(manager.root_clusters)}")
        
        # Test 2: Optimize cluster structure
        print("\n2. Testing cluster optimization")
        assignments = manager.optimize_cluster_structure()
        print(f"Optimization assignments: {assignments}")
        
        # Test 3: Classical optimization fallback
        print("\n3. Testing classical optimization fallback")
        # Create a large cluster that will trigger splitting
        large_cluster = manager.create_cluster()
        for i in range(101):  # More than the 100 agent threshold
            large_cluster.add_agent(f"agent{i+100}")
        
        assignments = manager._classical_optimization()
        print(f"Classical optimization results: {len(assignments)} clusters")
        
        # Test 4: Cluster metrics
        print("\n4. Testing cluster metrics calculation")
        metrics = manager._calculate_cluster_metrics()
        print(f"Cluster metrics: {metrics}")

if __name__ == "__main__":
    try:
        test_agent_cluster()
        test_cluster_manager()
        print("\n✅ All cluster management tests completed successfully")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")