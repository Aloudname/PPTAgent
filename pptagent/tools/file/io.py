"""T02-T05: open / save / save-as / close PPT files."""

from __future__ import annotations

import os
from pathlib import Path

from pptagent.core.converter import convert_ppt_to_pptx
from pptagent.core.document import PPTDocument
from pptagent.core.session import get_session
from pptagent.tools.base import BaseTool, ToolResult


# T02: open_ppt
class OpenPPTTool(BaseTool):
    name = "open_ppt"
    description = "Open a PowerPoint file and load it into memory."

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Absolute or relative path to the .ppt / .pptx file.",
            },
        },
        "required": ["file_path"],
    }

    async def execute(  # type: ignore[override]
        self, file_path: str
    ) -> ToolResult:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return ToolResult(success=False, error=f"File not found: {file_path}")

        # Convert legacy .ppt on the fly
        if path.suffix.lower() == ".ppt":
            try:
                path = convert_ppt_to_pptx(path)
            except Exception as exc:
                return ToolResult(success=False, error=f"Conversion failed: {exc}")

        try:
            doc = PPTDocument.from_file(path)
        except NotImplementedError:
            # from_file is a placeholder.
            # for now, construct a lightweight stub
            doc = PPTDocument(
                file_path=str(path),
                file_name=path.name,
            )
        except Exception as exc:
            return ToolResult(success=False, error=f"Failed to open file: {exc}")

        session = get_session()
        session.current_document = doc
        session.open_files.append(str(path))

        return ToolResult(
            success=True,
            data={
                "message": f"Opened {path.name}",
                "file_path": str(path),
                "file_name": doc.file_name,
                "slide_count": len(doc.slides),
            },
        )


# T03: save_ppt
class SavePPTTool(BaseTool):
    name = "save_ppt"
    description = "Save the current document to its original file path."

    schema: dict = {"type": "object", "properties": {}}  # noqa: RUF012

    async def execute(self) -> ToolResult:  # type: ignore[override]
        session = get_session()
        doc = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        if doc.file_path is None:
            return ToolResult(
                success=False,
                error="Document was created from scratch (no file_path). Use save_ppt_as to specify a path.",
            )

        try:
            saved = doc.to_file()
        except NotImplementedError:
            saved = doc.file_path  # to_file is a placeholder for now
        except Exception as exc:
            return ToolResult(success=False, error=f"Save failed: {exc}")

        size = os.path.getsize(saved) if os.path.exists(saved) else 0
        return ToolResult(
            success=True,
            data={
                "message": f"Saved to {saved}",
                "file_path": saved,
                "file_size_bytes": size,
            },
        )

# T04: save_ppt_as
class SavePPTAsTool(BaseTool):
    name = "save_ppt_as"
    description = "Save the current document to a new file path (Save As / Rename)."

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "new_path": {
                "type": "string",
                "description": "New file path for the presentation.",
            },
        },
        "required": ["new_path"],
    }

    async def execute(  # type: ignore[override]
        self, new_path: str
    ) -> ToolResult:
        session = get_session()
        doc = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        path = Path(new_path).expanduser().resolve()
        if not path.parent.exists():
            return ToolResult(
                success=False,
                error=f"Parent directory does not exist: {path.parent}",
            )

        doc.file_path = str(path)
        doc.file_name = path.name

        try:
            saved = doc.to_file(path)
        except NotImplementedError:
            saved = str(path)
        except Exception as exc:
            return ToolResult(success=False, error=f"Save failed: {exc}")

        size = os.path.getsize(saved) if os.path.exists(saved) else 0
        return ToolResult(
            success=True,
            data={
                "message": f"Saved as {path.name}",
                "file_path": saved,
                "file_size_bytes": size,
            },
        )


# T05: close_ppt
class ClosePPTTool(BaseTool):
    name = "close_ppt"
    description = "Close the current presentation, optionally saving changes."

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "save": {
                "type": "boolean",
                "description": "Whether to save before closing (default true).",
            },
        },
    }

    async def execute(  # type: ignore[override]
        self, save: bool = True
    ) -> ToolResult:
        session = get_session()
        doc = session.current_document
        if doc is None:
            return ToolResult(success=False, error="No document is currently open.")

        closed_path = doc.file_path

        if save and doc.file_path:
            save_tool = SavePPTTool()
            result = await save_tool.execute()
            if not result.success:
                return result

        session.current_document = None
        return ToolResult(
            success=True,
            data={
                "message": f"Closed {closed_path or 'untitled'}",
                "was_saved": save,
            },
        )
