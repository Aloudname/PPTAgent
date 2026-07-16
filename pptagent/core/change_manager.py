"""Undo / redo stack for PPTDocument mutations.

Provides ChangeRecord for undo,
and ChangeManager, a double-ended stack tracks changes.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChangeRecord:
    """A single undo/redo change.

    ## Attributes
    - ``id``:
        Unique change id.
    - ``timestamp``:
        ``time.time()`` when the change was recorded.
    - ``operation``:
        Operation name, e.g. ``"format_text"``.
    - ``target_element``:
        Changed ``element_id``.
    - ``slide_index``:
        Slide id of the changed element.
    - ``before_state``:
        ``Any`` snapshot before change, tool-specific.
    - ``after_state``:
        ``Any`` snapshot after change, tool-specific.
    """

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    timestamp: float | None = field(default_factory=time.time)
    operation: str = ""
    target_element: str = ""
    slide_index: int = 0
    before_state: Any = None
    after_state: Any = None


class ChangeManager:
    """Manages undo/redo stacks for a `PPTDocument`.

    ## Constraints
    - ``max_history`` limits the undo-stack size, default 16.
    - Recording a new change **clears** the redo stack.
    """

    def __init__(self, max_history: int = 16) -> None:
        self.undo_stack: list[ChangeRecord] = []
        self.redo_stack: list[ChangeRecord] = []
        self.max_history: int = max_history

    # core APIs
    def record(self, change: ChangeRecord) -> None:
        """Push *change* onto the undo stack.

        Side-effects:
        - Clears the redo stack.
        - If ``len(undo_stack) > max_history``, drop oldest record.
        """
        self.redo_stack.clear()
        self.undo_stack.append(change)
        # drop oldest
        while len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

    def undo(self) -> ChangeRecord | None:
        """Pop the most recent change from undo, push to redo.

        ## Returns
        ``ChangeRecord`` | ``None``
            The undone record, or ``None`` if the undo stack is empty.
        """
        if not self.undo_stack:
            return None
        record = self.undo_stack.pop()
        self.redo_stack.append(record)
        return record

    def redo(self) -> ChangeRecord | None:
        """Pop the most recent undone change from redo, push it to undo.

        ## Returns
        ``ChangeRecord`` | ``None``
            The redone record, or ``None`` if the redo stack is empty.
        """
        if not self.redo_stack:
            return None
        record = self.redo_stack.pop()
        self.undo_stack.append(record)
        return record

    def clear(self) -> None:
        """Clear both stacks, e.g. when closing a document."""
        self.undo_stack.clear()
        self.redo_stack.clear()

    # convenience predicates
    def can_undo(self) -> bool:
        """Return ``True`` if there is at least one undoable change."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Return ``True`` if there is at least one redoable change."""
        return len(self.redo_stack) > 0

    def __len__(self) -> int:
        """Total number of tracked changes."""
        return len(self.undo_stack) + len(self.redo_stack)
