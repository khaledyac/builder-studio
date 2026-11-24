"""Structured JSON logging: one line per event, carrying the request's IDs when they are known.

Cloud Logging reads `severity` and `message` from each line. `log_context` sets `user_id`,
`app_id` and `session_id` for everything logged inside it, including nested calls. A single
call can also pass them with `extra=`, which wins over the context.
"""

import json
import logging
import sys
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Literal, TextIO

type LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

ID_FIELDS = ("user_id", "app_id", "session_id")

_ids: ContextVar[Mapping[str, str]] = ContextVar("studio_log_ids", default=MappingProxyType({}))


@contextmanager
def log_context(
    *, user_id: str | None = None, app_id: str | None = None, session_id: str | None = None
) -> Generator[None]:
    """Add the given IDs to every event logged inside the block. Unset IDs are left out."""
    given = {"user_id": user_id, "app_id": app_id, "session_id": session_id}
    added = {name: value for name, value in given.items() if value is not None}
    token = _ids.set({**_ids.get(), **added})
    try:
        yield
    finally:
        _ids.reset(token)


def _ids_for(record: logging.LogRecord) -> dict[str, str]:
    ids = dict(_ids.get())
    for field in ID_FIELDS:
        value = getattr(record, field, None)
        if value is not None:
            ids[field] = str(value)
    return ids


class JsonFormatter(logging.Formatter):
    """Formats a record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        created = datetime.fromtimestamp(record.created, tz=UTC)
        event: dict[str, object] = {
            "time": created.isoformat(timespec="milliseconds"),
            "severity": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            **_ids_for(record),
        }
        if record.exc_info:
            event["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            event["stack"] = self.formatStack(record.stack_info)
        return json.dumps(event, ensure_ascii=False, default=str)


def configure_logging(level: LogLevel = "INFO", stream: TextIO | None = None) -> None:
    """Send every log event to `stream` (stdout by default) as one JSON line.

    Replaces the root logger's handlers, so calling it again never duplicates events.
    """
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
