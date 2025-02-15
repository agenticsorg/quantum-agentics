import yaml
import os

class ConfigLoader:
    def __init__(self):
        self.config_dir = "src/hello_world/config"

    def load_prompts(self):
        with open(os.path.join(self.config_dir, "prompts.yaml"), "r") as f:
            return yaml.safe_load(f)

    def apply_defaults(self, config):
        if "templates" not in config:
            config["templates"] = {}

        if "validation_rules" not in config["templates"]:
            config["templates"]["validation_rules"] = {
                "thought": {
                    "format": "Thought: {reasoning}",
                    "min_length": 20
                },
                "action": {
                    "format": "Action: {action_name}({params})",
                    "required_fields": ["action_name", "params"]
                }
            }

        if "progress_tracking" not in config["templates"]:
            config["templates"]["progress_tracking"] = {
                "format": "{timestamp} - {agent_name} - {status} - {message}",
                "statuses": ["started", "in_progress", "completed", "error"]
            }

        return config

    def validate_config(self, config):
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")

        if "templates" not in config:
            raise ValueError("Missing required templates section")

        if "user_prompts" not in config["templates"]:
            raise ValueError("Missing required user_prompts section")
