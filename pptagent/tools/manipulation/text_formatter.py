"""T16-T18: modify text formatting."""

from __future__ import annotations

import copy
from typing import Any

from pptagent.core.change_manager import ChangeRecord
from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult

_TEXT_FORMAT_FIELDS = [
    "font_name",
    "font_size",
    "font_color",
    "bold",
    "italic",
    "underline",
    "strikethrough",
    "superscript",
    "subscript",
    "highlight",
    "alignment",
    "line_spacing",
    "paragraph_spacing",
]


class FormatTextTool(BaseTool):
    name = "format_text"
    description = (
        "Modify text formatting for a specific text element. "
        "Only the properties you specify will be changed; all others "
        "retain their current values."
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
                "description": "Unique ID of the text element to format.",
            },
            "font_name": {
                "type": "string",
                "description": "Font family name (e.g. 'Calibri', 'Arial').",
            },
            "font_size": {
                "type": "number",
                "description": "Font size in points (pt).",
            },
            "font_color": {
                "type": "string",
                "description": "Font colour as a '#RRGGBB' hex string.",
            },
            "bold": {
                "type": "boolean",
                "description": "Enable or disable bold.",
            },
            "italic": {
                "type": "boolean",
                "description": "Enable or disable italic.",
            },
            "underline": {
                "type": "boolean",
                "description": "Enable or disable underline.",
            },
            "strikethrough": {
                "type": "boolean",
                "description": "Enable or disable strikethrough.",
            },
            "superscript": {
                "type": "boolean",
                "description": "Enable or disable superscript.",
            },
            "subscript": {
                "type": "boolean",
                "description": "Enable or disable subscript.",
            },
            "highlight": {
                "type": "string",
                "description": "Highlight colour as a '#RRGGBB' hex string, or null to remove.",
            },
            "alignment": {
                "type": "string",
                "description": "Text alignment: 'left', 'center', 'right', or 'justify'.",
            },
            "line_spacing": {
                "type": "number",
                "description": "Line spacing multiplier (1.0 = single, 1.5 = 1.5 lines, 2.0 = double).",
            },
            "paragraph_spacing": {
                "type": "number",
                "description": "Space before and after paragraphs in points (pt).",
            },
        },
        "required": ["slide_index", "element_id"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        element_id: str,
        font_name: str | None = None,
        font_size: float | None = None,
        font_color: str | None = None,
        bold: bool | None = None,
        italic: bool | None = None,
        underline: bool | None = None,
        strikethrough: bool | None = None,
        superscript: bool | None = None,
        subscript: bool | None = None,
        highlight: str | None = None,
        alignment: str | None = None,
        line_spacing: float | None = None,
        paragraph_spacing: float | None = None,
    ) -> ToolResult:
        session = get_session()
        doc = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        try:
            el = doc.get_element(slide_index, element_id)
        except (IndexError, KeyError) as exc:
            return ToolResult(success=False, error=str(exc))

        if el.type != "text":
            return ToolResult(
                success=False,
                error=f"Element '{element_id}' is type '{el.type}', not 'text'.",
            )

        if el.format is None:
            return ToolResult(
                success=False,
                error=f"Element '{element_id}' has no TextFormat to modify.",
            )

        # Collect only the parameters that were explicitly provided.
        supplied: dict[str, Any] = {}
        for field in _TEXT_FORMAT_FIELDS:
            val = locals()[field]
            if val is not None:
                supplied[field] = val

        if not supplied:
            return ToolResult(
                success=False,
                error="No formatting properties were provided to change.",
            )

        before = {"format": copy.deepcopy(el.format)}

        for field, val in supplied.items():
            setattr(el.format, field, val)

        after = {"format": copy.deepcopy(el.format)}

        doc.record_change(
            ChangeRecord(
                operation="format_text",
                target_element=element_id,
                slide_index=slide_index,
                before_state=before,
                after_state=after,
            )
        )

        return ToolResult(
            success=True,
            data={
                "element_id": element_id,
                "slide_index": slide_index,
                "changed_properties": sorted(supplied.keys()),
                "format": {
                    f: getattr(el.format, f) for f in _TEXT_FORMAT_FIELDS
                },
            },
        )


class SetAlignmentTool(BaseTool):
    name = "set_alignment"
    description = (
        "Set the text alignment of a text element. "
        "Supported values: 'left', 'center', 'right', 'justify'."
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
                "description": "Unique ID of the text element.",
            },
            "alignment": {
                "type": "string",
                "description": "Text alignment: 'left', 'center', 'right', or 'justify'.",
                "enum": ["left", "center", "right", "justify"],
            },
        },
        "required": ["slide_index", "element_id", "alignment"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        element_id: str,
        alignment: str,
    ) -> ToolResult:
        session = get_session()
        doc = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        try:
            el = doc.get_element(slide_index, element_id)
        except (IndexError, KeyError) as exc:
            return ToolResult(success=False, error=str(exc))

        if el.type != "text":
            return ToolResult(
                success=False,
                error=f"Element '{element_id}' is type '{el.type}', not 'text'.",
            )

        if el.format is None:
            return ToolResult(
                success=False,
                error=f"Element '{element_id}' has no TextFormat to modify.",
            )

        valid_alignments = {"left", "center", "right", "justify"}
        if alignment not in valid_alignments:
            return ToolResult(
                success=False,
                error=f"Invalid alignment '{alignment}'. Must be one of {sorted(valid_alignments)}.",
            )

        before = {"format": copy.deepcopy(el.format)}
        old_alignment = el.format.alignment
        el.format.alignment = alignment
        after = {"format": copy.deepcopy(el.format)}

        doc.record_change(
            ChangeRecord(
                operation="set_alignment",
                target_element=element_id,
                slide_index=slide_index,
                before_state=before,
                after_state=after,
            )
        )

        return ToolResult(
            success=True,
            data={
                "element_id": element_id,
                "slide_index": slide_index,
                "alignment": alignment,
                "previous_alignment": old_alignment,
                "format": {
                    f: getattr(el.format, f) for f in _TEXT_FORMAT_FIELDS
                },
            },
        )


class SetTextEffectTool(BaseTool):
    name = "set_text_effect"
    description = (
        "Toggle text effect flags (bold, italic, underline, etc.) on a text element. "
        "Only the flags you specify will be changed."
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
                "description": "Unique ID of the text element.",
            },
            "bold": {
                "type": "boolean",
                "description": "Enable or disable bold.",
            },
            "italic": {
                "type": "boolean",
                "description": "Enable or disable italic.",
            },
            "underline": {
                "type": "boolean",
                "description": "Enable or disable underline.",
            },
            "strikethrough": {
                "type": "boolean",
                "description": "Enable or disable strikethrough.",
            },
            "superscript": {
                "type": "boolean",
                "description": "Enable or disable superscript.",
            },
            "subscript": {
                "type": "boolean",
                "description": "Enable or disable subscript.",
            },
        },
        "required": ["slide_index", "element_id"],
    }

    async def execute(  # type: ignore[override]
        self,
        slide_index: int,
        element_id: str,
        bold: bool | None = None,
        italic: bool | None = None,
        underline: bool | None = None,
        strikethrough: bool | None = None,
        superscript: bool | None = None,
        subscript: bool | None = None,
    ) -> ToolResult:
        session = get_session()
        doc = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        try:
            el = doc.get_element(slide_index, element_id)
        except (IndexError, KeyError) as exc:
            return ToolResult(success=False, error=str(exc))

        if el.type != "text":
            return ToolResult(
                success=False,
                error=f"Element '{element_id}' is type '{el.type}', not 'text'.",
            )

        if el.format is None:
            return ToolResult(
                success=False,
                error=f"Element '{element_id}' has no TextFormat to modify.",
            )

        effect_fields = [
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "superscript",
            "subscript",
        ]
        supplied: dict[str, Any] = {}
        for field in effect_fields:
            val = locals()[field]
            if val is not None:
                supplied[field] = val

        if not supplied:
            return ToolResult(
                success=False,
                error="No effect flags were provided to change.",
            )

        before = {"format": copy.deepcopy(el.format)}

        for field, val in supplied.items():
            setattr(el.format, field, val)

        after = {"format": copy.deepcopy(el.format)}

        doc.record_change(
            ChangeRecord(
                operation="set_text_effect",
                target_element=element_id,
                slide_index=slide_index,
                before_state=before,
                after_state=after,
            )
        )

        return ToolResult(
            success=True,
            data={
                "element_id": element_id,
                "slide_index": slide_index,
                "changed_effects": sorted(supplied.keys()),
                "format": {
                    f: getattr(el.format, f) for f in effect_fields
                },
            },
        )
