"""Turns a conversation into a reviewed, disclosed draft from one chair."""

from __future__ import annotations

import uuid

from . import disclosure, persona as personas, providers
from .ledger import Ledger
from .persona import Persona


def to_messages(chair: Persona, thread: list[tuple[str, str]]) -> list[dict]:
    """Convert (speaker_handle, text) pairs into alternating user/assistant messages."""
    messages: list[dict] = []
    for speaker, text in thread:
        if speaker == chair.x_handle:
            role, content = "assistant", text
        else:
            role, content = "user", f"{speaker}: {text}"
        if messages and messages[-1]["role"] == role:
            messages[-1]["content"] += "\n\n" + content
        else:
            messages.append({"role": role, "content": content})
    if not messages or messages[-1]["role"] != "user":
        raise ValueError("The thread must end with someone other than this chair speaking")
    return messages


def draft(chair: Persona, thread: list[tuple[str, str]], ledger: Ledger,
          counterpart: Persona | None = None, provider: providers.Provider | None = None,
          in_reply_to: str | None = None) -> dict:
    provider = provider or providers.get(chair.provider, chair.model)
    budget = disclosure.body_budget(chair)
    system = personas.system_prompt(chair, counterpart, budget)
    messages = to_messages(chair, thread)

    body = provider.generate(system, messages)
    if len(body) > budget:
        # One retry, asking the model to shorten its own words rather than us truncating them.
        retry = messages + [
            {"role": "assistant", "content": body},
            {"role": "user", "content": f"(Operator: that's {len(body)} characters; the limit "
                                        f"is {budget}. Rewrite it shorter, same meaning.)"},
        ]
        body = provider.generate(system, retry)
    text = disclosure.finalize(chair, body)

    return ledger.append(
        "drafted", uuid.uuid4().hex[:8], persona=chair.id, provider=chair.provider,
        model=chair.model, thread=thread, raw_output=body, text=text, in_reply_to=in_reply_to,
    )
