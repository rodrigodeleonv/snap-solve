"""Tests for the provider registry and dispatch logic."""

import pytest
from pytest_mock import MockerFixture

from src import ai_client
from src.ai_client import (
    _REGISTRY,
    ClaudeProvider,
    GroqProvider,
    OpenAIProvider,
    analyze,
)

# ── Registry shape ─────────────────────────────────────────────────────────────


def test_registry_has_all_three_providers():
    assert set(_REGISTRY.keys()) == {"claude", "openai", "groq"}


def test_registry_maps_to_correct_classes():
    assert _REGISTRY["claude"] is ClaudeProvider
    assert _REGISTRY["openai"] is OpenAIProvider
    assert _REGISTRY["groq"] is GroqProvider


def test_all_providers_expose_call_method():
    """Structural check: every registered class has the Provider.call signature.

    Protocol is structural — isinstance() requires @runtime_checkable, which we
    intentionally avoid. Instead we verify the duck-typed contract directly.
    """
    for cls in _REGISTRY.values():
        instance = cls()
        assert hasattr(instance, "call")
        assert callable(instance.call)


# ── analyze() dispatch ─────────────────────────────────────────────────────────


def test_analyze_raises_on_unknown_provider(mocker: MockerFixture):
    mocker.patch.object(ai_client.config, "_resolve_provider", return_value="bogus")
    with pytest.raises(ValueError, match="Unknown provider 'bogus'"):
        analyze(b"fake-png")


def test_analyze_raises_on_empty_provider(mocker: MockerFixture):
    mocker.patch.object(ai_client.config, "_resolve_provider", return_value="")
    with pytest.raises(ValueError, match="Unknown provider"):
        analyze(b"fake-png")


def test_analyze_dispatches_to_claude(mocker: MockerFixture):
    mocker.patch.object(ai_client.config, "_resolve_provider", return_value="claude")
    mock_call = mocker.patch.object(ClaudeProvider, "call", return_value="claude-response")

    result = analyze(b"fake-png")

    assert result == "claude-response"
    mock_call.assert_called_once_with(b"fake-png")


def test_analyze_dispatches_to_openai(mocker: MockerFixture):
    mocker.patch.object(ai_client.config, "_resolve_provider", return_value="openai")
    mock_call = mocker.patch.object(OpenAIProvider, "call", return_value="openai-response")

    result = analyze(b"fake-png")

    assert result == "openai-response"
    mock_call.assert_called_once_with(b"fake-png")


def test_analyze_dispatches_to_groq(mocker: MockerFixture):
    mocker.patch.object(ai_client.config, "_resolve_provider", return_value="groq")
    mock_call = mocker.patch.object(GroqProvider, "call", return_value="groq-response")

    result = analyze(b"fake-png")

    assert result == "groq-response"
    mock_call.assert_called_once_with(b"fake-png")
