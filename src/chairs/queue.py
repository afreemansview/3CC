"""Draft state (pending → approved → posted, or rejected), rebuilt from the ledger."""

from __future__ import annotations

from .ledger import Ledger


def drafts(ledger: Ledger) -> dict[str, dict]:
    state: dict[str, dict] = {}
    for e in ledger.events():
        d = state.setdefault(e["draft_id"], {"id": e["draft_id"]})
        if e["event"] == "drafted":
            d.update(status="pending", persona=e["persona"], text=e["text"],
                     in_reply_to=e.get("in_reply_to"))
        elif e["event"] == "approved":
            d.update(status="approved", text=e["text"], edited=e.get("edited", False))
        elif e["event"] == "rejected":
            d.update(status="rejected", reason=e.get("reason"))
        elif e["event"] == "posted":
            d.update(status="posted", post_id=e.get("post_id"), dry_run=e.get("dry_run", False))
    return state


def get(ledger: Ledger, draft_id: str) -> dict:
    try:
        return drafts(ledger)[draft_id]
    except KeyError:
        raise KeyError(f"No draft {draft_id!r} in the ledger")
