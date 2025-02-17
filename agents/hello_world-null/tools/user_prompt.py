from typing import Any, Dict, Optional
from pydantic import Field
from .custom_tool import CustomTool
import json

class BaseUserPrompt(CustomTool):
    name = "base_user_prompt"
    description = "Base class for user prompt systems with validation and progress tracking"
    
    current_step: int = Field(default=0)
    total_steps: int = Field(default=0)
    status: str = Field(default="")

    def validate_input(self, input_data: Dict, schema: Dict) -> bool:
        # Basic schema validation
        try:
            for key, expected_type in schema.items():
                if key not in input_data:
                    raise ValueError(f"Missing required field: {key}")
                if not isinstance(input_data[key], expected_type):
                    raise TypeError(f"Invalid type for {key}")
            return True
        except (ValueError, TypeError) as e:
            self.status = f"Validation error: {str(e)}"
            return False

    def format_response(self, response_data: Any, format_type: str = "text") -> str:
        if format_type == "text":
            return str(response_data)
        elif format_type == "json":
            return json.dumps(response_data)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    def track_progress(self, step: int, total_steps: int) -> float:
        self.current_step = step
        self.total_steps = total_steps
        return (step / total_steps) * 100 if total_steps > 0 else 0

    def update_status(self, status_message: str) -> None:
        self.status = status_message

    def _sanitize_input(self, input_data: str) -> str:
        # Basic input sanitization
        return input_data.strip()

    def _run(self, query: str) -> Any:
        # Base implementation
        sanitized_query = self._sanitize_input(query)
        return f"Processed query: {sanitized_query}"

    async def _arun(self, query: str) -> Any:
        raise NotImplementedError("Async version not implemented")
