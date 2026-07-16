"""Session state management.

Provides per-user-session SessionState and WorkingMemory,
scratchpad for the Agent during a single task.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pptagent.core.document import PPTDocument


@dataclass
class WorkingMemory:
    """Agent's scratchpad during a single task.

    Stores intermediate observations, extracted elements,
    and user preferences gathered during the session.
    """

    user_preferences: dict[str, Any] = field(default_factory=dict)
    context_summary: str = ""
    extracted_elements: dict[str, Any] = field(default_factory=dict)
    recent_operations: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)


@dataclass
class SessionState:
    """Per-session state that persists across multiple tasks.

    Holds the currently open document, a list of previously
    opened files, task history, and the working memory.
    """

    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    current_document: PPTDocument | None = None
    open_files: list[str] = field(default_factory=list)
    task_history: list[Any] = field(default_factory=list)
    memory: WorkingMemory = field(default_factory=WorkingMemory)


# Module-level singleton — shared by all tools within the same process
_session: SessionState | None = None


def get_session() -> SessionState:
    """Return or lazily create the global SessionState singleton."""
    global _session
    if _session is None:
        _session = SessionState()
    return _session


def reset_session() -> None:
    """
    Reset the global session.
    e.g. between test cases.
    """
    global _session
    _session = SessionState()
