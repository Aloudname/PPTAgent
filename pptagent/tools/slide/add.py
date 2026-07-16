"""T35: add_slide, insert a new blank slide."""

from __future__ import annotations

import copy

from pptagent.core.change_manager import ChangeManager, ChangeRecord
from pptagent.core.document import PPTDocument, Slide
from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class AddSlideTool(BaseTool):
    name = "add_slide"
    description = "Add a new blank slide at the specified position."

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "position": {
                "type": "integer",
                "description": "0-based insertion position. Omit to append at end.",
            },
            "layout": {
                "type": "string",
                "description": "Slide layout name, default 'Blank'",
            },
        },
    }

    async def execute(  # type: ignore[override]
        self,
        position: int | None = None,
        layout: str = "Blank",
    ) -> ToolResult:
        session = get_session()
        doc: PPTDocument | None = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        if position is None:
            position = len(doc.slides)

        if not 0 <= position <= len(doc.slides):
            return ToolResult(
                success=False,
                error=f"Position index {position} out of range 0-{len(doc.slides)}.",
            )

        # snapshot
        before = copy.deepcopy(doc.slides)

        new_slide = Slide(index=position, layout_name=layout)
        doc.slides.insert(position, new_slide)
        self._reindex(doc)

        # record change
        self._record(doc, "add_slide", "", position, before, copy.deepcopy(doc.slides))

        return ToolResult(
            success=True,
            data={
                "message": f"Added slide at position {position}",
                "slide_index": position,
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
        cm: ChangeManager | None = getattr(doc, "_change_manager", None)
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
