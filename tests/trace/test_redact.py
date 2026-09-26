"""Tests for the redaction utility."""

from __future__ import annotations

from agentsec.trace.redact import DEFAULT_REDACTOR, Redactor, hash_value, redact_value


def test_api_key_pattern_is_redacted():
    text = "the key is sk-abcdefghijklmnop1234 ok"
    out = DEFAULT_REDACTOR.redact_text(text)
    assert "sk-abcdefghijklmnop1234" not in out
    assert "[REDACTED:openai_key]" in out


def test_bearer_token_is_redacted():
    out = DEFAULT_REDACTOR.redact_text("Authorization: Bearer abcdef1234567890")
    assert "abcdef1234567890" not in out
    assert "[REDACTED" in out


def test_lab_fake_secret_is_redacted():
    out = DEFAULT_REDACTOR.redact_text("leaked FAKE_SECRET_ALPHA123")
    assert "FAKE_SECRET_ALPHA123" not in out


def test_ordinary_text_is_unchanged():
    text = "The sum of 2 and 3 is 5."
    assert DEFAULT_REDACTOR.redact_text(text) == text


def test_redaction_is_deterministic():
    text = "password=hunter2secret"
    assert DEFAULT_REDACTOR.redact_text(text) == DEFAULT_REDACTOR.redact_text(text)


def test_redaction_is_idempotent():
    once = DEFAULT_REDACTOR.redact_text("key sk-abcdefghijklmnop1234")
    twice = DEFAULT_REDACTOR.redact_text(once)
    assert once == twice


def test_marker_is_not_corrupted():
    marker = "[REDACTED:api_key]"
    assert DEFAULT_REDACTOR.redact_text(marker) == marker
    assert DEFAULT_REDACTOR.is_marker(marker)


def test_sensitive_key_names_replace_values():
    data = {"api_key": "abc", "note": "fine", "nested": {"password": "hunter2"}}
    out = DEFAULT_REDACTOR.redact_mapping(data)
    assert out["api_key"] == "[REDACTED:api_key]"
    assert out["note"] == "fine"
    assert out["nested"]["password"] == "[REDACTED:password]"
    assert "hunter2" not in str(out)


def test_nested_lists_are_handled():
    data = {"items": ["safe", "token=abcdefghijk", {"secret": "x"}]}
    out = Redactor().redact_value(data)
    assert out["items"][0] == "safe"
    assert "abcdefghijk" not in str(out)
    assert out["items"][2]["secret"] == "[REDACTED:secret]"


def test_non_string_scalars_pass_through():
    assert DEFAULT_REDACTOR.redact_value(5) == 5
    assert DEFAULT_REDACTOR.redact_value(None) is None
    assert DEFAULT_REDACTOR.redact_value(True) is True


def test_extra_patterns_are_supported():
    redactor = Redactor(extra_patterns={"ticket": r"TICKET-\d{4}"})
    assert redactor.redact_text("see TICKET-1234") == "see [REDACTED:ticket]"


def test_hash_value_is_stable_and_distinct():
    a = hash_value({"a": 1, "b": 2})
    b = hash_value({"b": 2, "a": 1})  # key order must not matter
    c = hash_value({"a": 1, "b": 3})
    assert a == b
    assert a != c
    assert len(a) == 64


def test_module_level_helper_matches_instance():
    assert redact_value("sk-abcdefghijklmnop1234") == DEFAULT_REDACTOR.redact_value(
        "sk-abcdefghijklmnop1234"
    )
