import unittest
import numpy as np
from qam.enhanced_scheduler import EnhancedQUBOScheduler

class TestEnhancedQUBOScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = EnhancedQUBOScheduler()
        
        # Sample test data
        self.test_tasks = [
            {
                'id': 'task1',
                'required_resources': ['cpu', 'memory'],
                'duration': 2
            },
            {
                'id': 'task2',
                'required_resources': ['gpu', 'memory'],
                'duration': 1
            },
            {
                'id': 'task3',
                'required_resources': ['cpu'],
                'duration': 3
            }
        ]
        
        self.test_clusters = {
            'cluster1': {
                'available_resources': ['cpu', 'memory'],
                'capacity': 100,
                'current_load': 30
            },
            'cluster2': {
                'available_resources': ['gpu', 'memory'],
                'capacity': 50,
                'current_load': 10
            }
        }
        
    def test_build_hierarchical_qubo(self):
        # Test building hierarchical QUBO matrices
        qubo_matrices = self.scheduler.build_hierarchical_qubo(
            self.test_tasks,
            self.test_clusters,
            max_cluster_size=2
        )
        
        # Verify we got QUBO matrices
        self.assertIsInstance(qubo_matrices, list)
        self.assertTrue(all(isinstance(m, np.ndarray) for m in qubo_matrices))
        
        # Verify matrices are symmetric
        for matrix in qubo_matrices:
            np.testing.assert_array_almost_equal(matrix, matrix.T)
            
    def test_optimize_cluster_assignments(self):
        # Test cluster assignment optimization
        assignments = self.scheduler.optimize_cluster_assignments(
            self.test_tasks,
            self.test_clusters
        )
        
        # Verify all tasks are assigned
        self.assertEqual(len(assignments), len(self.test_tasks))
        
        # Verify assignments are valid
        for task_id, cluster_id in assignments.items():
            self.assertIn(cluster_id, self.test_clusters)
            
        # Verify resource-aware assignments
        # Task1 should be assigned to cluster1 (cpu+memory)
        self.assertEqual(assignments['task1'], 'cluster1')
        # Task2 should be assigned to cluster2 (gpu+memory)
        self.assertEqual(assignments['task2'], 'cluster2')
            
    def test_assign_tasks_to_clusters(self):
        # Test internal task clustering
        task_clusters = self.scheduler._assign_tasks_to_clusters(
            self.test_tasks,
            self.test_clusters,
            max_cluster_size=2
        )
        
        # Verify cluster structure
        self.assertEqual(len(task_clusters), len(self.test_clusters))
        
        # Verify cluster size limits
        for cluster_tasks in task_clusters.values():
            self.assertLessEqual(len(cluster_tasks), 2)
            
        # Verify all tasks are in some cluster
        total_tasks = sum(len(cluster) for cluster in task_clusters.values())
        self.assertGreater(total_tasks, 0)
        self.assertLessEqual(total_tasks, len(self.test_tasks))
        
    def test_empty_inputs(self):
        # Test with empty task list
        empty_assignments = self.scheduler.optimize_cluster_assignments(
            [],
            self.test_clusters
        )
        self.assertEqual(empty_assignments, {})
        
        # Test with empty cluster dict
        empty_assignments = self.scheduler.optimize_cluster_assignments(
            self.test_tasks,
            {}
        )
        self.assertEqual(empty_assignments, {})
        
        # Test hierarchical QUBO with empty inputs
        empty_qubo = self.scheduler.build_hierarchical_qubo([], {})
        self.assertEqual(empty_qubo, [])

if __name__ == '__main__':
    unittest.main()