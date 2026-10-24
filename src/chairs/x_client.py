"""Posts to X through the official API. Dry run unless explicitly told otherwise.

One developer app (X_API_KEY / X_API_SECRET) is shared by every chair. Each chair's account
authorizes that app once with `chairs x-login <persona>`, which yields that account's own
access token and secret (<PERSONA>_X_ACCESS_TOKEN / <PERSONA>_X_ACCESS_SECRET).
"""

from __future__ import annotations

import os


def _require(*names: str) -> dict[str, str]:
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise RuntimeError(f"Missing in .env: {', '.join(missing)}")
    return {n: os.environ[n] for n in names}


def _token_names(persona_id: str) -> tuple[str, str]:
    prefix = persona_id.upper()
    return f"{prefix}_X_ACCESS_TOKEN", f"{prefix}_X_ACCESS_SECRET"


def login(persona_id: str) -> tuple[str, str]:
    """Interactive PIN flow: sign in to X *as the chair's account* and authorize the app."""
    import tweepy

    app = _require("X_API_KEY", "X_API_SECRET")
    handler = tweepy.OAuth1UserHandler(app["X_API_KEY"], app["X_API_SECRET"], callback="oob")
    print("1. In a browser where you're logged in to X as this chair's account, open:\n\n"
          f"   {handler.get_authorization_url()}\n\n2. Click Authorize, then paste the PIN here.")
    return handler.get_access_token(input("PIN: ").strip())


def post(persona_id: str, text: str, in_reply_to: str | None = None, live: bool = False) -> str:
    """Returns the new post's ID (or a placeholder on a dry run)."""
    if not live:
        print(f"[dry run] would post as {persona_id}"
              f"{f' in reply to {in_reply_to}' if in_reply_to else ''}:\n{text}")
        return "dry-run"
    import tweepy

    token_env, secret_env = _token_names(persona_id)
    creds = _require("X_API_KEY", "X_API_SECRET", token_env, secret_env)
    client = tweepy.Client(consumer_key=creds["X_API_KEY"], consumer_secret=creds["X_API_SECRET"],
                           access_token=creds[token_env], access_token_secret=creds[secret_env])
    response = client.create_tweet(text=text, in_reply_to_tweet_id=in_reply_to)
    return str(response.data["id"])
