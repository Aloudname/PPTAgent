"""T10: extract flowcharts, SmartArt, and mind-map diagrams."""

from __future__ import annotations

from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class ExtractDiagramsTool(BaseTool):
    name = "extract_diagrams"
    description = (
        "Extract all diagrams (SmartArt, flowcharts, mind maps) from the currently "
        "open PowerPoint document. Returns structural descriptions and metadata."
    )

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index to extract diagrams from. Omit to extract from all slides.",
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
                if el.type != "diagram":
                    continue
                entry = {
                    "element_id": el.id,
                    "slide_index": slide.index,
                    "position": {
                        "left_emu": el.position[0],
                        "top_emu": el.position[1],
                        "width_emu": el.position[2],
                        "height_emu": el.position[3],
                    },
                    "diagram_type": el.metadata.get("diagram_type", "unknown"),
                    "description": el.content if isinstance(el.content, dict) else {"name": str(el.content)},
                }
                results.append(entry)

        return ToolResult(
            success=True,
            data={
                "diagram_elements": results,
                "count": len(results),
                "total_slides": len(doc.slides),
            },
        )
