class ReactValidator:
    def __init__(self, validation_rules):
        self.rules = validation_rules
        self.current_step = 0
        self.total_steps = 0
        self.is_complete = False
        self.stream_history = []

    def validate_thought(self, thought):
        if not thought.startswith("Thought:"): 
            return False
        if len(thought) < self.rules["thought"]["min_length"]:
            return False
        return True

    def validate_action(self, action):
        if not action.startswith("Action:"): 
            return False
        # Check if action has both name and parameters
        if "(" not in action or ")" not in action:
            return False
        return True

    def validate_observation(self, observation):
        return observation.startswith("Observation:")

    def start_tracking(self, task_name):
        self.current_step = 0
        self.total_steps = 0
        self.is_complete = False

    def update_progress(self, current, total, message):
        self.current_step = current
        self.total_steps = total
        return (current / total * 100) if total > 0 else 0

    def complete_task(self):
        self.is_complete = True

    def create_stream(self):
        return {"history": self.stream_history}

    def stream_update(self, message):
        self.stream_history.append(message)
