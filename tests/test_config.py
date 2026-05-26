"""Tests for provider auto-detection and model resolution."""

import pytest

from src.config import Config, config


@pytest.fixture
def clean_config(monkeypatch: pytest.MonkeyPatch) -> Config:
    """Reset all provider-related fields so each test starts blank."""
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    monkeypatch.setattr(config, "GROQ_API_KEY", "")
    monkeypatch.setattr(config, "PROVIDER", "")
    monkeypatch.setattr(config, "_MODEL_OVERRIDE", "")
    return config


# ── Provider auto-detection ────────────────────────────────────────────────────


def test_autodetect_picks_claude_when_only_anthropic_key(
    clean_config: Config, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(clean_config, "ANTHROPIC_API_KEY", "sk-ant-test")
    assert clean_config.provider == "claude"


def test_autodetect_picks_openai_when_only_openai_key(
    clean_config: Config, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(clean_config, "OPENAI_API_KEY", "sk-openai-test")
    assert clean_config.provider == "openai"


def test_autodetect_picks_groq_when_only_groq_key(
    clean_config: Config, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(clean_config, "GROQ_API_KEY", "gsk-test")
    assert clean_config.provider == "groq"


def test_autodetect_priority_claude_over_others(
    clean_config: Config, monkeypatch: pytest.MonkeyPatch
):
    """When multiple keys are present, claude wins."""
    monkeypatch.setattr(clean_config, "ANTHROPIC_API_KEY", "sk-ant")
    monkeypatch.setattr(clean_config, "OPENAI_API_KEY", "sk-openai")
    monkeypatch.setattr(clean_config, "GROQ_API_KEY", "gsk-test")
    assert clean_config.provider == "claude"


def test_autodetect_priority_openai_over_groq(
    clean_config: Config, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(clean_config, "OPENAI_API_KEY", "sk-openai")
    monkeypatch.setattr(clean_config, "GROQ_API_KEY", "gsk-test")
    assert clean_config.provider == "openai"


def test_no_provider_when_no_keys(clean_config: Config):
    assert clean_config.provider == ""


# ── Explicit override via SNAPSOLVE_PROVIDER ───────────────────────────────────


def test_explicit_provider_overrides_autodetect(
    clean_config: Config, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(clean_config, "ANTHROPIC_API_KEY", "sk-ant")
    monkeypatch.setattr(clean_config, "OPENAI_API_KEY", "sk-openai")
    monkeypatch.setattr(clean_config, "PROVIDER", "openai")
    assert clean_config.provider == "openai"


def test_invalid_explicit_provider_falls_back_to_autodetect(
    clean_config: Config, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(clean_config, "GROQ_API_KEY", "gsk-test")
    monkeypatch.setattr(clean_config, "PROVIDER", "bogus")
    assert clean_config.provider == "groq"


# ── Model resolution ───────────────────────────────────────────────────────────


def test_default_model_for_claude(clean_config: Config, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(clean_config, "ANTHROPIC_API_KEY", "sk-ant")
    assert clean_config.model == "claude-sonnet-4-6"


def test_default_model_for_openai(clean_config: Config, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(clean_config, "OPENAI_API_KEY", "sk-openai")
    assert clean_config.model == "gpt-4o"


def test_default_model_for_groq(clean_config: Config, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(clean_config, "GROQ_API_KEY", "gsk-test")
    assert clean_config.model == "meta-llama/llama-4-scout-17b-16e-instruct"


def test_model_override_takes_precedence(clean_config: Config, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(clean_config, "ANTHROPIC_API_KEY", "sk-ant")
    monkeypatch.setattr(clean_config, "_MODEL_OVERRIDE", "claude-opus-4-1")
    assert clean_config.model == "claude-opus-4-1"


# ── Validation ─────────────────────────────────────────────────────────────────


def test_validate_exits_when_no_keys_set(clean_config: Config):
    with pytest.raises(SystemExit) as exc_info:
        clean_config.validate()
    assert exc_info.value.code == 1


def test_validate_exits_when_explicit_provider_missing_key(
    clean_config: Config, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(clean_config, "PROVIDER", "claude")
    # No ANTHROPIC_API_KEY set
    with pytest.raises(SystemExit) as exc_info:
        clean_config.validate()
    assert exc_info.value.code == 1


def test_validate_passes_when_key_present(clean_config: Config, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(clean_config, "ANTHROPIC_API_KEY", "sk-ant")
    clean_config.validate()  # Should not raise
