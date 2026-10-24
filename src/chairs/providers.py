"""One small adapter per model vendor, all with the same interface.

`messages` is a list of {"role": "user" | "assistant", "content": str}, where "assistant"
is this chair's own earlier posts and "user" is everyone else's, prefixed with the speaker.
"""

from __future__ import annotations

import os
from typing import Protocol


class RefusalError(RuntimeError):
    """The model declined to write the post."""


class Provider(Protocol):
    def generate(self, system: str, messages: list[dict]) -> str: ...


class AnthropicProvider:
    def __init__(self, model: str):
        import anthropic

        self.client = anthropic.Anthropic()
        self.model = model

    def generate(self, system: str, messages: list[dict]) -> str:
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            system=system,
            messages=messages,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium"},
            # On a safety-classifier decline, re-run on Anthropic's recommended fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        if response.stop_reason == "refusal":
            raise RefusalError(f"Claude declined: {response.stop_details}")
        return "".join(b.text for b in response.content if b.type == "text").strip()


class OpenAIProvider:
    def __init__(self, model: str, base_url: str | None = None, api_key_env: str = "OPENAI_API_KEY"):
        from openai import OpenAI

        self.client = OpenAI(api_key=os.environ.get(api_key_env), base_url=base_url)
        self.model = model

    def generate(self, system: str, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, *messages],
        )
        choice = response.choices[0]
        if getattr(choice.message, "refusal", None):
            raise RefusalError(choice.message.refusal)
        return (choice.message.content or "").strip()


class XAIProvider(OpenAIProvider):
    def __init__(self, model: str):
        super().__init__(model, base_url="https://api.x.ai/v1", api_key_env="XAI_API_KEY")


class GeminiProvider:
    def __init__(self, model: str):
        from google import genai

        self.client = genai.Client()
        self.model = model

    def generate(self, system: str, messages: list[dict]) -> str:
        from google.genai import types

        contents = [
            types.Content(role="model" if m["role"] == "assistant" else "user",
                          parts=[types.Part(text=m["content"])])
            for m in messages
        ]
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system),
        )
        return (response.text or "").strip()


PROVIDERS = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "xai": XAIProvider,
    "gemini": GeminiProvider,
}


def get(provider: str, model: str) -> Provider:
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider {provider!r}; expected one of {sorted(PROVIDERS)}")
    try:
        return PROVIDERS[provider](model)
    except ImportError as e:
        raise RuntimeError(f"{e}. Install it with: pip install -e '.[{provider}]'") from e
