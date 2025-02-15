import unittest
from qam.cluster_management import AgentCluster, ClusterManager

class TestAgentCluster(unittest.TestCase):
    def setUp(self):
        self.cluster = AgentCluster()
        
    def test_add_agent(self):
        # Test adding a new agent
        success = self.cluster.add_agent('agent1')
        self.assertTrue(success)
        self.assertIn('agent1', self.cluster.agents)
        
        # Test adding duplicate agent
        success = self.cluster.add_agent('agent1')
        self.assertFalse(success)
        
    def test_add_sub_cluster(self):
        # Create and add sub-cluster
        sub_cluster = AgentCluster()
        success = self.cluster.add_sub_cluster(sub_cluster)
        self.assertTrue(success)
        self.assertIn(sub_cluster, self.cluster.sub_clusters)
        
        # Test adding duplicate sub-cluster
        success = self.cluster.add_sub_cluster(sub_cluster)
        self.assertFalse(success)
        
    def test_update_resource_requirements(self):
        requirements = {'cpu': 2.0, 'memory': 4.0}
        self.cluster.update_resource_requirements(requirements)
        self.assertEqual(self.cluster.resource_requirements, requirements)
        
        # Test updating existing requirements
        new_requirements = {'cpu': 3.0, 'disk': 10.0}
        self.cluster.update_resource_requirements(new_requirements)
        self.assertEqual(self.cluster.resource_requirements['cpu'], 3.0)
        self.assertEqual(self.cluster.resource_requirements['disk'], 10.0)
        self.assertEqual(self.cluster.resource_requirements['memory'], 4.0)
        
    def test_get_total_agents(self):
        # Add agents to main cluster
        self.cluster.add_agent('agent1')
        self.cluster.add_agent('agent2')
        
        # Create and add sub-cluster with agents
        sub_cluster = AgentCluster()
        sub_cluster.add_agent('agent3')
        sub_cluster.add_agent('agent4')
        self.cluster.add_sub_cluster(sub_cluster)
        
        # Test total count
        self.assertEqual(self.cluster.get_total_agents(), 4)
        
    def test_get_total_resource_requirements(self):
        # Add requirements to main cluster
        self.cluster.update_resource_requirements({'cpu': 2.0, 'memory': 4.0})
        
        # Create and add sub-cluster with requirements
        sub_cluster = AgentCluster()
        sub_cluster.update_resource_requirements({'cpu': 1.0, 'disk': 5.0})
        self.cluster.add_sub_cluster(sub_cluster)
        
        # Test combined requirements
        total_requirements = self.cluster.get_total_resource_requirements()
        self.assertEqual(total_requirements['cpu'], 3.0)
        self.assertEqual(total_requirements['memory'], 4.0)
        self.assertEqual(total_requirements['disk'], 5.0)

class TestClusterManager(unittest.TestCase):
    def setUp(self):
        self.manager = ClusterManager()
        
    def test_create_cluster(self):
        cluster = self.manager.create_cluster()
        self.assertIsInstance(cluster, AgentCluster)
        self.assertIn(cluster, self.manager.root_clusters)
        
    def test_optimize_cluster_structure_empty(self):
        assignments = self.manager.optimize_cluster_structure()
        self.assertEqual(assignments, {})
        
    def test_optimize_cluster_structure(self):
        # Create a large cluster that should be split
        cluster = self.manager.create_cluster()
        for i in range(150):  # Add more than 100 agents
            cluster.add_agent(f'agent{i}')
            
        # Add some resource requirements
        cluster.update_resource_requirements({'cpu': 10.0, 'memory': 20.0})
        
        # Test optimization
        assignments = self.manager.optimize_cluster_structure()
        
        # Verify assignments
        self.assertGreater(len(assignments), 1)  # Should have split into multiple clusters
        
        # Verify all agents are assigned
        assigned_agents = []
        for agent_list in assignments.values():
            assigned_agents.extend(agent_list)
        self.assertEqual(len(assigned_agents), 150)
        
    def test_calculate_cluster_metrics(self):
        # Create test cluster with sub-clusters
        cluster = self.manager.create_cluster()
        cluster.add_agent('agent1')
        
        sub_cluster = AgentCluster()
        sub_cluster.add_agent('agent2')
        cluster.add_sub_cluster(sub_cluster)
        
        # Add resource requirements
        cluster.update_resource_requirements({'cpu': 2.0})
        sub_cluster.update_resource_requirements({'memory': 4.0})
        
        # Calculate metrics
        metrics = self.manager._calculate_cluster_metrics()
        
        # Verify metrics
        cluster_id = str(id(cluster))
        self.assertIn(cluster_id, metrics)
        self.assertEqual(metrics[cluster_id]['size'], 2)
        self.assertEqual(metrics[cluster_id]['depth'], 2)
        self.assertGreater(metrics[cluster_id]['resource_density'], 0)

if __name__ == '__main__':
    unittest.main()