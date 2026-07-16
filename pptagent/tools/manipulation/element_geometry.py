"""T14-T15: modify element geometry on the current document."""

from __future__ import annotations

import copy

from pptagent.core.change_manager import ChangeRecord
from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class SetPositionTool(BaseTool):
    name = "set_position"
    description = (
        "Move an element to a new position on the slide. "
        "Coordinates are in EMU (1 inch = 914400 EMU)."
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
                "description": "Unique ID of the element to move.",
            },
            "left": {
                "type": "number",
                "description": "New left offset in EMU.",
            },
            "top": {
                "type": "number",
                "description": "New top offset in EMU.",
            },
        },
        "required": ["slide_index", "element_id", "left", "top"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        element_id: str,
        left: float,
        top: float,
    ) -> ToolResult:
        session = get_session()
        doc = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        try:
            el = doc.get_element(slide_index, element_id)
        except (IndexError, KeyError) as exc:
            return ToolResult(success=False, error=str(exc))

        old_pos = el.position
        before = {"position": copy.deepcopy(old_pos)}
        new_pos = (left, top, old_pos[2], old_pos[3])
        el.position = new_pos
        after = {"position": copy.deepcopy(new_pos)}

        doc.record_change(
            ChangeRecord(
                operation="set_position",
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
                "position": {
                    "left_emu": new_pos[0],
                    "top_emu": new_pos[1],
                    "width_emu": new_pos[2],
                    "height_emu": new_pos[3],
                },
            },
        )


class SetSizeTool(BaseTool):
    name = "set_size"
    description = (
        "Resize an element on the slide. Dimensions are in EMU "
        "(1 inch = 914400 EMU)."
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
                "description": "Unique ID of the element to resize.",
            },
            "width": {
                "type": "number",
                "description": "New width in EMU.",
            },
            "height": {
                "type": "number",
                "description": "New height in EMU.",
            },
            "lock_aspect_ratio": {
                "type": "boolean",
                "description": "If true and only one dimension is provided, "
                "the other dimension is computed to maintain the aspect ratio (default false).",
            },
        },
        "required": ["slide_index", "element_id"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        element_id: str,
        width: float | None = None,
        height: float | None = None,
        lock_aspect_ratio: bool = False,
    ) -> ToolResult:
        session = get_session()
        doc = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        if width is None and height is None:
            return ToolResult(
                success=False,
                error="At least one of 'width' or 'height' must be provided.",
            )

        try:
            el = doc.get_element(slide_index, element_id)
        except (IndexError, KeyError) as exc:
            return ToolResult(success=False, error=str(exc))

        old_pos = el.position
        before = {"position": copy.deepcopy(old_pos)}

        new_width = width if width is not None else old_pos[2]
        new_height = height if height is not None else old_pos[3]

        if lock_aspect_ratio:
            if width is not None and height is None:
                # Only width changed — compute height from aspect ratio
                if old_pos[2] != 0:
                    new_height = (new_width / old_pos[2]) * old_pos[3]
            elif height is not None and width is None:  # noqa: SIM102
                # Only height changed — compute width from aspect ratio
                if old_pos[3] != 0:
                    new_width = (new_height / old_pos[3]) * old_pos[2]

        new_pos = (old_pos[0], old_pos[1], new_width, new_height)
        el.position = new_pos
        after = {"position": copy.deepcopy(new_pos)}

        doc.record_change(
            ChangeRecord(
                operation="set_size",
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
                "position": {
                    "left_emu": new_pos[0],
                    "top_emu": new_pos[1],
                    "width_emu": new_pos[2],
                    "height_emu": new_pos[3],
                },
            },
        )
