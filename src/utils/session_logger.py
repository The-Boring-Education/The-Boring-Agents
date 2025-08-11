"""Lightweight session logger for agent workflows.

Writes JSONL logs to logs/sessions/<session_id>.log so Admin UI can stream/read.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _logs_root_dir() -> str:
    return os.path.join("logs", "sessions")


def get_log_file_path(session_id: str) -> str:
    """Return absolute path for a session log file.

    Args:
        session_id: Unique workflow session id
    """
    directory = _logs_root_dir()
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, f"{session_id}.log")


def append_log(session_id: str, event: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Append a single JSONL log entry for the session.

    Args:
        session_id: Unique workflow session id
        event: Short event label
        meta: Optional structured metadata for the event
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "meta": meta or {},
    }
    path = get_log_file_path(session_id)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_logs(session_id: str, limit: int = 200) -> List[Dict[str, Any]]:
    """Read recent logs for a session.

    Args:
        session_id: Unique workflow session id
        limit: Max number of lines to return (most recent last)
    """
    path = get_log_file_path(session_id)
    if not os.path.exists(path):
        return []

    # Efficiently read last N lines
    lines: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]

    results: List[Dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            results.append(json.loads(line))
        except json.JSONDecodeError:
            # Best effort: skip malformed lines
            continue
    return results

