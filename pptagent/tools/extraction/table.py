"""T08: extract all tables from the current document."""

from __future__ import annotations

from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class ExtractTablesTool(BaseTool):
    name = "extract_tables"
    description = (
        "Extract all tables from the currently open PowerPoint document. "
        "Returns table data as structured 2D arrays (list of rows)."
    )

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index to extract tables from. Omit to extract from all slides.",
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
                if el.type != "table":
                    continue
                rows_data: list[list[str]] | None = None
                row_count = 0
                col_count = 0
                if isinstance(el.content, list):
                    rows_data = el.content
                    row_count = len(rows_data)
                    col_count = max((len(r) for r in rows_data), default=0)
                entry = {
                    "element_id": el.id,
                    "slide_index": slide.index,
                    "position": {
                        "left_emu": el.position[0],
                        "top_emu": el.position[1],
                        "width_emu": el.position[2],
                        "height_emu": el.position[3],
                    },
                    "rows": row_count,
                    "cols": col_count,
                    "data": rows_data,
                }
                results.append(entry)

        return ToolResult(
            success=True,
            data={
                "table_elements": results,
                "count": len(results),
                "total_slides": len(doc.slides),
            },
        )
