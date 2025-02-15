"""
Azure Quantum integration module for QAM.

This module handles interactions with Azure Quantum services for solving QUBO problems.
"""
from typing import Dict, List, Optional
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
import tempfile

@dataclass
class AzureQuantumConfig:
    """Configuration for Azure Quantum workspace."""
    resource_group: str
    workspace_name: str
    location: str
    subscription_id: Optional[str] = None
    target_id: str = "microsoft.paralleltempering.cpu"  # Default to CPU solver

class AzureQuantumClient:
    """Client for interacting with Azure Quantum optimization service."""
    
    def __init__(self, config: AzureQuantumConfig):
        """Initialize Azure Quantum client.
        
        Args:
            config: Azure Quantum configuration
        """
        self.config = config
        self._check_azure_cli()
        self._setup_workspace()
    
    def _check_azure_cli(self) -> None:
        """Check if Azure CLI and quantum extension are installed."""
        try:
            # Check Azure CLI
            subprocess.run(
                ["az", "--version"],
                check=True, capture_output=True, text=True
            )
            
            # Check quantum extension
            ext_result = subprocess.run(
                ["az", "extension", "list"],
                check=True, capture_output=True, text=True
            )
            
            try:
                extensions = json.loads(ext_result.stdout)
                has_quantum = any(ext.get('name') == 'quantum' for ext in extensions)
            except json.JSONDecodeError:
                has_quantum = False
            
            if not has_quantum:
                subprocess.run(
                    ["az", "extension", "add", "-n", "quantum"],
                    check=True, capture_output=True, text=True
                )
                
        except FileNotFoundError:
            raise RuntimeError(
                "Azure CLI not found. Please install Azure CLI."
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Azure CLI check failed: {e.stderr or str(e)}"
            )
    
    def _setup_workspace(self) -> None:
        """Set up Azure Quantum workspace."""
        try:
            # Set workspace
            cmd = [
                "az", "quantum", "workspace", "set",
                "-g", self.config.resource_group,
                "-w", self.config.workspace_name,
                "-l", self.config.location
            ]
            
            if self.config.subscription_id:
                cmd.extend(["-s", self.config.subscription_id])
            
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Set target solver
            subprocess.run(
                ["az", "quantum", "target", "set",
                 "--target-id", self.config.target_id],
                check=True, capture_output=True, text=True
            )
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to set up Azure Quantum workspace: {e.stderr or str(e)}"
            )
    
    def submit_qubo(self, problem: Dict) -> str:
        """Submit QUBO problem to Azure Quantum.
        
        Args:
            problem: QUBO problem in Azure Quantum format
            
        Returns:
            Job ID of the submitted job
        """
        # Create temporary file for problem JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(problem, f)
            problem_file = f.name
        
        try:
            # Submit job
            result = subprocess.run(
                ["az", "quantum", "job", "submit",
                 "--target-id", self.config.target_id,
                 "--input-file", problem_file],
                check=True, capture_output=True, text=True
            )
            
            try:
                # Parse job ID from result
                job_data = json.loads(result.stdout)
                job_id = job_data.get('id')
                
                if not job_id:
                    raise ValueError("No job ID in response")
                
                return job_id
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse job submission response: {e}")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to submit job: {e.stderr or str(e)}")
        finally:
            # Clean up temporary file
            Path(problem_file).unlink()
    
    def get_job_status(self, job_id: str) -> str:
        """Get status of a submitted job.
        
        Args:
            job_id: Job ID to check
            
        Returns:
            Status of the job
        """
        try:
            result = subprocess.run(
                ["az", "quantum", "job", "show",
                 "--job-id", job_id,
                 "-o", "json"],
                check=True, capture_output=True, text=True
            )
            
            try:
                job_data = json.loads(result.stdout)
                return job_data.get('status', 'Unknown')
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse job status response: {e}")
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get job status: {e.stderr or str(e)}")
    
    def get_job_result(self, job_id: str) -> Dict:
        """Get result of a completed job.
        
        Args:
            job_id: Job ID to get results for
            
        Returns:
            Job results including solution
        """
        try:
            result = subprocess.run(
                ["az", "quantum", "job", "output",
                 "--job-id", job_id,
                 "-o", "json"],
                check=True, capture_output=True, text=True
            )
            
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse job result response: {e}")
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get job results: {e.stderr or str(e)}")
    
    def wait_for_job(self, job_id: str, timeout_seconds: int = 300) -> Dict:
        """Wait for job completion and get results.
        
        Args:
            job_id: Job ID to wait for
            timeout_seconds: Maximum time to wait in seconds
            
        Returns:
            Job results including solution
            
        Raises:
            TimeoutError: If job doesn't complete within timeout
            RuntimeError: If job fails
        """
        try:
            subprocess.run(
                ["az", "quantum", "job", "wait",
                 "--job-id", job_id,
                 "--max-poll-wait-secs", str(timeout_seconds)],
                check=True, capture_output=True, text=True
            )
        except subprocess.CalledProcessError as e:
            if "timeout" in (e.stderr or "").lower():
                raise TimeoutError(f"Job {job_id} did not complete within {timeout_seconds} seconds")
            raise RuntimeError(f"Job {job_id} failed: {e.stderr or str(e)}")
        
        # Get final results
        return self.get_job_result(job_id)