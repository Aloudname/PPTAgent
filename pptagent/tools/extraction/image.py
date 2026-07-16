"""T07: extract all embedded images from the current document."""

from __future__ import annotations

from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class ExtractImagesTool(BaseTool):
    name = "extract_images"
    description = (
        "Extract all embedded images from the currently open PowerPoint document. "
        "Returns metadata about each image including position, size, content type, "
        "and image data (as base64-encoded bytes)."
    )

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based slide index to extract images from. Omit to extract from all slides.",
            },
            "include_data": {
                "type": "boolean",
                "description": "Whether to include base64-encoded image data in the result (default true).",
            },
        },
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int | None = None,
        include_data: bool = True,
    ) -> ToolResult:
        import base64

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
                if el.type != "image":
                    continue
                entry: dict = {
                    "element_id": el.id,
                    "slide_index": slide.index,
                    "position": {
                        "left_emu": el.position[0],
                        "top_emu": el.position[1],
                        "width_emu": el.position[2],
                        "height_emu": el.position[3],
                    },
                }
                if isinstance(el.content, dict):
                    entry["content_type"] = el.content.get("content_type", "unknown")
                    entry["filename"] = el.content.get("filename", "")
                    if include_data:
                        blob = el.content.get("blob")
                        if isinstance(blob, bytes):
                            entry["data_base64"] = base64.b64encode(blob).decode("ascii")
                            entry["size_bytes"] = len(blob)
                results.append(entry)

        return ToolResult(
            success=True,
            data={
                "image_elements": results,
                "count": len(results),
                "total_slides": len(doc.slides),
            },
        )
