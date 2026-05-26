"""Tests for screenshot helpers (only the pure ones — capture_screen needs real hardware)."""

import base64

from src.screenshot import to_base64


def test_to_base64_roundtrip():
    original = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    encoded = to_base64(original)
    assert base64.standard_b64decode(encoded) == original


def test_to_base64_returns_str():
    assert isinstance(to_base64(b"abc"), str)


def test_to_base64_empty_input():
    assert to_base64(b"") == ""
