# Evaluation API

This document details the evaluation API for the Quantum Training Agent, including interfaces for metrics computation, analysis, and visualization.

## Evaluation Classes

### 1. Model Evaluator

```python
class ModelEvaluator:
    """Main interface for model evaluation."""
    
    def __init__(
        self,
        model: torch.nn.Module,
        metrics: List[Metric] = None,
        device: str = "cuda"
    ):
        """
        Initialize model evaluator.
        
        Args:
            model: Model to evaluate
            metrics: List of metrics to compute
            device: Device for computation
        """
        self.model = model
        self.metrics = metrics or default_metrics()
        self.device = device
    
    def evaluate(
        self,
        dataloader: DataLoader,
        quantum_metrics: bool = True
    ) -> EvaluationResult:
        """
        Evaluate model performance.
        
        Args:
            dataloader: Evaluation data
            quantum_metrics: Include quantum metrics
            
        Returns:
            Evaluation results
        """
        metrics = self.compute_metrics(dataloader)
        if quantum_metrics:
            metrics.update(self.compute_quantum_metrics())
        return EvaluationResult(metrics)
    
    def compute_metrics(
        self,
        dataloader: DataLoader
    ) -> Dict[str, float]:
        """
        Compute evaluation metrics.
        
        Args:
            dataloader: Evaluation data
            
        Returns:
            Dictionary of metric values
        """
        results = {}
        for metric in self.metrics:
            results[metric.name] = metric.compute(
                self.model,
                dataloader
            )
        return results
```

### 2. Metrics Computation

```python
class MetricsComputer:
    """Handles computation of various metrics."""
    
    def __init__(self):
        """Initialize metrics computer."""
        self.metrics = {}
        
    def add_metric(
        self,
        name: str,
        metric: Callable,
        **kwargs
    ) -> None:
        """
        Add new metric for computation.
        
        Args:
            name: Metric name
            metric: Metric computation function
            **kwargs: Additional parameters
        """
        self.metrics[name] = {
            'func': metric,
            'params': kwargs
        }
    
    def compute_all(
        self,
        model: torch.nn.Module,
        data: torch.Tensor
    ) -> Dict[str, float]:
        """
        Compute all registered metrics.
        
        Args:
            model: Model to evaluate
            data: Input data
            
        Returns:
            Dictionary of metric values
        """
        results = {}
        for name, metric in self.metrics.items():
            results[name] = metric['func'](
                model,
                data,
                **metric['params']
            )
        return results
```

### 3. Performance Analysis

```python
class PerformanceAnalyzer:
    """Analyzes model performance and resource usage."""
    
    def __init__(
        self,
        model: torch.nn.Module,
        quantum_optimizer: QuantumOptimizer = None
    ):
        """
        Initialize performance analyzer.
        
        Args:
            model: Model to analyze
            quantum_optimizer: Optional quantum optimizer
        """
        self.model = model
        self.quantum_optimizer = quantum_optimizer
        
    def analyze_performance(
        self,
        test_data: DataLoader
    ) -> PerformanceReport:
        """
        Analyze model performance.
        
        Args:
            test_data: Test dataset
            
        Returns:
            Performance analysis report
        """
        metrics = self.compute_metrics(test_data)
        resources = self.analyze_resources()
        efficiency = self.analyze_efficiency()
        return PerformanceReport(
            metrics=metrics,
            resources=resources,
            efficiency=efficiency
        )
```

## Evaluation Metrics

### 1. Training Metrics

```python
class TrainingMetrics:
    """Computes training-related metrics."""
    
    @staticmethod
    def compute_loss(
        model: torch.nn.Module,
        data: torch.Tensor,
        criterion: torch.nn.Module
    ) -> float:
        """
        Compute model loss.
        
        Args:
            model: Model to evaluate
            data: Input data
            criterion: Loss function
            
        Returns:
            Loss value
        """
        with torch.no_grad():
            outputs = model(data)
            loss = criterion(outputs, data)
        return loss.item()
    
    @staticmethod
    def compute_perplexity(
        model: torch.nn.Module,
        data: torch.Tensor
    ) -> float:
        """
        Compute model perplexity.
        
        Args:
            model: Model to evaluate
            data: Input data
            
        Returns:
            Perplexity value
        """
        loss = TrainingMetrics.compute_loss(
            model, data, torch.nn.CrossEntropyLoss()
        )
        return math.exp(loss)
```

### 2. Quantum Metrics

```python
class QuantumMetrics:
    """Computes quantum optimization metrics."""
    
    def __init__(self, optimizer: QuantumOptimizer):
        """
        Initialize quantum metrics.
        
        Args:
            optimizer: Quantum optimizer
        """
        self.optimizer = optimizer
        
    def compute_optimization_quality(
        self,
        problem: OptimizationProblem
    ) -> float:
        """
        Compute optimization quality metric.
        
        Args:
            problem: Optimization problem
            
        Returns:
            Quality score
        """
        solution = self.optimizer.optimize(problem)
        return self.evaluate_solution(solution)
```

## Visualization

### 1. Training Visualization

```python
class TrainingVisualizer:
    """Visualizes training progress and results."""
    
    def __init__(self, save_dir: str = "plots"):
        """
        Initialize training visualizer.
        
        Args:
            save_dir: Directory for saving plots
        """
        self.save_dir = save_dir
        
    def plot_training_progress(
        self,
        metrics: Dict[str, List[float]],
        save: bool = True
    ) -> None:
        """
        Plot training metrics over time.
        
        Args:
            metrics: Training metrics
            save: Whether to save plots
        """
        plt.figure(figsize=(12, 6))
        for name, values in metrics.items():
            plt.plot(values, label=name)
        plt.legend()
        if save:
            plt.savefig(f"{self.save_dir}/training.png")
```

## Usage Examples

### 1. Basic Evaluation

```python
# Initialize evaluator
evaluator = ModelEvaluator(
    model=model,
    metrics=[
        Perplexity(),
        Accuracy(),
        F1Score()
    ]
)

# Evaluate model
results = evaluator.evaluate(test_dataloader)
```

### 2. Performance Analysis

```python
# Analyze performance
analyzer = PerformanceAnalyzer(
    model=model,
    quantum_optimizer=optimizer
)

report = analyzer.analyze_performance(test_data)
print(report.summary())
```

## Related Documentation
- [Training API](api-training.md)
- [Optimization API](api-optimization.md)
- [Configuration API](api-configuration.md)