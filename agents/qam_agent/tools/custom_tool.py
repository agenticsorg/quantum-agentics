from typing import Any, Optional
from langchain.tools import BaseTool

class CustomTool(BaseTool):
    """A custom tool template that can be extended for specific use cases."""
    
    name: str = "custom_tool"
    description: str = "A custom tool that can be implemented for specific tasks"

    def _run(self, query: str) -> Any:
        """Use the tool.
        
        Args:
            query: The input query to process
            
        Returns:
            The result of the tool execution
        """
        return f"Processed query: {query}"

    async def _arun(self, query: str) -> Any:
        """Use the tool asynchronously."""
        raise NotImplementedError("Async version not implemented")
