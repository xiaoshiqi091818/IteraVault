"""Minimal CLI for task event intake and inspection."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .store import EVENT_KINDS, append_event, initialize, list_events


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="iteravault")
    parser.add_argument("--db", type=Path, default=Path(os.environ.get("ITERAVAULT_DB", "data/iteravault.sqlite3")))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="create a local database")
    record = commands.add_parser("record", help="append a task event")
    record.add_argument("task_id")
    record.add_argument("kind", choices=sorted(EVENT_KINDS))
    record.add_argument("--payload", required=True, help="JSON object")
    record.add_argument("--source", default="manual")
    history = commands.add_parser("history", help="list events for a task")
    history.add_argument("task_id")
    args = parser.parse_args(argv)
    if args.command == "init":
        initialize(args.db)
        print(f"Initialized: {args.db}")
    elif args.command == "record":
        try:
            payload = json.loads(args.payload)
            initialize(args.db)
            event = append_event(args.db, args.task_id, args.kind, payload, source=args.source)
        except (ValueError, TypeError, RuntimeError) as exc:
            parser.error(str(exc))
        print(event.id)
    else:
        if not args.db.exists():
            parser.error("database does not exist; run 'iteravault init' first")
        for event in list_events(args.db, args.task_id):
            print(json.dumps(event.__dict__, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
