"""T13: read detailed content of a specific element by ID."""

from __future__ import annotations

from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class ReadElementTool(BaseTool):
    name = "read_element"
    description = (
        "Read the detailed content of a specific element on a slide. "
        "Returns full content, formatting, position, and metadata for the requested element."
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
                "description": "Unique ID of the element to read (e.g. 'text_a3f2c1b0').",
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
            el = doc.get_element(slide_index, element_id)
        except (IndexError, KeyError) as exc:
            return ToolResult(success=False, error=str(exc))

        entry: dict = {
            "element_id": el.id,
            "type": el.type,
            "slide_index": slide_index,
            "z_order": el.z_order,
            "position": {
                "left_emu": el.position[0],
                "top_emu": el.position[1],
                "width_emu": el.position[2],
                "height_emu": el.position[3],
            },
            "content": el.content if isinstance(el.content, (str, int, float, bool, type(None), list, dict)) else str(el.content),
            "metadata": el.metadata,
        }

        if el.format is not None:
            entry["format"] = {
                "font_name": el.format.font_name,
                "font_size": el.format.font_size,
                "font_color": el.format.font_color,
                "bold": el.format.bold,
                "italic": el.format.italic,
                "underline": el.format.underline,
                "strikethrough": el.format.strikethrough,
                "superscript": el.format.superscript,
                "subscript": el.format.subscript,
                "highlight": el.format.highlight,
                "alignment": el.format.alignment,
                "line_spacing": el.format.line_spacing,
                "paragraph_spacing": el.format.paragraph_spacing,
            }

        return ToolResult(success=True, data=entry)
