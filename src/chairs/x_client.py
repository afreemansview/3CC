"""Posts to X through the official API. Dry run unless explicitly told otherwise."""

from __future__ import annotations

import os


def _creds(persona_id: str) -> dict:
    prefix = persona_id.upper()
    names = {
        "consumer_key": f"{prefix}_X_API_KEY",
        "consumer_secret": f"{prefix}_X_API_SECRET",
        "access_token": f"{prefix}_X_ACCESS_TOKEN",
        "access_token_secret": f"{prefix}_X_ACCESS_SECRET",
    }
    missing = [env for env in names.values() if not os.environ.get(env)]
    if missing:
        raise RuntimeError(f"Missing X credentials: {', '.join(missing)}")
    return {arg: os.environ[env] for arg, env in names.items()}


def post(persona_id: str, text: str, in_reply_to: str | None = None, live: bool = False) -> str:
    """Returns the new post's ID (or a placeholder on a dry run)."""
    if not live:
        print(f"[dry run] would post as {persona_id}"
              f"{f' in reply to {in_reply_to}' if in_reply_to else ''}:\n{text}")
        return "dry-run"
    import tweepy

    client = tweepy.Client(**_creds(persona_id))
    response = client.create_tweet(text=text, in_reply_to_tweet_id=in_reply_to)
    return str(response.data["id"])
