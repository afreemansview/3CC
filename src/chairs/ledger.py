"""Append-only public record of every draft, decision, and post."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import REPO_ROOT

LEDGER_PATH = REPO_ROOT / "ledger" / "events.jsonl"


class Ledger:
    def __init__(self, path: Path = LEDGER_PATH):
        self.path = path

    def append(self, event: str, draft_id: str, **data) -> dict:
        record = {"ts": datetime.now(timezone.utc).isoformat(), "event": event,
                  "draft_id": draft_id, **data}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def events(self) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
