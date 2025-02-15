import unittest
from datetime import datetime, timedelta
from qam.resource_management import ResourceManager, ResourceAllocation

class TestResourceManager(unittest.TestCase):
    def setUp(self):
        self.manager = ResourceManager()
        
    def test_add_resource_pool(self):
        # Test adding a new resource pool
        success = self.manager.add_resource_pool('pool1', 100.0, 'cpu')
        self.assertTrue(success)
        self.assertIn('pool1', self.manager.resource_pools)
        
        # Test adding duplicate pool
        success = self.manager.add_resource_pool('pool1', 50.0, 'cpu')
        self.assertFalse(success)
        
    def test_allocate_resource(self):
        # Add test pool
        self.manager.add_resource_pool('pool1', 100.0, 'cpu')
        
        # Test successful allocation
        allocation = self.manager.allocate_resource('pool1', 'cluster1', 50.0)
        self.assertIsNotNone(allocation)
        self.assertEqual(allocation.amount, 50.0)
        self.assertEqual(self.manager.resource_pools['pool1']['available'], 50.0)
        
        # Test allocation exceeding available resources
        allocation = self.manager.allocate_resource('pool1', 'cluster2', 60.0)
        self.assertIsNone(allocation)
        
        # Test allocation from non-existent pool
        allocation = self.manager.allocate_resource('pool2', 'cluster1', 10.0)
        self.assertIsNone(allocation)
        
    def test_release_resource(self):
        # Setup test pool and allocation
        self.manager.add_resource_pool('pool1', 100.0, 'cpu')
        self.manager.allocate_resource('pool1', 'cluster1', 50.0)
        
        # Test successful release
        success = self.manager.release_resource('pool1', 'cluster1', 30.0)
        self.assertTrue(success)
        self.assertEqual(self.manager.resource_pools['pool1']['available'], 80.0)
        
        # Test release exceeding allocation
        success = self.manager.release_resource('pool1', 'cluster1', 30.0)
        self.assertFalse(success)
        
        # Test release from non-existent pool
        success = self.manager.release_resource('pool2', 'cluster1', 10.0)
        self.assertFalse(success)
        
    def test_optimize_allocations(self):
        # Setup test pools and allocations
        self.manager.add_resource_pool('pool1', 100.0, 'cpu')
        self.manager.add_resource_pool('pool2', 200.0, 'memory')
        
        # Create over-utilized pool (90% > 80% target)
        self.manager.allocate_resource('pool1', 'cluster1', 90.0)
        
        # Create under-utilized pool (50% < 80% target)
        self.manager.allocate_resource('pool2', 'cluster2', 100.0)
        
        # Test optimization
        optimized = self.manager.optimize_allocations()
        
        # Verify both pools are in the result
        self.assertIn('pool1', optimized)
        self.assertIn('pool2', optimized)
        
        # Verify over-utilized pool (pool1) is reduced
        self.assertIn('cluster1', optimized['pool1'])
        reduced_allocation = optimized['pool1']['cluster1']
        self.assertLess(reduced_allocation, 90.0)
        self.assertGreater(reduced_allocation, 0.0)
        
        # Verify under-utilized pool (pool2) is increased
        self.assertIn('cluster2', optimized['pool2'])
        increased_allocation = optimized['pool2']['cluster2']
        self.assertGreater(increased_allocation, 100.0)
        self.assertLessEqual(increased_allocation, 150.0)  # Max 50% increase
        
    def test_get_allocation_history(self):
        # Setup test allocations
        self.manager.add_resource_pool('pool1', 100.0, 'cpu')
        self.manager.add_resource_pool('pool2', 200.0, 'memory')
        
        self.manager.allocate_resource('pool1', 'cluster1', 50.0)
        self.manager.allocate_resource('pool2', 'cluster1', 100.0)
        self.manager.allocate_resource('pool2', 'cluster2', 50.0)
        
        # Test unfiltered history
        history = self.manager.get_allocation_history()
        self.assertEqual(len(history), 3)
        
        # Test filtering by pool
        pool_history = self.manager.get_allocation_history(pool_id='pool1')
        self.assertEqual(len(pool_history), 1)
        self.assertEqual(pool_history[0].resource_id, 'pool1')
        
        # Test filtering by cluster
        cluster_history = self.manager.get_allocation_history(cluster_id='cluster1')
        self.assertEqual(len(cluster_history), 2)
        self.assertTrue(all(a.cluster_id == 'cluster1' for a in cluster_history))
        
    def test_calculate_utilization(self):
        # Setup test pools and allocations
        self.manager.add_resource_pool('pool1', 100.0, 'cpu')
        self.manager.allocate_resource('pool1', 'cluster1', 60.0)
        
        # Test utilization calculation
        utilization = self.manager._calculate_utilization()
        self.assertIn('pool1', utilization)
        self.assertEqual(utilization['pool1'], 0.6)  # 60/100 = 0.6
        
    def test_empty_optimization(self):
        # Test optimization with no pools
        optimized = self.manager.optimize_allocations()
        self.assertEqual(optimized, {})
        
        # Test optimization with empty pool
        self.manager.add_resource_pool('pool1', 100.0, 'cpu')
        optimized = self.manager.optimize_allocations()
        self.assertEqual(optimized['pool1'], {})

if __name__ == '__main__':
    unittest.main()