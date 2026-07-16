"""T09: extract mathematical formulas from the current document."""

from __future__ import annotations

from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class ExtractFormulasTool(BaseTool):
    name = "extract_formulas"
    description = (
        "Extract all mathematical formulas from the currently open PowerPoint document. "
        "Supports OMML (Office Math Markup Language) and MathType OLE objects. "
        "Formulas are returned as LaTeX strings when possible, or as raw MathML."
    )

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index to extract formulas from. Omit to extract from all slides.",
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
                if el.type != "formula":
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
                    "latex": el.content if isinstance(el.content, str) else str(el.content),
                    "raw_mathml": el.metadata.get("mathml", ""),
                    "formula_type": el.metadata.get("formula_type", "unknown"),
                }
                results.append(entry)

        return ToolResult(
            success=True,
            data={
                "formula_elements": results,
                "count": len(results),
                "total_slides": len(doc.slides),
            },
        )
