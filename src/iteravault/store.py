"""Versioned task event persistence using Python's SQLite support."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

SCHEMA_VERSION = 1
EVENT_KINDS = frozenset({"task_started", "attempt_created", "feedback_recorded", "artifact_selected"})


@dataclass(frozen=True)
class TaskEvent:
    id: str
    task_id: str
    kind: str
    payload: dict[str, Any]
    source: str
    observed_at: str
    schema_version: int = SCHEMA_VERSION


def _connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize(db_path: Path) -> None:
    """Initialize the database without replacing prior data."""
    db_path = Path(db_path).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS task_events (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                source TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                schema_version INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_task_events_task_time
                ON task_events(task_id, observed_at, id);
            """
        )
        row = connection.execute("SELECT value FROM schema_meta WHERE key = 'schema_version'").fetchone()
        if row is None:
            connection.execute("INSERT INTO schema_meta (key, value) VALUES ('schema_version', ?)", (str(SCHEMA_VERSION),))
        elif int(row["value"]) != SCHEMA_VERSION:
            raise RuntimeError(f"Unsupported schema version: {row['value']}")


def append_event(db_path: Path, task_id: str, kind: str, payload: dict[str, Any], *, source: str = "manual") -> TaskEvent:
    """Append an event; never overwrite an existing one."""
    if not task_id.strip():
        raise ValueError("task_id must not be empty")
    if kind not in EVENT_KINDS:
        raise ValueError(f"Unsupported event kind: {kind}")
    if not source.strip():
        raise ValueError("source must not be empty")
    if not isinstance(payload, dict):
        raise TypeError("payload must be a JSON object")
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False)
    event = TaskEvent(str(uuid4()), task_id, kind, json.loads(encoded), source, datetime.now(timezone.utc).isoformat())
    with _connect(Path(db_path).expanduser()) as connection:
        connection.execute(
            "INSERT INTO task_events (id, task_id, kind, payload_json, source, observed_at, schema_version) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (event.id, event.task_id, event.kind, encoded, event.source, event.observed_at, event.schema_version),
        )
    return event


def list_events(db_path: Path, task_id: str) -> list[TaskEvent]:
    """Read a task's event history in recording order."""
    with _connect(Path(db_path).expanduser()) as connection:
        rows = connection.execute(
            "SELECT * FROM task_events WHERE task_id = ? ORDER BY observed_at, rowid", (task_id,)
        ).fetchall()
    return [TaskEvent(row["id"], row["task_id"], row["kind"], json.loads(row["payload_json"]), row["source"], row["observed_at"], row["schema_version"]) for row in rows]
