import pytest
import numpy as np
from qam.cluster_management import ClusterManager, AgentCluster

def test_cluster_initialization():
    """Test cluster manager initialization with quantum client."""
    manager = ClusterManager()
    assert manager.quantum_client is not None
    assert manager.root_clusters == []
    assert manager.cluster_map == {}

def test_prepare_cluster_qubo():
    """Test QUBO problem preparation for quantum optimization."""
    manager = ClusterManager()
    
    # Create test clusters
    cluster1 = manager.create_cluster()
    cluster1.add_agent("agent1")
    cluster1.update_resource_requirements({"cpu": 2.0, "memory": 4.0})
    
    cluster2 = manager.create_cluster()
    cluster2.add_agent("agent2")
    cluster2.update_resource_requirements({"cpu": 1.0, "memory": 2.0})
    
    # Prepare QUBO problem
    problem = manager._prepare_cluster_qubo()
    
    assert problem["type"] == "optimization"
    assert problem["format"] == "microsoft.qio.v2"
    assert problem["problem"]["problem_type"] == "pubo"
    assert len(problem["problem"]["terms"]) > 0

def test_size_penalty_calculation():
    """Test cluster size penalty calculation."""
    manager = ClusterManager()
    cluster = manager.create_cluster()
    
    # Start with 30 agents (less than target size of 50)
    for i in range(30):
        cluster.add_agent(f"agent{i}")
    
    penalty1 = manager._calculate_size_penalty(cluster)
    print(f"Penalty for 30 agents: {penalty1}")
    assert penalty1 > 0
    
    # Add 40 more agents to reach 70 (exceeds target size)
    for i in range(30, 70):  # Using correct Python range syntax
        cluster.add_agent(f"agent{i}")
    
    penalty2 = manager._calculate_size_penalty(cluster)
    print(f"Penalty for 70 agents: {penalty2}")
    assert penalty2 > penalty1

def test_interaction_penalty():
    """Test interaction penalty calculation between clusters."""
    manager = ClusterManager()
    
    # Create clusters with overlapping resources
    cluster1 = manager.create_cluster()
    cluster1.update_resource_requirements({"cpu": 2.0, "memory": 4.0})
    
    cluster2 = manager.create_cluster()
    cluster2.update_resource_requirements({"cpu": 1.0, "memory": 2.0})
    
    penalty = manager._calculate_interaction_penalty(cluster1, cluster2)
    assert penalty > 0
    
    # Create cluster with non-overlapping resources
    cluster3 = manager.create_cluster()
    cluster3.update_resource_requirements({"gpu": 1.0})
    
    penalty = manager._calculate_interaction_penalty(cluster1, cluster3)
    assert penalty == 0

def test_quantum_optimization():
    """Test quantum optimization of cluster structure."""
    manager = ClusterManager()
    
    # Create test clusters
    for i in range(3):
        cluster = manager.create_cluster()
        for j in range(20):
            cluster.add_agent(f"agent{i}_{j}")
        cluster.update_resource_requirements({
            "cpu": float(i + 1),
            "memory": float(2 * (i + 1))
        })
    
    # Optimize cluster structure
    assignments = manager.optimize_cluster_structure()
    
    assert isinstance(assignments, dict)
    assert len(assignments) > 0
    assert all(isinstance(agents, list) for agents in assignments.values())

def test_quantum_result_processing():
    """Test processing of quantum optimization results."""
    manager = ClusterManager()
    
    # Create test clusters
    cluster1 = manager.create_cluster()
    cluster1.add_agent("agent1")
    
    cluster2 = manager.create_cluster()
    cluster2.add_agent("agent2")
    
    # Create mock quantum result
    mock_result = {
        "solutions": [{
            "configuration": {
                "0": 1,  # Keep first cluster intact
                "1": 0   # Split second cluster
            }
        }]
    }
    
    assignments = manager._process_quantum_result(mock_result)
    
    assert isinstance(assignments, dict)
    assert len(assignments) >= 1
    assert any(agents == ["agent1"] for agents in assignments.values())

def test_classical_fallback():
    """Test classical optimization fallback."""
    manager = ClusterManager()
    
    # Create a large cluster that should be split
    cluster = manager.create_cluster()
    for i in range(150):  # Exceeds threshold of 100
        cluster.add_agent(f"agent{i}")
    
    assignments = manager._classical_optimization()
    
    assert isinstance(assignments, dict)
    assert len(assignments) > 1  # Should have split into multiple assignments

def test_end_to_end_optimization():
    """Test complete optimization workflow."""
    manager = ClusterManager()
    
    # Create varied test clusters
    sizes = [30, 60, 90, 120]
    resources = [
        {"cpu": 1.0, "memory": 2.0},
        {"cpu": 2.0, "memory": 4.0},
        {"gpu": 1.0},
        {"cpu": 3.0, "gpu": 1.0}
    ]
    
    for i, (size, resource) in enumerate(zip(sizes, resources)):
        cluster = manager.create_cluster()
        for j in range(size):
            cluster.add_agent(f"agent{i}_{j}")
        cluster.update_resource_requirements(resource)
    
    # Run optimization
    assignments = manager.optimize_cluster_structure()
    
    assert isinstance(assignments, dict)
    assert len(assignments) > 0
    
    # Verify all agents are assigned
    assigned_agents = set()
    for agents in assignments.values():
        assigned_agents.update(agents)
    
    total_agents = sum(sizes)
    assert len(assigned_agents) == total_agents