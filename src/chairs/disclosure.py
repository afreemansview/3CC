"""The disclosure tag is added in code so no model can drop or reword it."""

from __future__ import annotations

from .persona import Persona

EDITED_MARK = " ✎"


class TooLongError(ValueError):
    pass


def tag(persona: Persona, edited: bool = False) -> str:
    return f"\n🤖 AI · {persona.model_family_label} · human-reviewed{EDITED_MARK if edited else ''}"


def body_budget(persona: Persona) -> int:
    """Characters left for the post body once the longest form of the tag is added."""
    return persona.max_chars - len(tag(persona, edited=True))


def finalize(persona: Persona, body: str, edited: bool = False) -> str:
    text = body.strip() + tag(persona, edited)
    if len(text) > persona.max_chars:
        raise TooLongError(f"{len(text)} characters; limit is {persona.max_chars}")
    return text
