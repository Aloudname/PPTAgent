"""T06: extract all text elements with formatting from the current document."""

from __future__ import annotations

from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class ExtractTextTool(BaseTool):
    name = "extract_text"
    description = (
        "Extract all text elements from the currently open PowerPoint document, "
        "including their content and full formatting details (font, size, color, style)."
    )

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index to extract text from. Omit to extract from all slides.",
            },
        },
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int | None = None,
    ) -> ToolResult:
        session = get_session()
        doc = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        slides = doc.slides
        if slide_index is not None:
            if slide_index < 0 or slide_index >= len(doc.slides):
                return ToolResult(
                    success=False,
                    error=f"Slide index {slide_index} out of range (0-{len(doc.slides) - 1}).",
                )
            slides = [doc.get_slide(slide_index)]

        results: list[dict] = []
        for slide in slides:
            for el in slide.elements.values():
                if el.type != "text":
                    continue
                entry: dict = {
                    "element_id": el.id,
                    "slide_index": slide.index,
                    "content": el.content,
                    "position": {
                        "left_emu": el.position[0],
                        "top_emu": el.position[1],
                        "width_emu": el.position[2],
                        "height_emu": el.position[3],
                    },
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
                results.append(entry)

        return ToolResult(
            success=True,
            data={
                "text_elements": results,
                "count": len(results),
                "total_slides": len(doc.slides),
            },
        )
