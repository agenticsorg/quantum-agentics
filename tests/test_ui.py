import pytest
from qam.ui import QuantumSchedulerUI
import ipywidgets as widgets
from datetime import datetime, timedelta

def test_parameter_widgets_creation():
    ui = QuantumSchedulerUI()
    assert isinstance(ui.param_widgets['num_qubits'], widgets.IntSlider)
    assert isinstance(ui.param_widgets['solver_type'], widgets.Dropdown)
    assert isinstance(ui.param_widgets['optimization_level'], widgets.IntSlider)
    
    # Test default values
    assert ui.param_widgets['num_qubits'].value == 4
    assert ui.param_widgets['solver_type'].value == 'D-Wave'
    assert ui.param_widgets['optimization_level'].value == 1

def test_task_input_widgets_creation():
    ui = QuantumSchedulerUI()
    assert isinstance(ui.task_widgets['task_name'], widgets.Text)
    assert isinstance(ui.task_widgets['duration'], widgets.IntText)
    assert isinstance(ui.task_widgets['dependencies'], widgets.Text)
    assert isinstance(ui.task_widgets['add_button'], widgets.Button)
    
    # Test default values
    assert ui.task_widgets['duration'].value == 1
    assert ui.task_widgets['dependencies'].placeholder == 'task1,task2'

def test_monitoring_widgets_creation():
    ui = QuantumSchedulerUI()
    assert isinstance(ui.monitoring_widgets['status'], widgets.HTML)
    assert isinstance(ui.monitoring_widgets['progress'], widgets.FloatProgress)
    assert isinstance(ui.monitoring_widgets['graph'], widgets.Output)
    
    # Test default values
    assert ui.monitoring_widgets['progress'].value == 0
    assert "Status: Idle" in ui.monitoring_widgets['status'].value

def test_update_monitoring():
    ui = QuantumSchedulerUI()
    ui.update_monitoring("Running", 50)
    
    assert "Status: Running" in ui.monitoring_widgets['status'].value
    assert ui.monitoring_widgets['progress'].value == 50

def test_plot_schedule():
    ui = QuantumSchedulerUI()
    
    # Test empty tasks
    with pytest.raises(ValueError, match="No tasks to display"):
        ui.plot_schedule([])
    
    # Test with sample tasks
    now = datetime.now()
    tasks = [
        {
            'name': 'Task 1',
            'start': now,
            'end': now + timedelta(hours=2),
            'resource': 'Resource 1'
        },
        {
            'name': 'Task 2',
            'start': now + timedelta(hours=2),
            'end': now + timedelta(hours=4),
            'resource': 'Resource 2'
        }
    ]
    
    # This should not raise any exception
    ui.plot_schedule(tasks)

def test_display_integration():
    ui = QuantumSchedulerUI()
    
    # Test that all containers are created
    assert hasattr(ui, 'param_container')
    assert hasattr(ui, 'task_container')
    assert hasattr(ui, 'monitoring_container')
    
    # Test that containers have correct widget types
    assert isinstance(ui.param_container, widgets.VBox)
    assert isinstance(ui.task_container, widgets.VBox)
    assert isinstance(ui.monitoring_container, widgets.VBox)

def test_task_addition_callback():
    ui = QuantumSchedulerUI()
    
    # Set up test task data
    ui.task_widgets['task_name'].value = "Test Task"
    ui.task_widgets['duration'].value = 3
    ui.task_widgets['dependencies'].value = "task1,task2"
    
    # Simulate button click
    ui.task_widgets['add_button']._click_handlers(ui.task_widgets['add_button'])
    
    # Unfortunately, we can't directly test the output widget content in a unit test
    # But we can verify the widget exists and is of correct type
    assert isinstance(ui.task_widgets['task_list'], widgets.Output)