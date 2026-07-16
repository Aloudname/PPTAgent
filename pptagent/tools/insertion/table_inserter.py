"""T26: insert a table with the specified number of rows and columns."""

from __future__ import annotations

import uuid

from pptagent.core.change_manager import ChangeRecord
from pptagent.core.document import Element
from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class InsertTableTool(BaseTool):
    name = "insert_table"
    description = "Insert a table with the specified number of rows and columns."

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based index of the target slide.",
            },
            "rows": {
                "type": "integer",
                "description": "Number of rows in the table.",
            },
            "cols": {
                "type": "integer",
                "description": "Number of columns in the table.",
            },
            "left": {
                "type": "number",
                "description": "Left position of the table in EMU.",
            },
            "top": {
                "type": "number",
                "description": "Top position of the table in EMU.",
            },
            "width": {
                "type": "number",
                "description": "Width of the table in EMU.",
            },
            "height": {
                "type": "number",
                "description": "Height of the table in EMU.",
            },
            "data": {
                "type": "array",
                "description": "Optional 2D array (list of rows) of strings for cell content.",
                "items": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        },
        "required": ["slide_index", "rows", "cols", "left", "top", "width", "height"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        rows: int,
        cols: int,
        left: float,
        top: float,
        width: float,
        height: float,
        data: list[list[str]] | None = None,
    ) -> ToolResult:
        session = get_session()
        doc = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        # Validate slide_index
        try:
            slide = doc.get_slide(slide_index)
        except IndexError as exc:
            return ToolResult(success=False, error=str(exc))

        # Build the 2D content matrix
        content: list[list[str]] = []
        for r in range(rows):
            row_data: list[str] = []
            for c in range(cols):
                cell_value = ""
                if data is not None and r < len(data) and c < len(data[r]):
                    cell_value = str(data[r][c])
                row_data.append(cell_value)
            content.append(row_data)

        # Generate element_id
        element_id = f"table_{uuid.uuid4().hex[:8]}"

        # Create Element
        element = Element(
            id=element_id,
            type="table",
            position=(float(left), float(top), float(width), float(height)),
            content=content,
            z_order=len(slide.elements),
        )

        # Insert into slide
        slide.elements[element_id] = element

        # Record change for undo
        change = ChangeRecord(
            operation="insert_table",
            target_element=element_id,
            slide_index=slide_index,
            before_state=None,
            after_state=element_id,
        )
        # [BUG] RuffSIM105
        # Use `contextlib.suppress(RuntimeError)`,
        # instead of `try`-`except`-`pass`.
        try:
            doc.record_change(change)
        except RuntimeError:
            pass  # ChangeManager not attached; skip undo support

        return ToolResult(
            success=True,
            data={
                "element_id": element_id,
                "slide_index": slide_index,
                "position": {
                    "left_emu": left,
                    "top_emu": top,
                    "width_emu": width,
                    "height_emu": height,
                },
                "rows": rows,
                "cols": cols,
            },
        )
