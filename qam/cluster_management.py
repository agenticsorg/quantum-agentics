from typing import List, Dict, Optional
import numpy as np
from dataclasses import dataclass, field
from .azure_quantum import AzureQuantumClient, AzureQuantumConfig

@dataclass
class AgentCluster:
    """Represents a group of related agents."""
    agents: List[str] = field(default_factory=list)
    sub_clusters: List['AgentCluster'] = field(default_factory=list)
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    optimization_parameters: Dict[str, float] = field(default_factory=dict)
    
    def add_agent(self, agent_id: str) -> bool:
        """Add an agent to the cluster."""
        if agent_id not in self.agents:
            self.agents.append(agent_id)
            return True
        return False
        
    def add_sub_cluster(self, cluster: 'AgentCluster') -> bool:
        """Add a sub-cluster to this cluster."""
        if cluster not in self.sub_clusters:
            self.sub_clusters.append(cluster)
            return True
        return False
        
    def update_resource_requirements(self, requirements: Dict[str, float]) -> None:
        """Update resource requirements for the cluster."""
        self.resource_requirements.update(requirements)
        
    def get_total_agents(self) -> int:
        """Get total number of agents in this cluster and sub-clusters."""
        total = len(self.agents)
        for sub_cluster in self.sub_clusters:
            total += sub_cluster.get_total_agents()
        return total
        
    def get_total_resource_requirements(self) -> Dict[str, float]:
        """Get combined resource requirements for this cluster and sub-clusters."""
        total_requirements = self.resource_requirements.copy()
        
        for sub_cluster in self.sub_clusters:
            sub_requirements = sub_cluster.get_total_resource_requirements()
            for resource, amount in sub_requirements.items():
                total_requirements[resource] = total_requirements.get(resource, 0.0) + amount
                
        return total_requirements

class ClusterManager:
    """Manages agent cluster hierarchy."""
    
    def __init__(self):
        self.root_clusters: List[AgentCluster] = []
        self.optimization_state: Optional[np.ndarray] = None
        self.cluster_map: Dict[str, AgentCluster] = {}
        self.quantum_client = AzureQuantumClient(
            AzureQuantumConfig(
                resource_group="AzureQuantum",
                workspace_name="QuantumGPT",
                location="eastus",
                target_id="ionq.simulator"
            )
        )
        
    def create_cluster(self) -> AgentCluster:
        """Create a new agent cluster."""
        cluster = AgentCluster()
        self.root_clusters.append(cluster)
        return cluster
        
    def optimize_cluster_structure(self) -> Dict[str, List[str]]:
        """Use quantum algorithms for cluster optimization."""
        if not self.root_clusters:
            return {}
            
        try:
            # Prepare QUBO problem for cluster optimization
            problem = self._prepare_cluster_qubo()
            
            # Submit to Azure Quantum
            job_id = self.quantum_client.submit_qubo(problem)
            
            # Get results
            result = self.quantum_client.wait_for_job(job_id)
            
            # Process results
            assignments = self._process_quantum_result(result)
            
            # If no valid assignments, use classical optimization
            if not assignments:
                assignments = self._classical_optimization()
                
            return assignments
            
        except Exception as e:
            print(f"Quantum optimization failed: {e}, falling back to classical method")
            return self._classical_optimization()

    def _prepare_cluster_qubo(self) -> Dict:
        """Prepare QUBO problem for cluster optimization."""
        # Get cluster metrics
        metrics = self._calculate_cluster_metrics()
        
        # Create QUBO terms
        terms = []
        n_clusters = len(self.root_clusters)
        
        for i in range(n_clusters):
            for j in range(i, n_clusters):
                cluster_i = self.root_clusters[i]
                cluster_j = self.root_clusters[j]
                
                if i == j:
                    # Diagonal terms - cluster size penalty
                    weight = self._calculate_size_penalty(cluster_i)
                    terms.append({
                        "c": float(weight),
                        "ids": [i]
                    })
                else:
                    # Interaction terms - resource sharing penalty
                    weight = self._calculate_interaction_penalty(cluster_i, cluster_j)
                    terms.append({
                        "c": float(weight),
                        "ids": [i, j]
                    })
        
        return {
            "type": "optimization",
            "format": "microsoft.qio.v2",
            "problem": {
                "problem_type": "pubo",
                "terms": terms,
                "version": "1.0"
            },
            "parameters": {
                "timeout": 100,
                "seed": 123,
                "beta_start": 0.1,
                "beta_stop": 1.0,
                "sweeps": 1000
            }
        }

    def _calculate_size_penalty(self, cluster: AgentCluster) -> float:
        """Calculate penalty for cluster size."""
        size = float(cluster.get_total_agents())
        target_size = 50.0  # Ideal cluster size
        
        # Calculate relative deviation from target size
        deviation = abs(size - target_size) / target_size
        
        # Use a combination of exponential and polynomial growth
        # This ensures the penalty grows rapidly as size deviates from target
        base_penalty = np.exp(deviation) - 1.0
        scaling_factor = (size / target_size) ** 2
        
        return base_penalty * scaling_factor

    def _calculate_interaction_penalty(self, cluster1: AgentCluster, 
                                    cluster2: AgentCluster) -> float:
        """Calculate interaction penalty between clusters."""
        # Get resource requirements
        resources1 = cluster1.get_total_resource_requirements()
        resources2 = cluster2.get_total_resource_requirements()
        
        # Calculate overlap in resource requirements
        overlap = 0.0
        for resource, amount1 in resources1.items():
            if resource in resources2:
                overlap += min(amount1, resources2[resource])
                
        return overlap

    def _process_quantum_result(self, result: Dict) -> Dict[str, List[str]]:
        """Process quantum optimization results."""
        assignments: Dict[str, List[str]] = {}
        
        if 'solutions' in result and len(result['solutions']) > 0:
            solution = result['solutions'][0].get('configuration', {})
            
            # Convert solution to cluster assignments
            for i, cluster in enumerate(self.root_clusters):
                if str(i) in solution and float(solution[str(i)]) > 0.5:
                    # Check if cluster needs splitting based on size
                    if cluster.get_total_agents() > 100:
                        self._split_cluster(cluster, assignments)
                    else:
                        # Keep cluster intact
                        assignments[id(cluster)] = cluster.agents.copy()
                else:
                    # Split cluster
                    self._split_cluster(cluster, assignments)
        
        return assignments

    def _classical_optimization(self) -> Dict[str, List[str]]:
        """Fallback classical optimization method."""
        assignments: Dict[str, List[str]] = {}
        
        for cluster in self.root_clusters:
            if cluster.get_total_agents() > 100:  # Split large clusters
                self._split_cluster(cluster, assignments)
            else:
                assignments[id(cluster)] = cluster.agents.copy()
                
        return assignments

    def _calculate_cluster_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate metrics for each cluster."""
        metrics = {}
        
        for cluster in self.root_clusters:
            cluster_id = str(id(cluster))
            metrics[cluster_id] = {
                'size': cluster.get_total_agents(),
                'resource_density': sum(cluster.get_total_resource_requirements().values()),
                'depth': self._calculate_cluster_depth(cluster)
            }
            
        return metrics
        
    def _calculate_cluster_depth(self, cluster: AgentCluster) -> int:
        """Calculate the depth of a cluster in the hierarchy."""
        if not cluster.sub_clusters:
            return 1
            
        return 1 + max(self._calculate_cluster_depth(sub) for sub in cluster.sub_clusters)
        
    def _split_cluster(self, cluster: AgentCluster, 
                      assignments: Dict[str, List[str]]) -> None:
        """Split a large cluster into smaller sub-clusters."""
        # Simple splitting strategy - divide agents evenly
        agents = cluster.agents.copy()  # Make a copy to avoid modifying original
        mid = len(agents) // 2
        
        sub_cluster1 = AgentCluster(agents=agents[:mid])
        sub_cluster2 = AgentCluster(agents=agents[mid:])
        
        # Update resource requirements
        total_requirements = cluster.get_total_resource_requirements()
        for resource, amount in total_requirements.items():
            sub_cluster1.resource_requirements[resource] = amount / 2
            sub_cluster2.resource_requirements[resource] = amount / 2
            
        # Update assignments
        assignments[id(sub_cluster1)] = sub_cluster1.agents.copy()
        assignments[id(sub_cluster2)] = sub_cluster2.agents.copy()
        
        # Add to cluster hierarchy
        cluster.agents.clear()
        cluster.add_sub_cluster(sub_cluster1)
        cluster.add_sub_cluster(sub_cluster2)
