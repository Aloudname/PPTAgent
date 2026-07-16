"""T30: insert a chart in bar, line, pie, scatter or whatever formats."""

from __future__ import annotations

import uuid

from pptagent.core.change_manager import ChangeRecord
from pptagent.core.document import Element
from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


class InsertChartTool(BaseTool):
    name = "insert_chart"
    description = "Insert a chart (bar, line, pie, or scatter)."

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "slide_index": {
                "type": "integer",
                "description": "0-based index of the target slide.",
            },
            "chart_type": {
                "type": "string",
                "enum": ["bar", "line", "pie", "scatter"],
                "description": "Type of chart to insert.",
            },
            "categories": {
                "type": "array",
                "description": "Category labels for the chart (e.g. ['Q1', 'Q2', 'Q3', 'Q4']).",
                "items": {"type": "string"},
            },
            "series_data": {
                "type": "array",
                "description": "Array of series objects, each with a 'name' and 'values' array.",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "values": {
                            "type": "array",
                            "items": {"type": "number"},
                        },
                    },
                    "required": ["name", "values"],
                },
            },
            "left": {
                "type": "number",
                "description": "Left position of the chart in EMU.",
            },
            "top": {
                "type": "number",
                "description": "Top position of the chart in EMU.",
            },
            "width": {
                "type": "number",
                "description": "Width of the chart in EMU.",
            },
            "height": {
                "type": "number",
                "description": "Height of the chart in EMU.",
            },
            "title": {
                "type": "string",
                "description": "Optional chart title.",
            },
        },
        "required": [
            "slide_index",
            "chart_type",
            "categories",
            "series_data",
            "left",
            "top",
            "width",
            "height",
        ],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        chart_type: str,
        categories: list[str],
        series_data: list[dict],
        left: float,
        top: float,
        width: float,
        height: float,
        title: str | None = None,
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

        # Validate chart_type
        valid_types = {"bar", "line", "pie", "scatter"}
        if chart_type not in valid_types:
            return ToolResult(
                success=False,
                error=f"Invalid chart_type '{chart_type}'. Must be one of: {', '.join(sorted(valid_types))}.",
            )

        # Build chart content dict
        chart_content: dict = {
            "chart_type": chart_type,
            "categories": categories,
            "series": series_data,
        }
        if title is not None:
            chart_content["title"] = title

        # Generate element_id
        element_id = f"chart_{uuid.uuid4().hex[:8]}"

        # Create Element
        element = Element(
            id=element_id,
            type="chart",
            position=(float(left), float(top), float(width), float(height)),
            content=chart_content,
            z_order=len(slide.elements),
        )

        # Insert into slide
        slide.elements[element_id] = element

        # Record change for undo
        change = ChangeRecord(
            operation="insert_chart",
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
                "chart_type": chart_type,
                "position": {
                    "left_emu": left,
                    "top_emu": top,
                    "width_emu": width,
                    "height_emu": height,
                },
                "categories_count": len(categories),
                "series_count": len(series_data),
            },
        )
