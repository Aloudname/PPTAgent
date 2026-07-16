"""Structured logging system

Provides both JSON structured and human-readable log formats.
Automatically injects session_id and task_id via ContextVar.

Usage:
    from pptagent.utils.logger import get_logger, setup_logging

    logger = get_logger(__name__)
    logger.info("operation_completed", extra={"extra_fields": {"duration_ms": 42}})
"""

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---- Context variables (safe across async tasks)----
session_id_ctx: ContextVar[str] = ContextVar("session_id", default="unknown")
task_id_ctx: ContextVar[str] = ContextVar("task_id", default="unknown")


class StructuredFormatter(logging.Formatter):
    """Structured JSON log formatter"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "session_id": session_id_ctx.get(),
            "task_id": task_id_ctx.get(),
        }

        # Merge custom fields from extra (dynamic attribute not natively on LogRecord)
        extra = getattr(record, "extra_fields", None)
        if extra:
            log_entry.update(extra)

        # Add exception information
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class PlainFormatter(logging.Formatter):
    """Human-readable formatter (for development)"""

    FORMAT = (
        "%(asctime)s | %(levelname)-7s | %(name)s:%(funcName)s:%(lineno)d | "
        "%(message)s"
    )

    def __init__(self):
        super().__init__(self.FORMAT, datefmt="%Y-%m-%d %H:%M:%S")


def setup_logging(
    name: str = "pptagent",
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    structured: bool = True,
) -> logging.Logger:
    """Initialize the logging system

    Args:
        name: Logger name
        level: Log level; defaults to PPTAGENT_LOG_LEVEL env var, falls back to INFO
        log_file: Log file path; if None, only output to console
        structured: Whether to use structured JSON format

    Returns:
        Configured Logger instance
    """
    if level is None:
        import os
        level = os.getenv("PPTAGENT_LOG_LEVEL", "INFO")

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    # Select formatter
    formatter = StructuredFormatter() if structured else PlainFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Set log level for third-party libraries
    for lib in ["urllib3", "httpx", "openai", "chromadb", "PIL", "matplotlib"]:
        logging.getLogger(lib).setLevel(logging.WARNING)

    return logger


def get_logger(name: str = "pptagent") -> logging.Logger:
    """Get a logger instance (reuses existing configuration)"""
    return logging.getLogger(name)


# ---- Convenience functions ----

def set_session_id(sid: Optional[str] = None) -> str:
    """Set the current session ID"""
    if sid is None:
        sid = uuid.uuid4().hex[:12]
    session_id_ctx.set(sid)
    return sid


def set_task_id(tid: Optional[str] = None) -> str:
    """Set the current task ID"""
    if tid is None:
        tid = uuid.uuid4().hex[:8]
    task_id_ctx.set(tid)
    return tid
