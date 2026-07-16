"""T38: duplicate_slide, copy an existing slide."""

from __future__ import annotations

import copy
import uuid
from typing import TYPE_CHECKING

from pptagent.core.change_manager import ChangeRecord
from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult

if TYPE_CHECKING:
    from pptagent.core.document import Element, PPTDocument


class DuplicateSlideTool(BaseTool):
    name = "duplicate_slide"
    description = "Duplicate an existing slide."

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based index of the slide to duplicate.",
            },
            "insert_after": {
                "type": "boolean",
                "description": "Insert after the source (default true). If false, insert before.",
            },
        },
        "required": ["slide_index"],
    }

    async def execute(  # type: ignore[override]
        self, slide_index: int, insert_after: bool = True
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

        # deep-copy and regenerate element IDs
        original = doc.slides[slide_index]
        clone = copy.deepcopy(original)
        new_elements: dict[str, Element] = {}
        for old_id, elem in clone.elements.items():  # noqa: B007
            new_id = f"{elem.type}_{uuid.uuid4().hex[:8]}"
            elem.id = new_id
            new_elements[new_id] = elem
        clone.elements = new_elements

        insert_pos = slide_index + 1 if insert_after else slide_index
        doc.slides.insert(insert_pos, clone)
        self._reindex(doc)

        after = copy.deepcopy(doc.slides)
        self._record(doc, "duplicate_slide", "", insert_pos, before, after)

        return ToolResult(
            success=True,
            data={
                "message": f"Duplicated slide {slide_index} → position {insert_pos}",
                "source_index": slide_index,
                "new_index": insert_pos,
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
