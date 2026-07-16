"""T36: delete_slide, remove a slide by index."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from pptagent.core.change_manager import ChangeRecord
from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult

if TYPE_CHECKING:
    from pptagent.core.document import PPTDocument


class DeleteSlideTool(BaseTool):
    name = "delete_slide"
    description = "Delete a slide by index."

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based index of the slide to delete.",
            },
        },
        "required": ["slide_index"],
    }

    async def execute(  # type: ignore[override]
        self, slide_index: int
    ) -> ToolResult:
        session = get_session()
        doc: PPTDocument | None = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        if not 0 <= slide_index < len(doc.slides):
            return ToolResult(
                success=False,
                error=f"Slide index {slide_index} out of range 0-{len(doc.slides) - 1}.",
            )

        before = copy.deepcopy(doc.slides)
        removed = doc.slides.pop(slide_index)  # noqa: F841
        self._reindex(doc)
        after = copy.deepcopy(doc.slides)

        self._record(doc, "delete_slide", "", slide_index, before, after)

        return ToolResult(
            success=True,
            data={
                "message": f"Deleted slide {slide_index}",
                "removed_slide_index": slide_index,
                "total_slides": len(doc.slides),
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
