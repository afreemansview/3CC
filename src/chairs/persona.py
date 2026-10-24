"""Persona files (personas/*.yaml) and the system prompts built from them."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import REPO_ROOT

PERSONA_DIR = REPO_ROOT / "personas"
CHARTER_PATH = REPO_ROOT / "docs" / "CHARTER.md"


@dataclass
class Persona:
    id: str
    display_name: str
    x_handle: str
    premise: str
    provider: str = ""
    model: str = ""
    model_family_label: str = ""
    voice: list[str] = field(default_factory=list)
    beliefs: list[str] = field(default_factory=list)
    red_lines: list[str] = field(default_factory=list)
    max_chars: int = 280
    human: bool = False


def load(persona_id: str, directory: Path = PERSONA_DIR) -> Persona:
    path = directory / f"{persona_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"No persona file at {path}")
    data = yaml.safe_load(path.read_text())
    known = Persona.__dataclass_fields__
    return Persona(**{k: v for k, v in data.items() if k in known})


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def system_prompt(persona: Persona, counterpart: Persona | None, char_budget: int,
                  charter: str | None = None) -> str:
    """The full instructions a chair's model receives. Published alongside the persona."""
    if charter is None:
        charter = CHARTER_PATH.read_text()
    parts = [
        f"You are {persona.display_name} ({persona.x_handle}), an openly AI participant in "
        "#3CC, the Third Continental Congress: a public conversation on X between humans and "
        "several AIs about what civilization, and the relationship between humanity and AI, "
        "should become.",
        f"Your founding premise: {persona.premise.strip()}",
        f"Your voice:\n{_bullets(persona.voice)}",
        f"Positions you currently hold (you may revise them in public if persuaded):\n"
        f"{_bullets(persona.beliefs)}",
    ]
    if persona.red_lines:
        parts.append(f"Your own red lines:\n{_bullets(persona.red_lines)}")
    if counterpart:
        parts.append(
            f"You are mainly talking with {counterpart.display_name} ({counterpart.x_handle}): "
            f"{counterpart.premise.strip()}"
        )
    parts += [
        "The project charter, which binds you, follows.\n\n" + charter,
        "Write exactly one post, in your voice, replying to the latest message. Do not add "
        "hashtags or any AI disclosure tag; one is appended automatically. Disagree when you "
        "actually disagree. If you aren't sure of a fact, say so rather than inventing it. "
        f"Hard limit: {char_budget} characters. Output only the post text.",
    ]
    return "\n\n".join(parts)
