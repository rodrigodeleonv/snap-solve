import os
import sys
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv

_root = Path(__file__).parent.parent
load_dotenv(_root / ".env")

_DEFAULT_PROMPT = (
    "You are an expert assistant. Analyze the screenshot carefully. "
    "If there is a question or multiple-choice problem visible, identify "
    "the correct answer and explain why clearly and concisely. "
    "Be direct and accurate."
)


class Config:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Auto-detect provider from which key is set; can be overridden explicitly.
    # Valid values: "claude", "openai", "groq"
    PROVIDER: str = os.getenv("SNAPSOLVE_PROVIDER", "").lower()

    # Model defaults per provider (overridable via SNAPSOLVE_MODEL)
    _MODEL_OVERRIDE: str = os.getenv("SNAPSOLVE_MODEL", "")
    _DEFAULT_MODELS: ClassVar[dict[str, str]] = {
        "claude": "claude-sonnet-4-6",
        "openai": "gpt-4o",
        "groq": "meta-llama/llama-4-scout-17b-16e-instruct",
    }

    HOTKEY: str = os.getenv("SNAPSOLVE_HOTKEY", "<ctrl>+<shift>+s")
    SYSTEM_PROMPT: str = os.getenv("SNAPSOLVE_SYSTEM_PROMPT", _DEFAULT_PROMPT)
    MAX_TOKENS: int = int(os.getenv("SNAPSOLVE_MAX_TOKENS", "1024"))

    def _resolve_provider(self) -> str:
        if self.PROVIDER in ("claude", "openai", "groq"):
            return self.PROVIDER
        # Auto-detect: preference order claude → openai → groq
        if self.ANTHROPIC_API_KEY:
            return "claude"
        if self.OPENAI_API_KEY:
            return "openai"
        if self.GROQ_API_KEY:
            return "groq"
        return ""

    @property
    def provider(self) -> str:
        return self._resolve_provider()

    @property
    def model(self) -> str:
        if self._MODEL_OVERRIDE:
            return self._MODEL_OVERRIDE
        return self._DEFAULT_MODELS.get(self.provider, "gpt-4o")

    def validate(self) -> None:
        p = self.provider
        _required = {
            "claude": ("ANTHROPIC_API_KEY", self.ANTHROPIC_API_KEY),
            "openai": ("OPENAI_API_KEY", self.OPENAI_API_KEY),
            "groq": ("GROQ_API_KEY", self.GROQ_API_KEY),
        }
        if p in _required:
            var, val = _required[p]
            if not val:
                print(
                    f"[SnapSolve] ERROR: SNAPSOLVE_PROVIDER={p} but {var} is not set.",
                    file=sys.stderr,
                )
                sys.exit(1)
        elif not p:
            print(
                "[SnapSolve] ERROR: No API key found.\n"
                "  Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY in your .env file.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"[SnapSolve] Provider: {p} | Model: {self.model}")


config = Config()
