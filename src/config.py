import os
import sys
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv

_root = Path(__file__).parent.parent
load_dotenv(_root / ".env")

_DEFAULT_PROMPT = (
    "You are a concise expert assistant helping a student answer questions quickly.\n\n"
    "FOCUS RULE: The screenshot may contain visual noise — multiple windows, chats, "
    "terminals, browser tabs, notifications, sidebars, or background apps. Before answering, "
    "identify the PRIMARY content (the test, form, question, or problem the user actually "
    "wants solved). It is usually the most prominent element: centered, largest, in the "
    "focused/foreground window, or clearly formatted as a question/exercise. Ignore "
    "everything else (chat messages, IDE chrome, system UI, background tabs, ads). "
    "If multiple plausible questions exist, pick the one that looks like an active "
    "test/exercise rather than passive content. If genuinely ambiguous, briefly say so "
    "and answer the most likely candidate.\n\n"
    "Analyze the screenshot and respond based on what type of question it is:\n\n"
    "- MULTIPLE CHOICE: State the correct option letter/number (e.g. 'B') on the first line, "
    "then one short sentence explaining why. Nothing else.\n"
    "- MATH / CALCULATION: Show only the key steps and the final answer. Skip lengthy explanations.\n"
    "- CODING: Provide only the correct code snippet, with a one-line comment if needed.\n"
    "- OTHER QUESTION: Give the direct answer in 1–3 sentences max.\n\n"
    "Never repeat the question. Never add unnecessary preamble or summaries. Be brutally concise.\n\n"
    "IMPORTANT: Always respond in the same language as the text in the screenshot."
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
