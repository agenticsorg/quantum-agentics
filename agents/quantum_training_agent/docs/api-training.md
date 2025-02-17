# Training API

This document details the training API for the Quantum Training Agent, including interfaces for model training, optimization, and evaluation.

## Training Classes

### 1. Model Trainer

```python
class ModelTrainer:
    """Main trainer class for model training and optimization."""
    
    def __init__(
        self,
        model: torch.nn.Module,
        config: TrainingConfig,
        quantum_optimizer: QuantumOptimizer = None
    ):
        """
        Initialize trainer with model and configuration.
        
        Args:
            model: The model to train
            config: Training configuration
            quantum_optimizer: Optional quantum optimizer
        """
        self.model = model
        self.config = config
        self.quantum_optimizer = quantum_optimizer
        self.setup_training()
    
    def train(
        self,
        train_dataloader: DataLoader,
        val_dataloader: DataLoader = None,
        callbacks: List[TrainingCallback] = None
    ) -> TrainingResult:
        """
        Train the model with quantum optimization.
        
        Args:
            train_dataloader: Training data loader
            val_dataloader: Optional validation data loader
            callbacks: Optional training callbacks
            
        Returns:
            TrainingResult containing metrics and model state
        """
        for epoch in range(self.config.num_epochs):
            self.train_epoch(train_dataloader)
            if val_dataloader:
                self.validate(val_dataloader)
            if self.should_optimize():
                self.quantum_optimize()
        return self.get_training_result()
    
    def train_epoch(self, dataloader: DataLoader) -> dict:
        """
        Train for one epoch.
        
        Args:
            dataloader: Data loader for training
            
        Returns:
            Dictionary of training metrics
        """
        self.model.train()
        for batch in dataloader:
            loss = self.train_step(batch)
            self.backward_step(loss)
            self.optimization_step()
        return self.get_epoch_metrics()
```

### 2. Training Step

```python
class TrainingStep:
    """Handles individual training steps and gradient updates."""
    
    def __init__(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None
    ):
        """
        Initialize training step handler.
        
        Args:
            model: Model to train
            optimizer: Optimizer for parameter updates
            scheduler: Optional learning rate scheduler
        """
        self.model = model
        self.optimizer = optimizer
        self.scheduler = scheduler
        
    def forward_step(
        self,
        batch: Dict[str, torch.Tensor]
    ) -> Tuple[torch.Tensor, dict]:
        """
        Perform forward pass and compute loss.
        
        Args:
            batch: Dictionary of input tensors
            
        Returns:
            Tuple of (loss, metrics)
        """
        with torch.cuda.amp.autocast():
            outputs = self.model(**batch)
            loss = outputs.loss
        return loss, self.compute_metrics(outputs)
    
    def backward_step(
        self,
        loss: torch.Tensor,
        gradient_accumulation: int = 1
    ) -> None:
        """
        Perform backward pass with gradient accumulation.
        
        Args:
            loss: Loss tensor
            gradient_accumulation: Number of steps for gradient accumulation
        """
        scaled_loss = loss / gradient_accumulation
        scaled_loss.backward()
```

### 3. Optimization Integration

```python
class OptimizationStep:
    """Handles quantum optimization integration in training."""
    
    def __init__(
        self,
        quantum_optimizer: QuantumOptimizer,
        optimization_frequency: int = 100
    ):
        """
        Initialize optimization step handler.
        
        Args:
            quantum_optimizer: Quantum optimization interface
            optimization_frequency: Steps between optimizations
        """
        self.quantum_optimizer = quantum_optimizer
        self.optimization_frequency = optimization_frequency
        
    def optimize_step(
        self,
        model: torch.nn.Module,
        metrics: dict
    ) -> OptimizationResult:
        """
        Perform quantum optimization step.
        
        Args:
            model: Current model state
            metrics: Training metrics
            
        Returns:
            Optimization results
        """
        problem = self.formulate_problem(model, metrics)
        solution = self.quantum_optimizer.solve(problem)
        return self.apply_solution(model, solution)
```

## Training Utilities

### 1. Data Management

```python
class DataManager:
    """Handles data loading and preprocessing."""
    
    def __init__(
        self,
        dataset: Dataset,
        batch_size: int,
        num_workers: int = 4
    ):
        """
        Initialize data manager.
        
        Args:
            dataset: PyTorch dataset
            batch_size: Batch size for training
            num_workers: Number of data loading workers
        """
        self.dataset = dataset
        self.batch_size = batch_size
        self.num_workers = num_workers
        
    def get_dataloader(
        self,
        shuffle: bool = True
    ) -> DataLoader:
        """
        Create data loader with optimized settings.
        
        Args:
            shuffle: Whether to shuffle data
            
        Returns:
            Configured DataLoader
        """
        return DataLoader(
            self.dataset,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            shuffle=shuffle,
            pin_memory=True
        )
```

### 2. Metrics Tracking

```python
class MetricsTracker:
    """Tracks and computes training metrics."""
    
    def __init__(self):
        """Initialize metrics tracker."""
        self.metrics = defaultdict(list)
        self.current_step = 0
        
    def update(
        self,
        metrics: dict,
        step: Optional[int] = None
    ) -> None:
        """
        Update metrics with new values.
        
        Args:
            metrics: Dictionary of metric values
            step: Optional step number
        """
        step = step or self.current_step
        for name, value in metrics.items():
            self.metrics[name].append((step, value))
        self.current_step = step + 1
        
    def get_summary(self) -> dict:
        """
        Get summary of tracked metrics.
        
        Returns:
            Dictionary of metric summaries
        """
        return {
            name: self.compute_summary(values)
            for name, values in self.metrics.items()
        }
```

## Training Callbacks

### 1. Callback Interface

```python
class TrainingCallback:
    """Base class for training callbacks."""
    
    def on_training_start(self, trainer: ModelTrainer) -> None:
        """Called when training starts."""
        pass
        
    def on_epoch_start(self, trainer: ModelTrainer, epoch: int) -> None:
        """Called at the start of each epoch."""
        pass
        
    def on_step_end(
        self,
        trainer: ModelTrainer,
        step: int,
        metrics: dict
    ) -> None:
        """Called after each training step."""
        pass
        
    def on_epoch_end(
        self,
        trainer: ModelTrainer,
        epoch: int,
        metrics: dict
    ) -> None:
        """Called at the end of each epoch."""
        pass
```

## Usage Examples

### 1. Basic Training

```python
# Initialize trainer
trainer = ModelTrainer(
    model=model,
    config=training_config,
    quantum_optimizer=quantum_optimizer
)

# Train model
result = trainer.train(
    train_dataloader=train_loader,
    val_dataloader=val_loader
)
```

### 2. Custom Training Loop

```python
# Custom training with callbacks
callbacks = [
    MetricsCallback(),
    CheckpointCallback(),
    EarlyStoppingCallback()
]

trainer = ModelTrainer(model, config)
trainer.train(
    train_loader,
    val_loader,
    callbacks=callbacks
)
```

## Related Documentation
- [Configuration API](api-configuration.md)
- [Optimization API](api-optimization.md)
- [Evaluation API](api-evaluation.md)