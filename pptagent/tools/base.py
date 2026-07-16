"""Tool base class and registry mechanism

Common interfaces for all tools and the ToolRegistry.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolResult:
    """Tool execution result"""

    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseTool(ABC):
    """Tool base class

    NOTE: All tools must inherit this class and implement the execute() method.
    """

    name: str = ""
    description: str = ""
    schema: Dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool logic

        Args:
            **kwargs: tool parameters (defined by schema)

        Returns:
            ToolResult: result object containing success/data/error
        """

        pass

    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI Function Calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.schema,
            },
        }


class ToolRegistry:
    """Tool registry

    All tools must be registered with this registry during Agent init.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool"""
        if not tool.name:
            raise ValueError(f"Tool {tool.__class__.__name__} is missing 'name' attribute")
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        """Get a tool by name"""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered")
        return self._tools[name]

    def list_all(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get OpenAI Function Calling schemas for all tools"""
        return [tool.to_openai_schema() for tool in self._tools.values()]

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        """Check if a tool is registered"""
        return name in self._tools
