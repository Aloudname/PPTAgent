"""T37: reorder_slides, change order of slides."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from pptagent.core.change_manager import ChangeRecord
from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult

if TYPE_CHECKING:
    from pptagent.core.document import PPTDocument


class ReorderSlidesTool(BaseTool):
    name = "reorder_slides"
    description = "Change the order of slides by providing a new index ordering."

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "new_order": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Permutation of current slide indices, e.g. [2,0,1].",
            },
        },
        "required": ["new_order"],
    }

    async def execute(  # type: ignore[override]
        self, new_order: list[int]
    ) -> ToolResult:
        session = get_session()
        doc: PPTDocument | None = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        n = len(doc.slides)
        if sorted(new_order) != list(range(n)):
            return ToolResult(
                success=False,
                error=f"new_order must be a permutation of 0-{n - 1}, got {new_order}",
            )

        before = copy.deepcopy(doc.slides)
        doc.slides = [doc.slides[i] for i in new_order]
        self._reindex(doc)
        after = copy.deepcopy(doc.slides)

        self._record(doc, "reorder_slides", "", 0, before, after)

        return ToolResult(
            success=True,
            data={
                "message": "Slides reordered",
                "new_order": new_order,
                "total_slides": n,
            },
        )

    @staticmethod
    def _reindex(doc: PPTDocument) -> None:
        for i, slide in enumerate(doc.slides):
            slide.index = i

    @staticmethod
    def _record(
        doc: PPTDocument,
        operation: str,
        target: str,
        slide_idx: int,
        before: object,
        after: object,
    ) -> None:
        cm = getattr(doc, "_change_manager", None)
        if cm is None:
            return
        cm.record(
            ChangeRecord(
                operation=operation,
                target_element=target,
                slide_index=slide_idx,
                before_state=before,
                after_state=after,
            )
        )
