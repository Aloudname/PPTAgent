"""T19: remove an element from a slide."""

from __future__ import annotations

import copy

from pptagent.core.change_manager import ChangeRecord
from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class DeleteElementTool(BaseTool):
    name = "delete_element"
    description = (
        "Delete an element from a slide. This operation can be undone."
    )

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based index of the slide containing the element.",
            },
            "element_id": {
                "type": "string",
                "description": "Unique ID of the element to delete.",
            },
        },
        "required": ["slide_index", "element_id"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        element_id: str,
    ) -> ToolResult:
        session = get_session()
        doc = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        try:
            slide = doc.get_slide(slide_index)
        except IndexError as exc:
            return ToolResult(success=False, error=str(exc))

        if element_id not in slide.elements:
            return ToolResult(
                success=False,
                error=f"Element '{element_id}' not found on slide {slide_index}.",
            )

        el = slide.elements[element_id]

        # Snapshot the full element before deletion.
        before = {"element": copy.deepcopy(el)}

        del slide.elements[element_id]

        after = {"deleted": True}

        doc.record_change(
            ChangeRecord(
                operation="delete_element",
                target_element=element_id,
                slide_index=slide_index,
                before_state=before,
                after_state=after,
            )
        )

        return ToolResult(
            success=True,
            data={
                "element_id": element_id,
                "slide_index": slide_index,
                "type": el.type,
                "deleted": True,
            },
        )
