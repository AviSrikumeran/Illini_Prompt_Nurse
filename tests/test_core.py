import pytest

from core import (
    is_message_relevant,
    contains_crisis_language,
    recognize_appointment_intent,
    triage_priority,
    disclaimer_for,
    sanitize_message,
    make_cache_key,
)


def test_irrelevant_message():
    assert not is_message_relevant("I like cows")


def test_crisis_detection():
    assert contains_crisis_language("I don't want to live anymore")


def test_appointment_intent():
    assert recognize_appointment_intent("Can I schedule an appointment?")


def test_triage_priority_high():
    assert triage_priority("I have chest pain") == "high"


def test_disclaimer_present():
    assert disclaimer_for("chest pain") is not None


def test_sanitize_message_trims_long_text():
    msg = "a" * 600
    assert sanitize_message(msg).endswith("...")


def test_cache_key_consistency():
    k1 = make_cache_key("123", "Hello")
    k2 = make_cache_key("123", "hello")
    assert k1 == k2

