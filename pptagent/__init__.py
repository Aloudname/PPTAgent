"""
PPTAgent: PPT Agent for Study & Research

An intelligent PPT-making agent for researchers.

It understands user intents through natural language interaction,
orchestrates tools to read, analyze, edit, generate, beautify, and save PowerPoints.

A database for academic papers is planned in future,
so hopefully it'll support auto-searching, summarizing and remembering academic papers when given a field,
and making PPTs based on one specific paper or all latest research progresses in specific field.
"""

__version__ = "0.1.0"
__author__ = "Aloudname"
__license__ = "MIT"

from pptagent.core.exceptions import (
    ConfigError,
    ElementNotFoundError,
    FormatNotSupportedError,
    InvalidOperationError,
    PPTAgentError,
    PPTFileNotFoundError,
    ToolExecutionError,
)

__all__: list[str] = [
    "ConfigError",
    "ElementNotFoundError",
    "FormatNotSupportedError",
    "InvalidOperationError",
    "PPTAgentError",
    "PPTFileNotFoundError",
    "ToolExecutionError",
    "__version__",
]
