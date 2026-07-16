"""PPTAgent custom exceptions

All exceptions inherit from PPTAgentError.
External callers only need to catch PPTAgentError.
Internal modules can catch specific subclasses for targeted handling.
"""

from __future__ import annotations

from typing import Optional


class PPTAgentError(Exception):
    """Base class for all PPTAgent exceptions"""

    def __init__(self, message: str = "",
                  *, detail: Optional[dict] = None) -> None:
        super().__init__(message)
        self.detail = detail or {}


class PPTFileNotFoundError(PPTAgentError):
    """Specified PPT file does not exist"""
    pass


class ElementNotFoundError(PPTAgentError):
    """Specified PPT element (text box, image, table, etc.) does not exist"""
    pass


class FormatNotSupportedError(PPTAgentError):
    """File or element format is not supported"""
    pass


class InvalidOperationError(PPTAgentError):
    """Invalid operation in PPT level"""
    pass


class ToolExecutionError(PPTAgentError):
    """An error occurred during tool execution"""
    pass


class ConversionError(PPTAgentError):
    """File format conversion failed"""
    pass


class RenderingError(PPTAgentError):
    """Formula / chart / diagram rendering failed"""
    pass


class ConfigError(PPTAgentError):
    """Config error"""
    pass
