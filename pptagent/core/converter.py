"""Legacy .ppt -> .pptx converter using LibreOffice headless."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from pptagent.core.exceptions import ConversionError
from pptagent.utils.config import get_config


def find_libreoffice() -> Optional[str]:
    """Locate the LibreOffice / soffice binary.

    ## Search order
    1. ``LIBREOFFICE_PATH`` env var.
    2. ``shutil.which("libreoffice")`` for Linux.
    3. ``shutil.which("soffice")`` for macOS.
    4. ``~/.local/bin/libreoffice*`` for AppImage / manual extract.

    ## Returns
    ``str`` or ``None``
        Absolute path to the binary, or ``None`` if not found.
    """
    # env var
    env_path = os.environ.get("LIBREOFFICE_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    # libreoffice on PATH
    lo = shutil.which("libreoffice")
    if lo:
        return lo

    # soffice on PATH
    so = shutil.which("soffice")
    if so:
        return so

    # ~/ .local/bin
    local_bin = Path.home() / ".local" / "bin"
    if local_bin.is_dir():
        for candidate in sorted(local_bin.glob("libreoffice*")):
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return str(candidate)

    return None


def convert_ppt_to_pptx(source: str | Path) -> Path:
    """Convert ``.ppt`` file to ``.pptx`` via LibreOffice headless.

    ## Parameters
    ``source``: ``str`` or ``Path``,
        Path to the ``.ppt`` file.

    ## Returns
    ``Path``:
        ``Path`` to the newly created ``.pptx`` file.

    ## Raises
    ``ConversionError`` if:
    - LibreOffice is not found
    - input is not ``.ppt``,
    - conversion process fails / times out.
    """
    source = Path(source).resolve()

    if source.suffix.lower() != ".ppt":
        raise ConversionError(
            f"Expected a .ppt file, got '{source.suffix}': {source}"
        )

    libre_bin = find_libreoffice()
    if libre_bin is None:
        raise ConversionError(
            "LibreOffice not found. Install it via your system package manager, "
            "or download an AppImage to ~/.local/bin/."
        )

    config = get_config()
    timeout = config.file_system.libreoffice_timeout

    with tempfile.TemporaryDirectory(prefix="pptagent_lo_") as tmp_dir:
        cmd = [
            libre_bin,
            "--headless",
            "--norestore",
            "--convert-to", "pptx",
            "--outdir", tmp_dir,
            str(source),
        ]

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True,
            )
        except subprocess.TimeoutExpired as exc:
            raise ConversionError(
                f"LibreOffice conversion timed out after {timeout} s: {source}"
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise ConversionError(
                f"LibreOffice conversion failed (exit {exc.returncode}): "
                f"{exc.stderr.strip()}"
            ) from exc

        # LibreOffice names the output <stem>.pptx in --outdir
        output = Path(tmp_dir) / f"{source.stem}.pptx"
        if not output.exists():
            raise ConversionError(
                f"LibreOffice did not produce expected output file: {output}"
            )

        # Copy to a persistent location next to the source file
        dest = source.with_suffix(".pptx")
        shutil.copy2(output, dest)

    return dest
