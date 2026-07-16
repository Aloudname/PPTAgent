"""T01: recursive PPT file discovery."""

from __future__ import annotations

import re
from pathlib import Path

from pptagent.tools.base import BaseTool, ToolResult
from pptagent.utils.config import get_config


class FindPPTFilesTool(BaseTool):
    name = "find_ppt_files"
    description = (
        """
        Recursively search a directory for PowerPoint files,
        including `.ppt`, `.pptx`, `.potx`, `.ppsx`.
        Supports glob patterns and regex filtering.
        """
    )

    schema = {  # noqa: RUF012
        "type": "object",
        "properties": {
            "search_path": {
                "type": "string",
                "description": "Root directory to search.",
            },
            "pattern": {
                "type": "string",
                "description": "Optional glob or regex pattern to filter results.",
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to search subdirectories, default true.",
            },
            "max_depth": {
                "type": "integer",
                "description": "Maximum recursion depth. 0 = root only.",
            },
        },
        "required": ["search_path"],
    }

    async def execute(  # type: ignore[override]
        self,
        search_path: str,
        pattern: str = "*",
        recursive: bool = True,
        max_depth: int | None = None,
    ) -> ToolResult:
        config = get_config()
        extensions = tuple(config.file_system.supported_formats)
        if max_depth is None:
            max_depth = config.file_system.search_max_depth

        root = Path(search_path).expanduser().resolve()
        if not root.exists():
            return ToolResult(success=False, error=f"Path does not exist: {search_path}")
        if not root.is_dir():
            return ToolResult(success=False, error=f"Path is not a directory: {search_path}")

        matches: list[str] = []

        if recursive and max_depth > 0:
            iterator = root.rglob("*")
        else:
            iterator = root.glob("*")

        for entry in iterator:
            if not entry.is_file():
                continue
            if entry.suffix.lower() not in extensions:
                continue

            # Enforce max_depth
            if recursive and max_depth > 0:
                rel = entry.relative_to(root)
                depth = len(rel.parts) - 1
                if depth > max_depth:
                    continue

            # Apply pattern filter
            if pattern and pattern != "*":  # noqa: SIM102
                if not self._match_pattern(entry.name, pattern):
                    continue

            matches.append(str(entry))

        matches.sort()
        return ToolResult(
            success=True,
            data={
                "files": matches,
                "count": len(matches),
                "search_path": str(root),
            },
        )

    @staticmethod
    def _match_pattern(filename: str, pattern: str) -> bool:
        """Match *filename* against *pattern*.

        First tries as a regex via ``re.search``.
        Falls back to simple ``fnmatch``-style glob matching.
        """
        # Try regex
        if any(c in pattern for c in r".^$*+?{}[]\|()"):
            try:
                return re.search(pattern, filename) is not None
            except re.error:
                pass
        # Try glob
        return Path(filename).match(pattern)
