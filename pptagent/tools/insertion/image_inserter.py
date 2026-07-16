"""T21: insert an image file into a slide at the specified position."""

from __future__ import annotations

import uuid
from pathlib import Path

from pptagent.core.change_manager import ChangeRecord
from pptagent.core.document import Element
from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class InsertImageTool(BaseTool):
    name = "insert_image"
    description = "Insert an image file into a slide at the specified position."

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based index of the target slide.",
            },
            "image_path": {
                "type": "string",
                "description": "Absolute or relative path to the image file.",
            },
            "left": {
                "type": "number",
                "description": "Left position of the image in EMU.",
            },
            "top": {
                "type": "number",
                "description": "Top position of the image in EMU.",
            },
            "width": {
                "type": "number",
                "description": "Width of the image in EMU. Auto-detected from the image if omitted.",
            },
            "height": {
                "type": "number",
                "description": "Height of the image in EMU. Auto-detected from the image if omitted.",
            },
            "alt_text": {
                "type": "string",
                "description": "Alternative text for accessibility (default empty).",
            },
        },
        "required": ["slide_index", "image_path", "left", "top"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        image_path: str,
        left: float,
        top: float,
        width: float | None = None,
        height: float | None = None,
        alt_text: str = "",
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

        # Resolve and validate image_path
        resolved_path = Path(image_path).resolve()
        if not resolved_path.exists():
            return ToolResult(
                success=False,
                error=f"Image file not found: {resolved_path}",
            )
        if not resolved_path.is_file():
            return ToolResult(
                success=False,
                error=f"Path is not a file: {resolved_path}",
            )

        # Read file bytes
        try:
            blob = resolved_path.read_bytes()
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"Failed to read image file: {exc}",
            )

        # Determine content_type from extension
        ext = resolved_path.suffix.lower()
        content_type_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
        }
        content_type = content_type_map.get(ext, "image/png")
        ext_clean = ext.lstrip(".") if ext else "png"

        # Auto-detect dimensions if not provided
        if width is None or height is None:
            try:
                from PIL import Image as PILImage

                with PILImage.open(resolved_path) as img:
                    img_width, img_height = img.size
                if width is None:
                    width = img_width / 96.0 * 914400
                if height is None:
                    height = img_height / 96.0 * 914400
            except ImportError:
                if width is None:
                    width = 914400.0  # default ~1 inch
                if height is None:
                    height = 914400.0  # default ~1 inch

        # Generate element_id and filename
        element_id = f"image_{uuid.uuid4().hex[:8]}"
        filename = f"image_{uuid.uuid4().hex[:8]}.{ext_clean}"

        # Build Element content
        content = {
            "blob": blob,
            "content_type": content_type,
            "filename": filename,
        }

        # Create Element
        element = Element(
            id=element_id,
            type="image",
            position=(float(left), float(top), float(width), float(height)),
            content=content,
            z_order=len(slide.elements),
        )

        # Add alt_text to metadata
        if alt_text:
            element.metadata["alt_text"] = alt_text

        # Insert into slide
        slide.elements[element_id] = element

        # Record change for undo
        change = ChangeRecord(
            operation="insert_image",
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
                "content_type": content_type,
                "filename": filename,
            },
        )
