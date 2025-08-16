"""Core logic for Illini Prompt Nurse prototype.

This module implements basic message filtering, crisis detection,
appointment recognition, and triage scoring. Functions are kept
simple and stateless so they can be unit tested.
"""
from __future__ import annotations

import re

# Keywords for simple heuristics
IRRELEVANT_PATTERNS = [
    re.compile(r"\b(?:cow|cows|moo)\b", re.IGNORECASE),
]

CRISIS_PATTERNS = [
    re.compile(r"\b(?:suicide|kill myself|don't want to live)\b", re.IGNORECASE),
]

APPOINTMENT_PATTERNS = [
    re.compile(r"\b(?:appointment|schedule|come in)\b", re.IGNORECASE),
]

URGENT_PATTERNS = [
    re.compile(r"\b(?:chest pain|difficulty breathing|shortness of breath)\b", re.IGNORECASE),
]


def is_message_relevant(message: str) -> bool:
    """Return True if the message appears relevant to health triage."""
    return not any(p.search(message) for p in IRRELEVANT_PATTERNS)


def contains_crisis_language(message: str) -> bool:
    """Detect potential mental health crisis language."""
    return any(p.search(message) for p in CRISIS_PATTERNS)


def recognize_appointment_intent(message: str) -> bool:
    """Identify whether the student seems to request an appointment."""
    return any(p.search(message) for p in APPOINTMENT_PATTERNS)


def triage_priority(message: str) -> str:
    """Return 'high' or 'routine' priority based on simple heuristics."""
    return "high" if any(p.search(message) for p in URGENT_PATTERNS) else "routine"


def disclaimer_for(message: str) -> str | None:
    """Return the legal disclaimer if message contains urgent symptoms."""
    if any(p.search(message) for p in URGENT_PATTERNS):
        return (
            "Illini Prompt Nurse is not legally allowed to give medical recommendations. "
            "You must always contact McKinley Health Center for confirmation."
        )
    return None


def sanitize_message(message: str, max_chars: int = 500) -> str:
    """Trim very long messages to save tokens."""
    message = message.strip()
    if len(message) > max_chars:
        return message[:max_chars] + "..."
    return message


def make_cache_key(student_id: str, message: str) -> str:
    """Create a cache key from student ID and message."""
    return f"{student_id}:{message.lower()}"

