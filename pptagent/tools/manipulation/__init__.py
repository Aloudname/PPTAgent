"""T14-T19: manipulation tool exports."""

from pptagent.tools.manipulation.element_delete import DeleteElementTool
from pptagent.tools.manipulation.element_geometry import SetPositionTool, SetSizeTool
from pptagent.tools.manipulation.text_formatter import (
    FormatTextTool,
    SetAlignmentTool,
    SetTextEffectTool,
)

__all__ = [
    "DeleteElementTool",
    "FormatTextTool",
    "SetAlignmentTool",
    "SetPositionTool",
    "SetSizeTool",
    "SetTextEffectTool",
]
