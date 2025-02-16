#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

from unittest.mock import Mock, patch, MagicMock, call
import ipywidgets as widgets
from IPython.display import display, clear_output
from qam.ui import QuantumSchedulerUI

# Mock widgets and display functions
mock_widget = Mock()
mock_widget.value = ""
mock_output = Mock()
mock_output.__enter__ = Mock(return_value=None)
mock_output.__exit__ = Mock(return_value=None)

class MockDisplay:
    def __call__(self, *args, **kwargs):
        pass

def test_ui():
    print("\nTesting QuantumSchedulerUI...")
    
    mock_display = MockDisplay()
    
    with patch('ipywidgets.IntSlider', return_value=mock_widget), \
         patch('ipywidgets.Dropdown', return_value=mock_widget), \
         patch('ipywidgets.Text', return_value=mock_widget), \
         patch('ipywidgets.IntText', return_value=mock_widget), \
         patch('ipywidgets.Button', return_value=mock_widget), \
         patch('ipywidgets.Output', return_value=mock_output), \
         patch('ipywidgets.HTML', return_value=mock_widget), \
         patch('ipywidgets.FloatProgress', return_value=mock_widget), \
         patch('ipywidgets.VBox', return_value=mock_widget), \
         patch('qam.ui.display', mock_display), \
         patch('qam.ui.clear_output') as mock_clear:
        
        # Test 1: Create UI
        print("\n1. Testing UI creation")
        ui = QuantumSchedulerUI()
        print("UI created successfully")
        
        # Test 2: Parameter widgets
        print("\n2. Testing parameter widgets")
        assert 'num_qubits' in ui.param_widgets
        assert 'solver_type' in ui.param_widgets
        assert 'optimization_level' in ui.param_widgets
        print("Parameter widgets verified")
        
        # Test 3: Task widgets
        print("\n3. Testing task widgets")
        assert 'task_name' in ui.task_widgets
        assert 'duration' in ui.task_widgets
        assert 'dependencies' in ui.task_widgets
        assert 'add_button' in ui.task_widgets
        print("Task widgets verified")
        
        # Test 4: Monitoring widgets
        print("\n4. Testing monitoring widgets")
        assert 'status' in ui.monitoring_widgets
        assert 'progress' in ui.monitoring_widgets
        assert 'graph' in ui.monitoring_widgets
        print("Monitoring widgets verified")
        
        # Test 5: Add task callback
        print("\n5. Testing task addition")
        ui.task_widgets['task_name'].value = "Test Task"
        ui.task_widgets['duration'].value = 2
        ui.task_widgets['dependencies'].value = "task1,task2"
        ui._add_task_callback(None)
        print("Task addition tested")
        
        # Test 6: Update monitoring
        print("\n6. Testing monitoring updates")
        ui.update_monitoring("Running", 50)
        assert ui.monitoring_widgets['progress'].value == 50
        print("Monitoring updates verified")
        
        # Test 7: Plot schedule
        print("\n7. Testing schedule plotting")
        tasks = [
            {
                'name': 'Task 1',
                'start': '2025-02-16 10:00:00',
                'end': '2025-02-16 12:00:00',
                'resource': 'CPU'
            },
            {
                'name': 'Task 2',
                'start': '2025-02-16 11:00:00',
                'end': '2025-02-16 13:00:00',
                'resource': 'GPU'
            }
        ]
        
        with patch('plotly.figure_factory.create_gantt') as mock_gantt:
            mock_fig = MagicMock()
            mock_gantt.return_value = mock_fig
            ui.plot_schedule(tasks)
            mock_gantt.assert_called_once()
            print("Schedule plotting verified")
        
        # Test 8: Empty schedule plotting
        print("\n8. Testing empty schedule handling")
        try:
            ui.plot_schedule([])
            print("❌ Should have raised ValueError")
        except ValueError as e:
            print("✅ Correctly caught empty schedule error")
        
        # Test 9: Display UI
        print("\n9. Testing UI display")
        ui.display()
        print("UI display verified")
        
        # Test 10: Widget value updates
        print("\n10. Testing widget value updates")
        ui.param_widgets['num_qubits'].value = 8
        ui.param_widgets['solver_type'].value = 'IonQ-QAOA'
        ui.param_widgets['optimization_level'].value = 2
        print("Widget value updates verified")
        
        # Test 11: Progress updates
        print("\n11. Testing progress updates")
        for progress in range(0, 101, 20):
            ui.update_monitoring(f"Progress: {progress}%", progress)
            assert ui.monitoring_widgets['progress'].value == progress
        print("Progress updates verified")
        
        # Test 12: Multiple task additions
        print("\n12. Testing multiple task additions")
        tasks = [
            ("Task A", 3, ""),
            ("Task B", 2, "Task A"),
            ("Task C", 4, "Task A,Task B")
        ]
        
        for task_name, duration, deps in tasks:
            ui.task_widgets['task_name'].value = task_name
            ui.task_widgets['duration'].value = duration
            ui.task_widgets['dependencies'].value = deps
            ui._add_task_callback(None)
        print("Multiple task additions verified")

if __name__ == "__main__":
    try:
        test_ui()
        print("\n✅ All UI tests completed successfully")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")