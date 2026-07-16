"""T25: insert a new text box with specified content and formatting."""

from __future__ import annotations

import uuid

from pptagent.core.change_manager import ChangeRecord
from pptagent.core.document import Element, TextFormat
from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class InsertTextBoxTool(BaseTool):
    name = "insert_text_box"
    description = "Insert a new text box with specified content and formatting."

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based index of the target slide.",
            },
            "text": {
                "type": "string",
                "description": "The text content to insert.",
            },
            "left": {
                "type": "number",
                "description": "Left position of the text box in EMU.",
            },
            "top": {
                "type": "number",
                "description": "Top position of the text box in EMU.",
            },
            "width": {
                "type": "number",
                "description": "Width of the text box in EMU.",
            },
            "height": {
                "type": "number",
                "description": "Height of the text box in EMU.",
            },
            "font_name": {
                "type": "string",
                "description": "Font name (default 'Calibri').",
            },
            "font_size": {
                "type": "number",
                "description": "Font size in points (default 12).",
            },
            "font_color": {
                "type": "string",
                "description": "Font color as HEX string (default '#000000').",
            },
            "bold": {
                "type": "boolean",
                "description": "Whether the text is bold (default false).",
            },
            "italic": {
                "type": "boolean",
                "description": "Whether the text is italic (default false).",
            },
            "alignment": {
                "type": "string",
                "description": "Text alignment: 'left', 'center', 'right', or 'justify' (default 'left').",
            },
        },
        "required": ["slide_index", "text", "left", "top", "width", "height"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        text: str,
        left: float,
        top: float,
        width: float,
        height: float,
        font_name: str = "Calibri",
        font_size: float = 12.0,
        font_color: str = "#000000",
        bold: bool = False,
        italic: bool = False,
        alignment: str = "left",
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

        # Build TextFormat
        text_format = TextFormat(
            font_name=font_name,
            font_size=font_size,
            font_color=font_color,
            bold=bold,
            italic=italic,
            alignment=alignment,
        )

        # Generate element_id
        element_id = f"text_{uuid.uuid4().hex[:8]}"

        # Create Element
        element = Element(
            id=element_id,
            type="text",
            position=(float(left), float(top), float(width), float(height)),
            content=text,
            format=text_format,
            z_order=len(slide.elements),
        )

        # Insert into slide
        slide.elements[element_id] = element

        # Record change for undo
        change = ChangeRecord(
            operation="insert_text_box",
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
                "format": {
                    "font_name": font_name,
                    "font_size": font_size,
                    "font_color": font_color,
                    "bold": bold,
                    "italic": italic,
                    "alignment": alignment,
                },
            },
        )
