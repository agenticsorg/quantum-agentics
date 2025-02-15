import unittest
import numpy as np
from qam.quantum_orchestration import QuantumOrchestrator

class TestQuantumOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = QuantumOrchestrator()
        
    def test_add_cluster(self):
        # Test adding a new cluster
        cluster_data = {
            'size': 50,
            'resources': ['cpu', 'memory']
        }
        success = self.orchestrator.add_cluster('cluster1', cluster_data)
        self.assertTrue(success)
        self.assertIn('cluster1', self.orchestrator.agent_clusters)
        
        # Test adding duplicate cluster
        success = self.orchestrator.add_cluster('cluster1', cluster_data)
        self.assertFalse(success)
        
    def test_add_resource(self):
        # Test adding a new resource
        resource_data = {
            'available': 100,
            'type': 'cpu'
        }
        success = self.orchestrator.add_resource('resource1', resource_data)
        self.assertTrue(success)
        self.assertIn('resource1', self.orchestrator.resource_map)
        
        # Test adding duplicate resource
        success = self.orchestrator.add_resource('resource1', resource_data)
        self.assertFalse(success)
        
    def test_optimize_resource_allocation_empty(self):
        # Test optimization with no clusters or resources
        result = self.orchestrator.optimize_resource_allocation()
        self.assertEqual(result, {})
        
    def test_optimize_resource_allocation(self):
        # Add test clusters
        cluster1 = {'size': 50, 'resources': ['cpu']}
        cluster2 = {'size': 30, 'resources': ['memory']}
        self.orchestrator.add_cluster('cluster1', cluster1)
        self.orchestrator.add_cluster('cluster2', cluster2)
        
        # Add test resources
        resource1 = {'available': 100, 'type': 'cpu'}
        resource2 = {'available': 200, 'type': 'memory'}
        self.orchestrator.add_resource('resource1', resource1)
        self.orchestrator.add_resource('resource2', resource2)
        
        # Test optimization
        result = self.orchestrator.optimize_resource_allocation()
        self.assertIsInstance(result, dict)
        self.assertIn('cluster1', result)
        self.assertIn('cluster2', result)
        self.assertIsInstance(result['cluster1']['resources'], list)
        
    def test_manage_agent_clusters_empty(self):
        # Test cluster management with no clusters
        result = self.orchestrator.manage_agent_clusters()
        self.assertEqual(result, {})
        
    def test_manage_agent_clusters(self):
        # Add a large cluster that should be split
        large_cluster = {
            'size': 150,
            'resources': ['cpu', 'memory']
        }
        self.orchestrator.add_cluster('large_cluster', large_cluster)
        
        # Test cluster management
        result = self.orchestrator.manage_agent_clusters()
        self.assertGreater(len(result), 1)  # Should have split into multiple clusters
        self.assertEqual(
            sum(cluster.get('size', 0) for cluster in result.values()),
            large_cluster['size']
        )
        
    def test_convert_matrix_to_allocation(self):
        # Setup test data
        self.orchestrator.add_cluster('cluster1', {'size': 50})
        self.orchestrator.add_resource('resource1', {'available': 100})
        
        # Create test matrix
        matrix = np.array([[1]])
        
        # Test conversion
        result = self.orchestrator._convert_matrix_to_allocation(matrix)
        self.assertIn('cluster1', result)
        self.assertIn('resources', result['cluster1'])
        self.assertEqual(result['cluster1']['resources'], ['resource1'])

if __name__ == '__main__':
    unittest.main()