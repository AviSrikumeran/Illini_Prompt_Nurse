import pytest

from core import (
    is_message_relevant,
    contains_crisis_language,
    recognize_appointment_intent,
    triage_priority,
    disclaimer_for,
    sanitize_message,
    make_cache_key,
    run_gpt,
    CACHE,
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


def test_run_gpt_irrelevant():
    result = run_gpt("s1", "I like cows")
    assert "not an appropriate" in result["response"]


def test_run_gpt_disclaimer_and_cache():
    CACHE.clear()
    first = run_gpt("s2", "I have chest pain")
    assert "Illini Prompt Nurse is not legally allowed" in first["response"]
    assert first["priority"] == "high"
    second = run_gpt("s2", "I have chest pain")
    assert second["cached"] is True

