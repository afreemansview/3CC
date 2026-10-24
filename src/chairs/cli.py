"""`chairs` command line: draft, queue, approve, reject, post."""

from __future__ import annotations

import argparse
import sys

from . import disclosure, orchestrator, persona as personas, queue, x_client
from .ledger import Ledger

CONVENER = "lucianof_dc"


def cmd_draft(args, ledger: Ledger) -> None:
    chair = personas.load(args.persona)
    convener = personas.load(CONVENER)
    thread = [(convener.x_handle, args.say)]
    record = orchestrator.draft(chair, thread, ledger, counterpart=convener,
                                in_reply_to=args.in_reply_to)
    print(f"Draft {record['draft_id']} ({len(record['text'])} chars):\n\n{record['text']}")


def cmd_queue(args, ledger: Ledger) -> None:
    rows = [d for d in queue.drafts(ledger).values() if args.all or d["status"] in ("pending", "approved")]
    if not rows:
        print("Nothing in the queue.")
    for d in rows:
        print(f"[{d['id']}] {d['status']:<8} {d.get('persona', '?')}\n  {d.get('text', '').replace(chr(10), chr(10) + '  ')}\n")


def cmd_approve(args, ledger: Ledger) -> None:
    d = queue.get(ledger, args.id)
    if d["status"] != "pending":
        sys.exit(f"Draft {args.id} is {d['status']}, not pending")
    chair = personas.load(d["persona"])
    text = disclosure.finalize(chair, args.edit, edited=True) if args.edit else d["text"]
    ledger.append("approved", args.id, text=text, edited=bool(args.edit))
    print(f"Approved {args.id}:\n\n{text}")


def cmd_reject(args, ledger: Ledger) -> None:
    queue.get(ledger, args.id)
    ledger.append("rejected", args.id, reason=args.reason)
    print(f"Rejected {args.id}")


def cmd_post(args, ledger: Ledger) -> None:
    d = queue.get(ledger, args.id)
    if d["status"] != "approved":
        sys.exit(f"Draft {args.id} is {d['status']}; only approved drafts can be posted")
    post_id = x_client.post(d["persona"], d["text"], d.get("in_reply_to"), live=args.live)
    if args.live:
        ledger.append("posted", args.id, post_id=post_id)
        print(f"Posted {args.id} as {post_id}")


def cmd_x_login(args, ledger: Ledger) -> None:
    personas.load(args.persona)
    token, secret = x_client.login(args.persona)
    token_env, secret_env = x_client._token_names(args.persona)
    print(f"\nAdd these two lines to .env (keep them secret):\n\n{token_env}={token}\n{secret_env}={secret}")


def main(argv: list[str] | None = None) -> None:
    from dotenv import load_dotenv

    load_dotenv()
    p = argparse.ArgumentParser(prog="chairs", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("draft", help="have a chair draft a reply to @Lucianof_DC")
    s.add_argument("persona")
    s.add_argument("--say", required=True, help="what @Lucianof_DC said")
    s.add_argument("--in-reply-to", help="X post ID to reply to")
    s.set_defaults(fn=cmd_draft)

    s = sub.add_parser("queue", help="list drafts awaiting review or posting")
    s.add_argument("--all", action="store_true", help="include rejected and posted drafts")
    s.set_defaults(fn=cmd_queue)

    s = sub.add_parser("approve", help="human sign-off on a draft")
    s.add_argument("id")
    s.add_argument("--edit", help="replacement body text (the post is then marked as edited)")
    s.set_defaults(fn=cmd_approve)

    s = sub.add_parser("reject", help="discard a draft (it stays in the ledger)")
    s.add_argument("id")
    s.add_argument("--reason", default="")
    s.set_defaults(fn=cmd_reject)

    s = sub.add_parser("post", help="post an approved draft (dry run unless --live)")
    s.add_argument("id")
    s.add_argument("--live", action="store_true")
    s.set_defaults(fn=cmd_post)

    s = sub.add_parser("x-login", help="authorize the X app for a chair's account (one time)")
    s.add_argument("persona")
    s.set_defaults(fn=cmd_x_login)

    args = p.parse_args(argv)
    args.fn(args, Ledger())


if __name__ == "__main__":
    main()
