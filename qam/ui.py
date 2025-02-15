import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

class QuantumSchedulerUI:
    def __init__(self):
        self.param_widgets = {}
        self.task_widgets = {}
        self.monitoring_widgets = {}
        self.setup_parameter_widgets()
        self.setup_task_input()
        self.setup_monitoring()
        
    def setup_parameter_widgets(self):
        """Setup widgets for quantum scheduler parameters"""
        self.param_widgets['num_qubits'] = widgets.IntSlider(
            value=4,
            min=2,
            max=20,
            description='Num Qubits:',
            style={'description_width': 'initial'}
        )
        
        self.param_widgets['solver_type'] = widgets.Dropdown(
            options=['D-Wave', 'IonQ-QAOA', 'Hybrid'],
            value='D-Wave',
            description='Solver:',
            style={'description_width': 'initial'}
        )
        
        self.param_widgets['optimization_level'] = widgets.IntSlider(
            value=1,
            min=0,
            max=3,
            description='Optimization Level:',
            style={'description_width': 'initial'}
        )
        
        self.param_container = widgets.VBox([
            widgets.HTML("<h3>Parameter Configuration</h3>"),
            self.param_widgets['num_qubits'],
            self.param_widgets['solver_type'],
            self.param_widgets['optimization_level']
        ])
        
    def setup_task_input(self):
        """Setup widgets for task and agent input"""
        self.task_widgets['task_name'] = widgets.Text(
            description='Task Name:',
            style={'description_width': 'initial'}
        )
        
        self.task_widgets['duration'] = widgets.IntText(
            value=1,
            description='Duration (hrs):',
            style={'description_width': 'initial'}
        )
        
        self.task_widgets['dependencies'] = widgets.Text(
            description='Dependencies:',
            placeholder='task1,task2',
            style={'description_width': 'initial'}
        )
        
        self.task_widgets['add_button'] = widgets.Button(
            description='Add Task',
            button_style='success'
        )
        
        self.task_widgets['task_list'] = widgets.Output()
        
        self.task_container = widgets.VBox([
            widgets.HTML("<h3>Task Management</h3>"),
            self.task_widgets['task_name'],
            self.task_widgets['duration'],
            self.task_widgets['dependencies'],
            self.task_widgets['add_button'],
            self.task_widgets['task_list']
        ])
        
        self.task_widgets['add_button'].on_click(self._add_task_callback)
        
    def setup_monitoring(self):
        """Setup widgets for real-time monitoring"""
        self.monitoring_widgets['status'] = widgets.HTML(
            value="<h4>Status: Idle</h4>"
        )
        
        self.monitoring_widgets['progress'] = widgets.FloatProgress(
            value=0,
            min=0,
            max=100,
            description='Progress:',
            style={'description_width': 'initial'}
        )
        
        self.monitoring_widgets['graph'] = widgets.Output()
        
        self.monitoring_container = widgets.VBox([
            widgets.HTML("<h3>Monitoring</h3>"),
            self.monitoring_widgets['status'],
            self.monitoring_widgets['progress'],
            self.monitoring_widgets['graph']
        ])
        
    def _add_task_callback(self, button):
        """Callback for adding a new task"""
        with self.task_widgets['task_list']:
            clear_output()
            task_name = self.task_widgets['task_name'].value
            duration = self.task_widgets['duration'].value
            dependencies = self.task_widgets['dependencies'].value.split(',') if self.task_widgets['dependencies'].value else []
            print(f"Added task: {task_name} (Duration: {duration}hrs, Dependencies: {dependencies})")
            
    def update_monitoring(self, status, progress):
        """Update monitoring display"""
        self.monitoring_widgets['status'].value = f"<h4>Status: {status}</h4>"
        self.monitoring_widgets['progress'].value = progress
        
    def plot_schedule(self, tasks):
        """Plot schedule using Plotly Gantt chart"""
        with self.monitoring_widgets['graph']:
            clear_output()
            if not tasks:
                raise ValueError("No tasks to display")
                
            df = []
            for task in tasks:
                df.append(dict(
                    Task=task['name'],
                    Start=task['start'],
                    Finish=task['end'],
                    Resource=task.get('resource', 'Default')
                ))
                
            fig = ff.create_gantt(df, index_col='Resource',
                                show_colorbar=True,
                                group_tasks=True)
            fig.show()
            
    def display(self):
        """Display the complete UI"""
        display(widgets.VBox([
            self.param_container,
            self.task_container,
            self.monitoring_container
        ]))