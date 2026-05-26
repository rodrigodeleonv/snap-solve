from typing import Protocol

from .config import config
from .screenshot import to_base64

# ── Contract ───────────────────────────────────────────────────────────────────


class Provider(Protocol):
    """Structural interface every AI provider must satisfy."""

    def call(self, png_bytes: bytes) -> str:
        """Send a screenshot and return the model's text response."""
        ...


# ── Concrete providers ─────────────────────────────────────────────────────────


class ClaudeProvider(Provider):
    def call(self, png_bytes: bytes) -> str:
        import anthropic
        from anthropic.types import TextBlock

        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=config.model,
            max_tokens=config.MAX_TOKENS,
            system=config.SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": to_base64(png_bytes),
                            },
                        },
                        {"type": "text", "text": config.USER_PROMPT},
                    ],
                }
            ],
        )
        block = message.content[0]
        if not isinstance(block, TextBlock):
            raise ValueError(f"Unexpected response block type from Claude: {type(block)}")
        return block.text


class OpenAIProvider(Provider):
    def call(self, png_bytes: bytes) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=config.model,
            max_tokens=config.MAX_TOKENS,
            messages=[
                {"role": "system", "content": config.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{to_base64(png_bytes)}"},
                        },
                        {"type": "text", "text": config.USER_PROMPT},
                    ],
                },
            ],
        )
        return response.choices[0].message.content or ""


class GroqProvider(Provider):
    def call(self, png_bytes: bytes) -> str:
        from groq import Groq

        client = Groq(api_key=config.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=config.model,
            max_tokens=config.MAX_TOKENS,
            messages=[
                {"role": "system", "content": config.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{to_base64(png_bytes)}"},
                        },
                        {"type": "text", "text": config.USER_PROMPT},
                    ],
                },
            ],
        )
        return response.choices[0].message.content or ""


# ── Registry + public entry point ──────────────────────────────────────────────

_REGISTRY: dict[str, type[Provider]] = {
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "groq": GroqProvider,
}


def analyze(png_bytes: bytes) -> str:
    """Send a screenshot to the configured AI provider and return the response."""
    cls = _REGISTRY.get(config.provider)
    if cls is None:
        raise ValueError(f"Unknown provider {config.provider!r}. Valid options: {list(_REGISTRY)}")
    return cls().call(png_bytes)
