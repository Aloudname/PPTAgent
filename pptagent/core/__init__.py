"""Core module: data models, state management, format conversion"""

from pptagent.core.change_manager import ChangeManager, ChangeRecord
from pptagent.core.converter import convert_ppt_to_pptx, find_libreoffice
from pptagent.core.document import (
    BackgroundInfo,
    CursorState,
    Element,
    PPTDocument,
    Slide,
    TextFormat,
)
from pptagent.core.session import SessionState, WorkingMemory, get_session, reset_session

__all__ = [
    "BackgroundInfo",
    "ChangeManager",
    "ChangeRecord",
    "CursorState",
    "Element",
    "PPTDocument",
    "SessionState",
    "Slide",
    "TextFormat",
    "WorkingMemory",
    "convert_ppt_to_pptx",
    "find_libreoffice",
    "get_session",
    "reset_session",
]
